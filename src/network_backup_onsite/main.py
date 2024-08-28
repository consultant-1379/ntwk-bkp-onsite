#!/usr/bin/env python

##############################################################################
# COPYRIGHT Ericsson 2018
#
# The copyright to the computer program(s) herein is the property of
# Ericsson Inc. The programs may be used and/or copied only with written
# permission from Ericsson Inc. or in accordance with the terms and
# conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
##############################################################################

# For broad exception
# For too many arguments
# For snake_case comments (invalid-name)
# For unused arguments
# pylint: disable=W0703,R0913,C0103,W0613

"""Module for running network backup upload, download, list or retention."""

import argparse
import os
from subprocess import PIPE, Popen
import sys

from enum import Enum

from network_backup_onsite import __version__
from network_backup_onsite.exceptions import NotificationHandlerException
from network_backup_onsite.input_validators import SCRIPT_OBJECTS, validate_get_main_logger, \
    validate_log_level, validate_log_root_path, validate_nodes_backup_location, \
    validate_script_settings
from network_backup_onsite.logger import logging
from network_backup_onsite.node_backup_handler import NodeBackupHandler, \
    create_backup_folder_onsite
from network_backup_onsite.utils import LOG_ROOT_PATH_CLI, LOG_SUFFIX, get_home_dir

LOG_ROOT_PATH_HELP = "Provide a path to store the logs."
LOG_LEVEL_HELP = "Provide the log level. Options: [CRITICAL, ERROR, WARNING, INFO, DEBUG]."
BACKUP_DESTINATION_HELP = "Provide the destination of the backup."
USAGE_HELP = "Display detailed help."
NTWK_BKP_VERSION_HELP = "Show currently installed ntwk_bkp version."

SCRIPT_FILE = os.path.basename(__file__).split('.')[0]

CONF_FILE_NAME = 'config.cfg'

MAIN_LOG_FILE_NAME = "ntwk_bkp_onsite_{}.{}".format(SCRIPT_FILE, LOG_SUFFIX)
DEFAULT_LOG_ROOT_PATH = os.path.join(get_home_dir(), "network_device_backup_logs")

BKP_FOLDER_TEMPLATE = 'network_device_backup_'

EXIT_CODES = Enum('ExitCodes', 'SUCCESS, INVALID_INPUT, FAILED_BKP_CREATION, '
                               'FAILED_BKP_VALIDATION, FAILED_BKP_SEND')


def main():
    """
    Start the backup upload/download/list/retention processes according to the input.

    1. Validate input parameters.
    2. Read the configuration file and validate it.
    3. Check the connection with the nodes .
    4. Execute the backup creation and transferring to OMBS.

    :return: SUCCESS exit code in case of success or one of the error codes specified by ExitCodes
    in case of failure.
    """
    try:
        args = parse_arguments()
    except Exception as arg_parse_exp:
        show_ntwk_arg_error(arg_parse_exp.message)

    if args.usage:
        show_ntwk_bkp_usage()

    if args.version:
        show_ntwk_bkp_version()

    logger = validate_get_main_logger(args, MAIN_LOG_FILE_NAME)

    logger.log_info("Running ntwk_bkp_onsite")

    config_object_dict = execute_validation_input(logger)

    node_config_dict = config_object_dict[SCRIPT_OBJECTS.NODE_CONFIG_DICT.name]
    backup_config = config_object_dict[SCRIPT_OBJECTS.BACKUP_CONFIG.name]
    delay = config_object_dict[SCRIPT_OBJECTS.DELAY.name]
    ombs_config = config_object_dict[SCRIPT_OBJECTS.OMBS_CONFIG.name]
    notification_handler = config_object_dict[SCRIPT_OBJECTS.NOTIFICATION_HANDLER.name]

    backup_execution_result = execute_backup_creation_and_sending(node_config_dict, backup_config,
                                                                  delay, ombs_config,
                                                                  notification_handler, logger)

    if not backup_execution_result:
        return EXIT_CODES.FAILED_BKP_CREATION.value

    return EXIT_CODES.SUCCESS.value


def parse_arguments():
    """
    Parse input arguments.

    :return: parsed arguments.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(LOG_ROOT_PATH_CLI, nargs='?', default=DEFAULT_LOG_ROOT_PATH,
                        help=LOG_ROOT_PATH_HELP)
    parser.add_argument("--log_level", nargs='?', default=logging.INFO, help=LOG_LEVEL_HELP)
    parser.add_argument("--usage", action="store_true", help=USAGE_HELP)
    parser.add_argument("--version", action="store_true", help=NTWK_BKP_VERSION_HELP)

    args = parser.parse_args()

    args.log_root_path = validate_log_root_path(args.log_root_path, DEFAULT_LOG_ROOT_PATH)
    args.log_level = validate_log_level(args.log_level)

    return args


def execute_validation_input(logger):
    """
    Validate input parameters.

    :param logger: instance of Custom Logger.
    :return: script_objects.
    """
    script_objects = {}
    try:
        script_objects = validate_script_settings(CONF_FILE_NAME, script_objects, logger)

        validate_nodes_backup_location(CONF_FILE_NAME, script_objects, logger)

    except Exception as validation_exception:
        logger.log_error_exit(validation_exception.message, EXIT_CODES.FAILED_BKP_VALIDATION.value)

    return script_objects


def show_ntwk_bkp_usage():
    """ Display this usage help message whenever the script is run with '--usage' argument."""
    print """
        Usage of: '{}'

        This message is displayed when script is run with '--usage' argument.
        ============================================================================================
                                          Overview:
        ============================================================================================
        This script is for automating the process of onsite backup creation for network configs.
        The genie-bur network device backup requirements are defined under Jira issue NMAAS-1812:
        
        It basically does the following :

        1. Creates a backup of a nodes, specified in the configuration file
        2. Send created backup to OMBS
        
        ============================================================================================
                                    Script Exit Codes:
        ============================================================================================

        The following error codes can be raised in case of other failures during the process:

        INVALID_INPUT (2): Error while validating input arguments or configuration file.
        FAILED_BKP_CREATION (3): Error while creating backup.
        FAILED_BKP_VALIDATION (4): Error while validating backup file.
        FAILED_BKP_SEND (5): Error while sending backup to OMBS.

        ============================================================================================
                                        Configuration File ({}):
        ============================================================================================

        The script depends on a configuration file '{}' for all operations.
        The operations are: Upload, Download, List, Retention.

        --------------------------------------------------------------------------------------------
        It must contain the following sections:

        [SUPPORT_CONTACT]
        EMAIL_TO       Email address to send failure notifications.
        EMAIL_URL      URL of the email service.

        [NODE]
        HOSTNAME                          name of the host node
        IP                                ip of the node
        TYPE                              type of a node
        EQ_PROMPT                         prompt used in a node's OS
        USERNAME                          account username on the node
        PASSWORD                          account password on the node
        
        
        [OFFSITE_CONN]
        IP              remote ip address.
        USER            server user.
        BKP_PATH        remote root path where the backups will be placed.
        BKP_DIR         remote folder name where the backups will be stored. This folder will be
                        created in the BKP_PATH if it does not exist.
        BKP_TEMP_FOLDER local temporary folder to store files during the upload process before
                        transferring.
                        
        [BACKUP_CONFIG]
        PATH               path to the folder where the backup is stored
        BUFFER_SIZE        size of the buffer (needed for re4ading the config of the nodes)
        MIN_BACKUP_SIZE    minimal size of a backup eligible for sending to OMBS

        For example:

        [SUPPORT_CONTACT]
        EMAIL_TO=fo-enmaas@ericsson.com
        EMAIL_URL=https://172.31.2.5/v1/emailservice/send

        [GNUPG]
        GPG_USER_NAME=backup
        GPG_USER_EMAIL=backup@root.com

        [TEST_SWITCH]
        HOSTNAME=Connectivity_Switch_Test
        IP=10.0.2.1
        TYPE=connectivitySwitch
        EQ_PROMPT=EXOS-VM
        USERNAME=admin
        PASSWORD=qwerty123

        [BACKUP_CONFIG]
        PATH=/home/vagrant/Documents/BACKUPS_NTWK/backups/
        BUFFER_SIZE=100MB
        MIN_BACKUP_SIZE=5B
        
        [OMBS_CONFIG]
        IP=10.0.2.4
        USERNAME=vagrant
        DIR=/home/vagrant/backups
        
        [DELAY]
        BKP_MAX_DELAY=2s

        Note: Path variables should not contain quotes.

        ============================================================================================
        ============================================================================================
        """.format(SCRIPT_FILE, CONF_FILE_NAME, CONF_FILE_NAME)

    sys.exit(EXIT_CODES.SUCCESS.value)


def show_ntwk_bkp_version():
    """
    Display currently installed ntwk_bkp_onsite version, whenever the script is run with
    '--version' argument.

    :param exit_code: exit code to quit this application with after running this method.
    """
    print "ntwk_bkp_onsite version: {}".format(__version__)

    sys.exit(EXIT_CODES.SUCCESS.value)


def validate_backup_file_onsite(backup_config, backup_file, logger):
    """
    Check the size of a file.

    :param backup_config: instance on BackupConfig class.
    :param backup_file: file to be validated.
    :param logger: instance of CustomLogger.
    :return: True if success, else False.
    """
    if os.path.getsize(backup_file) > backup_config.min_backup_size:
        logger.info("File: {} is validated".format(backup_file))
    else:
        logger.error("There was a problem with {}! It's size is smaller than expected!\n"
                     .format(backup_file))
        return False
    return True


def validate_backup_folder_and_files_onsite(number_nodes, backup_config, folder_path, logger):
    """
    Checks the number of files in the folder. In case it matches the number of nodes and validates
    files.

    :param number_nodes: number of nodes in config file.
    :param backup_config: instance of BackupConfig.
    :param folder_path: path to a backup.
    :param logger: instance of CustomLogger.
    :return: True if success, else False.
    """
    files = [backup_file for backup_file in os.listdir(folder_path) if os.path.isfile(
        os.path.join(folder_path, backup_file))]

    if len(files) == number_nodes:
        logger.info("Backup folder {} has {} node backup files specified in config file"
                    .format(folder_path, number_nodes))
    else:
        logger.error("Backup folder {} does not contain all {} node backup files specified in "
                     "config file".format(folder_path, number_nodes))
        return False

    for backup_file in files:
        validation_result = validate_backup_file_onsite(backup_config,
                                                        os.path.join(folder_path, backup_file),
                                                        logger)
        if not validation_result:
            return False

    return True


def send_backup_to_ombs(bkp_dir, ombs_config, logger):
    """
    Send the folder with node backups to OMBS.

    :param bkp_dir: folder to be sent.
    :param ombs_config: instance of OMBSConfig.
    :param logger: instance of CustomLogger.
    :return: True in case of success, False otherwise.
    """
    try:
        command = "scp -r -i {} {} {}:{}".format(ombs_config.key_path, bkp_dir, ombs_config.host, ombs_config.dir)
        process = Popen(command.split(), stdout=PIPE)
        _, error = process.communicate()
        if error:
            error_msg = "Error occurred while sending the file: {} to OMBS server.".format(bkp_dir)
            logger.error(error_msg)
            raise Exception(error_msg)
        return True

    except Exception as send_exception:
        raise Exception(send_exception.message)


def execute_backup_creation_and_sending(node_config_dict, backup_config, delay, ombs_config,
                                        notification_handler, logger):
    """
    Run backup creation and transferring to OMBS.

    :param node_config_dict: list of node configurations.
    :param backup_config: backup configuration.
    :param delay: max number of seconds to wait.
    :param ombs_config: OMBS configuration.
    :param notification_handler: instance of Notification Handler.
    :param logger: instance of Custom Logger.
    :return: Exit code in case of failure.
    """
    try:
        bkp_folder_path = create_backup_folder_onsite(BKP_FOLDER_TEMPLATE, backup_config.path,
                                                      logger)

        for node_config in node_config_dict.values():
            get_sw_config = NodeBackupHandler(node_config, backup_config, delay, logger)
            get_sw_config.create_node_backup(bkp_folder_path)

        validation_result = validate_backup_folder_and_files_onsite(len(node_config_dict),
                                                                    backup_config,
                                                                    bkp_folder_path, logger)

        if not validation_result:
            error_list = ["Backup {} will not be sent to OMBS".format(bkp_folder_path)]
            logger.error(error_list)
            report_error(notification_handler, logger, error_list,
                         EXIT_CODES.FAILED_BKP_VALIDATION.value, "")
            return False

        logger.info("Backup folder {} is valid and can be sent to OMBS".format(bkp_folder_path))
        send_result = send_backup_to_ombs(bkp_folder_path, ombs_config, logger)
        if send_result:
            logger.log_info("Backup {} was successfully sent to OMBS".format(bkp_folder_path))

        success_list = ["Onsite was successfully created and sent to OMBS"]
        report_success(notification_handler, logger, success_list, "")

    except Exception as bkp_creation_exception:
        error_list = ["Backup could not be created. Cause: {}".format(bkp_creation_exception)]
        report_error(notification_handler, logger, error_list,
                     EXIT_CODES.FAILED_BKP_CREATION.value, "")
        return False

    return True


def report_success(notification_handler, logger, success_list, sender):
    """
    In case of success of backup creation, log the returned error, send email and exit.

    :param notification_handler: object that process the e-mail sending.
    :param logger: logger object.
    :param success_list: list of success messages.
    :param sender: deployment label that the operation was triggered for.
    :return: true if success.
    """
    try:
        report_title = "Network devices backup creation is finished"
        if sender is None or not sender.strip():
            sender = "network_bkp_onsite"

        notification_handler.send_success_email(sender, report_title, success_list)

    except NotificationHandlerException as notification_exp:
        logger.error(notification_exp.message)

    return True


def report_error(notification_handler, logger, error_list, error_code, sender, exit_script=False):
    """
    In case of error during backup creation, log the returned error, send email and exit.

    :param notification_handler: object that process the e-mail sending.
    :param logger: logger object.
    :param error_list: raised error message.
    :param error_code: error code.
    :param sender: deployment label that the operation was triggered for.
    :param exit_script: if the report should finish the script and exit the execution.
    :return: true if success.
    """
    try:
        subject = "Error executing onsite backup creation"

        if sender is None or not sender.strip():
            sender = "ntwk_bkp_onsite"
        notification_handler.send_error_email(sender, subject, error_list, error_code)

    except NotificationHandlerException as notification_exp:
        logger.error(notification_exp.message)

    if exit_script:
        logger.log_error_exit("Onsite Backup Creation finished.", error_code)

    return True


def show_ntwk_arg_error(error_message=""):
    """Display an error message when the argument list provided cannot be validated."""
    print "Provided arguments are invalid due to: {}\n\nRun --usage option for help.".format(
        error_message)

    sys.exit(EXIT_CODES.INVALID_INPUT.value)


if __name__ == '__main__':
    sys.exit(main())

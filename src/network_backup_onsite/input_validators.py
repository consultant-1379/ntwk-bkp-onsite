##############################################################################
# COPYRIGHT Ericsson 2018
#
# The copyright to the computer program(s) herein is the property of
# Ericsson Inc. The programs may be used and/or copied only with written
# permission from Ericsson Inc. or in accordance with the terms and
# conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
##############################################################################

# For snake_case comments (invalid-name)
# For broad exception
# For too many return statements
# pylint: disable=C0103,W0703,R0911

"""Module to handle all kinds of input validations prior to core processing."""

import logging
import os

from enum import Enum

from network_backup_onsite.backup_settings import ScriptSettings
from network_backup_onsite.exceptions import BackupSettingsException
from network_backup_onsite.logger import CustomLogger
from network_backup_onsite.utils import LOG_SUFFIX, create_path, is_host_accessible, is_valid_ip

SCRIPT_OBJECTS = Enum('SCRIPT_OBJECTS',
                      'NOTIFICATION_HANDLER, NODE_CONFIG_DICT, BACKUP_CONFIG, DELAY, OMBS_CONFIG')


def validate_get_main_logger(console_input_args, main_script_file_name):
    """
    Validate and get the main logger object, which is created based on the selected operation.

    :param console_input_args: arguments passed to the console.
    :param main_script_file_name: name of the main script.
    :return: custom logger object.
    :raise Exception: if logger object was not created.
    """
    try:
        main_log_file_name = "network_device_backup_create.{}".format(LOG_SUFFIX)

        return CustomLogger(main_script_file_name, console_input_args.log_root_path,
                            main_log_file_name, console_input_args.log_level)

    except Exception as exp:
        logger = CustomLogger(main_script_file_name, "")
        logger.log_error_exit("Error creating the logger object: {}.".format(exp))


def validate_log_root_path(log_root_path, default_log_root_path):
    """
    Validate the informed log root path.

    Try to create this path if it does not exist.

    Raise an exception if an error occurs.

    :param log_root_path: log root path to be validated.
    :param default_log_root_path: default log value.
    :return: validated log root path.
    :raise Exception: if a path was not created.
    """
    if log_root_path is None or not log_root_path.strip():
        log_root_path = default_log_root_path

    if not create_path(log_root_path):
        raise Exception("Error creating log root path '{}'.".format(log_root_path))

    return log_root_path


def validate_log_level(log_level):
    """
    Validate the informed log level. Sets to INFO when the informed value is invalid.

    :param log_level: log level.
    :return: validated log level.
    """
    if log_level in (logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG):
        return log_level

    log_level = str(log_level)

    if str(log_level).lower() == "critical":
        log_level = logging.CRITICAL
    elif str(log_level).lower() == "error":
        log_level = logging.ERROR
    elif str(log_level).lower() == "warning":
        log_level = logging.WARNING
    elif str(log_level).lower() == "info":
        log_level = logging.INFO
    elif str(log_level).lower() == "debug":
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    return log_level


def validate_nodes_backup_location(config_file_name, script_objects, logger):
    """
    Validate nodes and backup configs.

    :param config_file_name: BUR configuration file name.
    :param script_objects: dictionary of validated ScriptSettings objects.
    :param logger: logger object.
    :return: True if the validation was successful.
    :raise Exception: if the validation fails.
    """
    node_config_dict = script_objects[SCRIPT_OBJECTS.NODE_CONFIG_DICT.name]
    backup_config = script_objects[SCRIPT_OBJECTS.BACKUP_CONFIG.name]

    validation_error_list = []

    validate_nodes(node_config_dict, config_file_name, validation_error_list)
    validate_backup_location(backup_config, validation_error_list)

    if validation_error_list:
        raise Exception(validation_error_list)
    else:
        logger.log_info("Nodes and backup validation passed.")

    return True


def validate_nodes(node_config_dict, config_file_name, validation_error_list=None):
    """
    Validate nodes config.

    :param node_config_dict: list of nodes specified in config file.
    :param config_file_name: name of a config file.
    :param validation_error_list: list of errors.
    :return: True if nodes are validated, False otherwise.
    """
    if validation_error_list is None:
        validation_error_list = []

    if not node_config_dict.keys():
        validation_error_list.append("No nodes defined in the configuration file '{}'. "
                                     "Nothing to do.".format(config_file_name))

    for node_key in node_config_dict.keys():
        node_config = node_config_dict[node_key]

        if not node_config.hostname.strip():
            validation_error_list.append("Node parameters not defined in the configuration file"
                                         "'{}' for {}. Nothing to do.".format(config_file_name,
                                                                              node_key))

        if not node_config.ip.strip():
            validation_error_list.append("Node parameter 'IP' is empty for {}".format(
                node_config.hostname))

        if not node_config.type.strip():
            validation_error_list.append("Node parameter 'TYPE' is empty for {}".format(
                node_config.hostname))

        if not node_config.eq_prompt.strip():
            validation_error_list.append("Node parameter 'EQ_PROMPT' is empty for {}".format(
                node_config.hostname))

        if not node_config.username.strip():
            validation_error_list.append("Node parameter 'USERNAME' is empty for {}".format(
                node_config.hostname))

        if not node_config.password.strip():
            validation_error_list.append("Node parameter 'PASSWORD' is empty for {}".format(
                node_config.hostname))

        if not is_valid_ip(node_config.ip):
            validation_error_list.append("Informed IP {} for node {} is not valid".format(
                node_config.ip, node_config.hostname))

        if not is_host_accessible(node_config.ip):
            validation_error_list.append("Node {} with credentials {} is not accessible"
                                         .format(node_config.hostname, node_config.ip))

    if validation_error_list:
        return False

    return True


def validate_backup_location(backup_config, validation_error_list=None):
    """
    Validate if specified backup path exists.

    :param backup_config: Backup Config object.
    :param validation_error_list: list of errors.
    """
    if validation_error_list is None:
        validation_error_list = []

        if not os.path.exists(backup_config.path):
            validation_error_list.append("Informed path for backup storage does not exist: '{}'."
                                         .format(backup_config.path))
            return False
    return True


def validate_script_settings(config_file_name, script_objects, logger):
    """
    Validate the config_file parsing and the objects created from it.

    :param config_file_name: BUR configuration file name.
    :param logger: logger object.
    :param script_objects: ScriptSetting objects.
    :return: ScriptSetting objects validated.
    :raise Exception: if ScriptSettings object is invalid.
    """
    script_settings = ScriptSettings(config_file_name, logger)

    try:
        script_objects[SCRIPT_OBJECTS.NOTIFICATION_HANDLER.name] = \
            script_settings.get_notification_handler()

        script_objects[SCRIPT_OBJECTS.NODE_CONFIG_DICT.name] = \
            script_settings.get_node_config_dict()

        script_objects[SCRIPT_OBJECTS.BACKUP_CONFIG.name] = \
            script_settings.get_backup_config()

        script_objects[SCRIPT_OBJECTS.DELAY.name] = \
            script_settings.get_delay_config()

        script_objects[SCRIPT_OBJECTS.OMBS_CONFIG.name] = \
            script_settings.get_ombs_config()

    except BackupSettingsException as exception:
        raise Exception("Error validating ScriptSettings object due to: {}."
                        .format(str(exception)))

    return script_objects

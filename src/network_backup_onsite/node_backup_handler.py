#!/usr/bin/env python3

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
# For too many statements
# For too few public methods
# For too broad exception
# pylint: disable=C0103,R0915,R0903,W0703

"""Module to take care of onsite backup creation and transfer."""

import datetime
import os
import time

import pexpect

from network_backup_onsite.logger import CustomLogger
from network_backup_onsite.utils import create_path, to_seconds

SCRIPT_FILE = os.path.basename(__file__).split('.')[0]
TIME_FORMAT = "%Y%m%d"
SEPARATOR = "-----------------------------------------------------------------------------------\n"
TIME_OUT_1 = 120
TIME_OUT_2 = 240


def create_backup_folder_onsite(template, path, logger):
    """
    Create a folder on the onsite with a specific name (template_date).

    :param template: folder name format.
    :param path: folder location.
    :param logger: instance of CustomLogger.
    :return: path to the created folder.
    """
    now = datetime.datetime.now()
    bkp_folder_name = template + now.strftime(TIME_FORMAT)
    bkp_folder_path = os.path.join(path, bkp_folder_name)

    if not os.path.exists(bkp_folder_path):
        logger.info("Creating the directory '{}'".format(bkp_folder_path))
        if not create_path(bkp_folder_path):
            raise Exception("Failed to create backup folder {} onsite.".format(bkp_folder_path))

    return bkp_folder_path


def write_to_file(file_name, messages):
    """
    Write message to file.

    :param file_name: name of the file to be updated.
    :param message: message to be added.
    """
    f = open(file_name, "a+")
    for message in messages:
        f.write(message)
    f.close()


class NodeBackupHandler:
    """Class for creating a backup for a node."""

    def __init__(self, node_config, backup_config, delay_config, logger):
        """
        Method to initiate the class.

        :param node_config: instance of NodeConfig class.
        :param backup_config: instance of BackupConfig class.
        :param delay_config: instance of DelayConfig class.
        :param logger: instance of CustomLogger class.
        """
        self.node_config = node_config
        self.backup_config = backup_config
        self.delay_config = delay_config

        logger_script_reference = "{}_{}".format(SCRIPT_FILE, "network_device_backup")

        self.logger = CustomLogger(logger_script_reference, logger.log_root_path,
                                   logger.log_file_name, logger.log_level)

    def create_node_backup(self, bkp_folder_path):
        """
        Creates a backup for a node an keeps it as a file.

        :param bkp_folder_path: path to the folder to store backup.
        """
        now = datetime.datetime.now()
        file_name = self.node_config.hostname.lower() + "-backup-" + now.strftime(TIME_FORMAT)
        remote_host = self.node_config.host

        # Creating a file
        backup_file_location = os.path.join(bkp_folder_path, file_name)

        messages = []

        try:
            backup_file = open(backup_file_location, "w+")
            backup_file.close()
        except Exception as file_exception:
            self.logger.error("Backup file {} was not created due to {}.")\
                .format(file_name, file_exception)

        messages.append(SEPARATOR)
        messages.append("Equipment type: {} -> {} with IP: {}\n"
                        .format(self.node_config.type, self.node_config.hostname,
                                self.node_config.ip))
        messages.append(SEPARATOR)

        # Start spawning
        try:
            child = pexpect.spawn("ssh {}".format(remote_host), timeout=TIME_OUT_1,
                                  maxread=self.backup_config.buffer_size)

        except pexpect.exceptions.TIMEOUT:
            error_msg = "Connection timed out. Cannot connect to node: {}!"\
                .format(self.node_config.hostname)
            messages.append(error_msg)
            raise Exception(error_msg)

        child.expect("assword:")
        try:
            child.sendline(self.node_config.password)

        except pexpect.exceptions.TIMEOUT:
            raise Exception("Can't establish connection to {}. Check username and password"
                            .format(self.node_config.hostname))

        self.logger.info("Connected to {}".format(self.node_config.hostname))

        # Check node type as commands are different
        if str(self.node_config.type) == "srx":
            child.expect(self.node_config.eq_prompt, timeout=TIME_OUT_2)
            child.sendline("show config | display set | no-more")

            time.sleep(to_seconds(self.delay_config.max_delay))

        # For connectivity switch
        elif str(self.node_config.type) == "connectivitySwitch":
            child.expect(self.node_config.eq_prompt, timeout=TIME_OUT_2)
            child.sendline("disable clipaging")

            child.expect('#')
            child.sendline("show configuration")

            time.sleep(to_seconds(self.delay_config.max_delay))

        else:
            messages.append("Equipment not supported!")
            write_to_file(backup_file_location, messages)
            return

        if str(self.node_config.type) == "srx":
            child.expect('set')
        else:
            child.expect('#')
        messages.append(child.buffer)

        write_to_file(backup_file_location, messages)
        self.logger.log_info("Created backup file for {}".format(self.node_config.hostname))
        child.send("exit")
        self.logger.info("Closed the connection for {}".format(self.node_config.hostname))

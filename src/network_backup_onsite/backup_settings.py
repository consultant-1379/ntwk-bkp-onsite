##############################################################################
# COPYRIGHT Ericsson 2018
#
# The copyright to the computer program(s) herein is the property of
# Ericsson Inc. The programs may be used and/or copied only with written
# permission from Ericsson Inc. or in accordance with the terms and
# conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
##############################################################################

# For too many attributes comments
# For snake_case comments (invalid-name)
# For too many arguments comments
# pylint: disable=R0902,C0103,R0913

"""Module for processing config.cfg file."""

from ConfigParser import ConfigParser, MissingSectionHeaderError, NoOptionError, NoSectionError, \
    ParsingError
import os

from network_backup_onsite.exceptions import BackupSettingsException, ExceptionCodes
from network_backup_onsite.logger import CustomLogger
from network_backup_onsite.notification_handler import NotificationHandler
from network_backup_onsite.utils import get_home_dir, to_bytes

SCRIPT_FILE = os.path.basename(__file__).split('.')[0]

SYSTEM_CONFIG_FILE_ROOT_PATH = os.path.join(get_home_dir(), "network_backup_offsite", "config")
DEFAULT_CONFIG_FILE_ROOT_PATH = os.path.join(os.path.dirname(__file__), 'config')


class SupportInfo:
    """Class used to hold parsed information from config.cfg about support."""

    def __init__(self, email, server):
        """
        Initialize Support Info object.

        :param email: support email info.
        :param server: email server.
        """
        self.email = email
        self.server = server

    def __str__(self):
        """Represent Support Info object as string."""
        return "({}, {})".format(self.email, self.server)

    def __repr__(self):
        """Represent Support Info object."""
        return self.__str__()


class NodeConfig:
    """Class used to hold parsed information from config.cfg about nodes."""

    def __init__(self, hostname, ip, node_type, eq_prompt, username, password):
        """
        Initialize Node Config object.

        :param hostname: name of the host.
        :param ip: ip address of a node.
        :param node_type: type of a node.
        :param eq_prompt: prompt in node's OS system.
        :param username: node account user name.
        :param password: node account password.
        """
        self.hostname = hostname
        self.ip = ip
        self.type = node_type
        self.eq_prompt = eq_prompt
        self.username = username
        self.password = password
        self.host = username + '@' + ip

    def __str__(self):
        """Represent Node Config object as string."""
        return "({}, {}, {}, {}, {}, {})".format(self.hostname, self.ip, self.type,
                                                 self.eq_prompt, self.username, self.password)

    def __repr__(self):
        """Represent Node Config object."""
        return self.__str__()


class BackupConfig:
    """Class used to hold parsed information from config.cfg about backup storage and properties."""

    def __init__(self, path, buffer_size, min_backup_size):
        """
        Initialize Backup Config object.

        :param path: path.
        :param buffer_size.
        :param min_backup_size.
        """
        self.path = path
        self.buffer_size = buffer_size
        self.min_backup_size = min_backup_size

    def __str__(self):
        """Represent Backup Config object as string."""
        return "({}, {}, {})".format(self.path, self.buffer_size, self.min_backup_size)

    def __repr__(self):
        """Represent Backup Config object."""
        return self.__str__()


class OMBSConfig:
    """Class used to hold parsed information from config.cfg about OMBS."""

    def __init__(self, ip, username, bkp_dir, key_path):
        """
        Initialize OMBS Config object.

        :param ip: OMBS ip.
        :param username: OMBS username.
        :param bkp_dir: folder to store backups on OMBS.
        """
        self.ip = ip
        self.username = username
        self.dir = bkp_dir
        self.host = username + "@" + ip
        self.key_path = key_path

    def __str__(self):
        """Represent OMBS Config object as string."""
        return "({}, {}, {})".format(self.ip, self.username, self.dir)

    def __repr__(self):
        """Represent OMBS Config object."""
        return self.__str__()


class DelayConfig:
    """"Class used to hold parsed information from config.cfg about delay."""

    def __init__(self, max_delay):
        """
        Initialize Delay Config object.

        :param max_delay: max time of delay.
        """
        self.max_delay = max_delay

    def __str__(self):
        """Represent Delay Config object as string."""
        return "({})".format(self.max_delay)

    def __repr__(self):
        """Represent Delay Config object."""
        return self.__str__()


class ScriptSettings:
    """
    Class used to hold and information from the configuration file config.cfg.

    Configuration file will be checked first in $USER_HOME/network_backup_onsite/config/config.cfg
    and then at the directory "config" in the same level as the script.
    """

    def __init__(self, config_file_name, logger):
        """
        Initialize Script Settings object.

        :param config_file_name: name of the configuration file.
        :param logger: logger object.
        """
        self.config_file_name = config_file_name

        self.config_file_path = self._get_config_file_path()

        self.logger = CustomLogger(SCRIPT_FILE, logger.log_root_path, logger.log_file_name,
                                   logger.log_level)

        self.config = self._get_config_details()

    def _get_config_file_path(self):
        """
        Verify the path to config file.

        :return: config file pathname.
        """
        config_root_path = SYSTEM_CONFIG_FILE_ROOT_PATH
        if not os.access(config_root_path, os.R_OK):
            config_root_path = DEFAULT_CONFIG_FILE_ROOT_PATH

        return os.path.join(config_root_path, self.config_file_name)

    def _get_config_details(self):
        """
        Read, validate the configuration file and create the main objects used by the system.

        Errors that occur during this process are appended to the validation error list.

        :return: a dictionary with the following objects: notification handler, backup_config,
        ombs_config, node_config_dict, delay_config if success; an empty dictionary otherwise.
        """
        if not os.access(self.config_file_path, os.R_OK):
            raise BackupSettingsException("Configuration file is not accessible '{}'"
                                          .format(self.config_file_path),
                                          ExceptionCodes.ConfigurationFileReadError)

        try:
            config = ConfigParser()
            config.readfp(open(self.config_file_path))

        except (AttributeError, MissingSectionHeaderError, ParsingError) as parser_error:
            raise BackupSettingsException("Parsing configuration file error: {}"
                                          .format(parser_error.message),
                                          ExceptionCodes.ConfigurationFileParsingError)

        except IOError as exception:
            raise BackupSettingsException("Configuration file error: {}".format(exception),
                                          ExceptionCodes.ConfigurationFileReadError)

        self.logger.info("Reading configuration file '%s'.", self.config_file_path)
        return config

    def get_notification_handler(self):
        """
        Read the support contact information from the config file.

        1. EMAIL_TO: email address of the support team.
        2. EMAIL_URL: email server url.

        :return: the notification handler with the informed data.
        :raise BackupSettingsException: if invalid section/option given.
        """
        try:
            support_info = SupportInfo(str(self.config.get('SUPPORT_CONTACT', 'EMAIL_TO')),
                                       str(self.config.get('SUPPORT_CONTACT', 'EMAIL_URL')))
        except (NoSectionError, NoOptionError) as exception:
            raise BackupSettingsException("Error reading the configuration file '{}': {}"
                                          .format(self.config_file_name, exception.message),
                                          ExceptionCodes.ConfigurationFileOptionError)

        self.logger.info("The following support information was defined: %s.", support_info)

        return NotificationHandler(support_info.email, support_info.server, self.logger)

    def get_ombs_config(self):
        """
        Read the support contact information from the config file.

        1. IP: ip of OMBS server.
        2. USERNAME: account's username used on OMBS server.
        3. DIR: a path to a folder to store backups in OMBS server.

        If an error occurs, an Exception is raised with the details of the problem.

        :return: the notification handler with the informed data.
        :raise BackupSettingsException: if invalid section/option given.
        """
        try:
            ombs_config = OMBSConfig(str(self.config.get('OMBS_CONFIG', 'IP')),
                                     str(self.config.get('OMBS_CONFIG', 'USERNAME')),
                                     str(self.config.get('OMBS_CONFIG', 'BKP_DIR')),
                                     str(self.config.get('OMBS_CONFIG', 'KEY_PATH')))
        except (NoSectionError, NoOptionError) as exception:
            raise BackupSettingsException("Error reading the configuration file '{}': {}"
                                          .format(self.config_file_name, exception.message),
                                          ExceptionCodes.ConfigurationFileOptionError)

        self.logger.info("The following OMBS information was defined: %s.", ombs_config)

        return ombs_config

    def get_node_config_dict(self, hostname=None):
        """
        Read node configuration details.

        1. IP: ip of a node.
        2. TYPE: node_type of a node.
        3. EQ_PROMPT: prompt used on node OS system.
        4. USERNAME: account username used on the node.
        5. PASSWORD: account password used on the node.

        If an error occurs, an Exception is raised with the details of the problem.

        :param hostname: customer name, if running the script just for one customer.
        :return: dictionary with the information of all customers in the configuration file.
        :raise BackupSettingsException: if invalid section given.
        """
        try:
            sections = self.config.sections()
            sections.remove('SUPPORT_CONTACT')
            sections.remove('BACKUP_CONFIG')
            sections.remove('DELAY')
            sections.remove('OMBS_CONFIG')

            self.logger.info("The following nodes were defined: %s.", sections)

            customer_config_dict = {}

            if hostname and hostname.strip():
                self.logger.info("Configuration loaded only for: {}.".format(hostname))
                ip = self.config.get(hostname, "IP")
                node_type = self.config.get(hostname, "TYPE")
                eq_prompt = self.config.get(hostname, "EQ_PROMPT")
                username = self.config.get(hostname, "USERNAME")
                password = self.config.get(hostname, "PASSWORD")

                return {hostname: NodeConfig(hostname, ip, node_type, eq_prompt, username,
                                             password)}

            for section in sections:
                hostname = self.config.get(section, "HOSTNAME")
                ip = self.config.get(section, "IP")
                node_type = self.config.get(section, "TYPE")
                eq_prompt = self.config.get(section, "EQ_PROMPT")
                username = self.config.get(section, "USERNAME")
                password = self.config.get(section, "PASSWORD")

                customer_config_dict[section] = NodeConfig(hostname, ip, node_type, eq_prompt,
                                                           username, password)

        except NoSectionError as error:
            raise BackupSettingsException(ExceptionCodes.MissingNodeSection, error)

        except NoOptionError as error:
            raise BackupSettingsException(ExceptionCodes.ConfigurationFileOptionError, error)

        return customer_config_dict

    def get_backup_config(self):
        """
        Read the support contact information from the config file.

        1. PATH: path to the folder to store backups.
        2. BUFFER_SIZE: size of pexpect buffer for reading the configuration.
        3. MIN_BACKUP_SIZE: minimal size of a backup eligible for sending.

        :return: the notification handler with the informed data.
        :raise BackupSettingsException: if invalid section/option given.
        """
        try:
            backup_config = BackupConfig(str(self.config.get('BACKUP_CONFIG', 'PATH')),
                                         int(to_bytes(self.config.get('BACKUP_CONFIG',
                                                                      'BUFFER_SIZE'))),
                                         int(to_bytes(self.config.get('BACKUP_CONFIG',
                                                                      'MIN_BACKUP_SIZE'))))
        except (NoSectionError, NoOptionError) as exception:
            raise BackupSettingsException("Error reading the configuration file '{}': {}"
                                          .format(self.config_file_name, exception.message),
                                          ExceptionCodes.ConfigurationFileOptionError)

        self.logger.info("The following backup information was defined: %s.", backup_config)

        return backup_config

    def get_delay_config(self):
        """
        Read the support contact information from the config file.

        1. BKP_MAX_DELAY: maximum time of delay.

        :return: the notification handler with the informed data.
        :raise BackupSettingsException: if invalid section/option given.
        """
        try:
            delay_config = DelayConfig(str(self.config.get('DELAY', 'BKP_MAX_DELAY')))
        except (NoSectionError, NoOptionError) as exception:
            raise BackupSettingsException("Error reading the configuration file '{}': {}"
                                          .format(self.config_file_name, exception.message),
                                          ExceptionCodes.ConfigurationFileOptionError)
        return delay_config

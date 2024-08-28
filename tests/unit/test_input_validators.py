##############################################################################
# COPYRIGHT Ericsson 2018
#
# The copyright to the computer program(s) herein is the property of
# Ericsson Inc. The programs may be used and/or copied only with written
# permission from Ericsson Inc. or in accordance with the terms and
# conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
##############################################################################

# For unable to import
# For the snake_case comments (invalid test names)
# pylint: disable=C0103,E0401

"""Module for unit testing the bur_input_validators.py script."""

import unittest

import mock

from network_backup_onsite.exceptions import BackupSettingsException
import network_backup_onsite.input_validators as validators

INPUT_VALIDATORS = 'network_backup_onsite.input_validators.'
BACKUP_SETTINGS = 'network_backup_onsite.backup_settings.'
CONFIG_FILE_NAME = 'fake_config_file'

TEST_IP = '127.0.0.1'
TEST_TYPE = 'test_type'
TEST_EQ_PROMPT = 'test_prompt'
TEST_USERNAME = 'test_username'
TEST_PASSWORD = 'test_password'


class InputValidatorsValidateScriptSettingsTestCase(unittest.TestCase):
    """ Class for unit testing the validate_script_settings function."""

    def setUp(self):
        """Setting up test constants/variables."""
        with mock.patch(BACKUP_SETTINGS + 'NotificationHandler') as nh:
            self.mock_notification_handler = nh

        with mock.patch(BACKUP_SETTINGS + 'NodeConfig') as node_config:
            self.mock_node_config_dict = dict({'customer_0': node_config})

        with mock.patch(BACKUP_SETTINGS + 'OMBSConfig') as ombs_config:
            self.mock_ombs_config = ombs_config

        with mock.patch(BACKUP_SETTINGS + 'BackupConfig') as backup_config:
            self.mock_backup_config = backup_config

        with mock.patch(BACKUP_SETTINGS + 'DelayConfig') as delay_config:
            self.mock_delay_config = delay_config

        with mock.patch(INPUT_VALIDATORS + 'CustomLogger') as logger:
            self.mock_logger = logger

    @mock.patch(INPUT_VALIDATORS + 'ScriptSettings.get_node_config_dict')
    @mock.patch(INPUT_VALIDATORS + 'ScriptSettings')
    def test_validate_script_settings_check_return_dict(self, mock_script_settings,
                                                        mock_node_config):
        """
        Assert if returns a dictionary with the four objects if ScriptSettings object was
        created correctly with config_file.

        :param mock_script_settings: mock of ScriptSettings object.
        :param mock_node_config: ScriptSettings.get_customer_config_dict method.
        """
        mock_script_settings.return_value.get_notification_handler = self.mock_notification_handler
        mock_script_settings.return_value.get_backup_config = self.mock_backup_config
        mock_script_settings.return_value.get_delay_config = self.mock_delay_config
        mock_script_settings.return_value.get_ombs_config = self.mock_ombs_config
        mock_node_config.return_value = self.mock_node_config_dict

        result = validators.validate_script_settings(CONFIG_FILE_NAME, {}, self.mock_logger)

        self.assertIsNotNone(result)
        self.assertIs(len(validators.SCRIPT_OBJECTS), len(result))

    @mock.patch(INPUT_VALIDATORS + 'ScriptSettings')
    def test_validate_script_settings_notification_handler_error(self, mock_script_settings):
        """
        Assert if raises an Exception when trying to get NotificationHandler from ScriptSetting.

        :param mock_script_settings: mock of ScriptSettings object.
        """
        error_msg = "Error validating ScriptSettings object due to: Error: 30. No NH available."

        mock_script_settings.return_value.get_notification_handler.side_effect = \
            BackupSettingsException("No NH available")

        with self.assertRaises(Exception) as cex:
            validators.validate_script_settings(CONFIG_FILE_NAME, {}, self.mock_logger)

        self.assertEqual(error_msg, cex.exception.message)

    @mock.patch(INPUT_VALIDATORS + 'ScriptSettings')
    def test_validate_script_settings_backup_config_error(self, mock_script_settings):
        """
        Assert if raises an Exception when trying to get Gnupg_Manager from ScriptSetting.

        :param mock_script_settings: mock of ScriptSettings object.
        """
        error_msg = "Error validating ScriptSettings object due to: Error: 30. No BACKUP_CONFIG " \
                    "available."

        mock_script_settings.return_value.get_backup_config.side_effect = \
            BackupSettingsException("No BACKUP_CONFIG available")

        with self.assertRaises(Exception) as cex:
            validators.validate_script_settings(CONFIG_FILE_NAME, {}, self.mock_logger)

        self.assertEqual(error_msg, cex.exception.message)

    @mock.patch(INPUT_VALIDATORS + 'ScriptSettings')
    def test_validate_script_settings_node_config_dict_error(self, mock_script_settings):
        """
        Assert if raises an Exception when trying to get enmaas_config_dict from ScriptSetting.

        :param mock_script_settings: mock of ScriptSettings object.
        """
        error_msg = "Error validating ScriptSettings object due to: " \
                    "Error: 30. No node configuration available."

        mock_script_settings.return_value.get_node_config_dict.side_effect = \
            BackupSettingsException("No node configuration available")

        with self.assertRaises(Exception) as cex:
            validators.validate_script_settings(CONFIG_FILE_NAME, {}, self.mock_logger)

        self.assertEqual(error_msg, cex.exception.message)

    @mock.patch(INPUT_VALIDATORS + 'ScriptSettings')
    def test_validate_script_settings_delay_config_error(self, mock_script_settings):
        """
        Assert if raises an Exception when trying to get DelayConfig from ScriptSetting.

        :param mock_script_settings: mock of ScriptSettings object.
        """
        error_msg = "Error validating ScriptSettings object due to: Error: 30. No DELAY_CONFIG " \
                    "available."

        mock_script_settings.return_value.get_delay_config.side_effect = \
            BackupSettingsException("No DELAY_CONFIG available")

        with self.assertRaises(Exception) as cex:
            validators.validate_script_settings(CONFIG_FILE_NAME, {}, self.mock_logger)

        self.assertEqual(error_msg, cex.exception.message)

    @mock.patch(INPUT_VALIDATORS + 'ScriptSettings')
    def test_validate_script_settings_ombs_config_error(self, mock_script_settings):
        """
        Assert if raises an Exception when trying to get DelayConfig from ScriptSetting.

        :param mock_script_settings: mock of ScriptSettings object.
        """
        error_msg = "Error validating ScriptSettings object due to: Error: 30. No OMBS_CONFIG " \
                    "available."

        mock_script_settings.return_value.get_ombs_config.side_effect = \
            BackupSettingsException("No OMBS_CONFIG available")

        with self.assertRaises(Exception) as cex:
            validators.validate_script_settings(CONFIG_FILE_NAME, {}, self.mock_logger)

        self.assertEqual(error_msg, cex.exception.message)


class InputValidatorsValidateNodesTestCase(unittest.TestCase):
    """Class to test validate_node method."""

    def setUp(self):
        """Setting up test constants/variables."""
        with mock.patch(BACKUP_SETTINGS + 'NodeConfig') as node_config:
            self.mock_node_config_dict = dict({'customer_0': node_config})

    def test_validate_nodes_no_ip(self):
        """Check the return value if no IP specified."""
        self.mock_node_config_dict.get('customer_0').ip = ""

        self.assertFalse(validators.validate_nodes(self.mock_node_config_dict, CONFIG_FILE_NAME))

    def test_validate_nodes_no_type(self):
        """Check the return value if no TYPE specified."""
        self.mock_node_config_dict.get('customer_0').ip = TEST_IP
        self.mock_node_config_dict.get('customer_0').type = ""

        self.assertFalse(validators.validate_nodes(self.mock_node_config_dict, CONFIG_FILE_NAME))

    def test_validate_nodes_no_eq_prompt(self):
        """Check the return value if no EQ_PROMPT specified."""
        self.mock_node_config_dict.get('customer_0').ip = TEST_IP
        self.mock_node_config_dict.get('customer_0').type = TEST_TYPE
        self.mock_node_config_dict.get('customer_0').eq_prompt = ""

        self.assertFalse(validators.validate_nodes(self.mock_node_config_dict, CONFIG_FILE_NAME))

    def test_validate_nodes_no_username(self):
        """Check the return value if no USERNAME specified."""
        self.mock_node_config_dict.get('customer_0').ip = TEST_IP
        self.mock_node_config_dict.get('customer_0').type = TEST_TYPE
        self.mock_node_config_dict.get('customer_0').eq_prompt = TEST_EQ_PROMPT
        self.mock_node_config_dict.get('customer_0').username = ""

        self.assertFalse(validators.validate_nodes(self.mock_node_config_dict, CONFIG_FILE_NAME))

    def test_validate_nodes_no_password(self):
        """Check the return value if no PASSWORD specified."""
        self.mock_node_config_dict.get('customer_0').ip = TEST_IP
        self.mock_node_config_dict.get('customer_0').type = TEST_TYPE
        self.mock_node_config_dict.get('customer_0').eq_prompt = TEST_EQ_PROMPT
        self.mock_node_config_dict.get('customer_0').username = TEST_USERNAME
        self.mock_node_config_dict.get('customer_0').password = ""

        self.assertFalse(validators.validate_nodes(self.mock_node_config_dict, CONFIG_FILE_NAME))

    @mock.patch(INPUT_VALIDATORS + 'is_valid_ip')
    def test_validate_nodes_invalid_ip(self, mock_is_valid_ip):
        """
        Check the return value if ip is invalid.

        :param mock_is_valid_ip: mock of is_valid_ip method.
        """
        self.mock_node_config_dict.get('customer_0').ip = TEST_IP
        self.mock_node_config_dict.get('customer_0').type = TEST_TYPE
        self.mock_node_config_dict.get('customer_0').eq_prompt = TEST_EQ_PROMPT
        self.mock_node_config_dict.get('customer_0').username = TEST_USERNAME
        self.mock_node_config_dict.get('customer_0').password = TEST_PASSWORD

        mock_is_valid_ip.return_value = False

        self.assertFalse(validators.validate_nodes(self.mock_node_config_dict, CONFIG_FILE_NAME))

    @mock.patch(INPUT_VALIDATORS + 'is_host_accessible')
    @mock.patch(INPUT_VALIDATORS + 'is_valid_ip')
    def test_validate_nodes_inaccessible_host(self, mock_is_valid_ip, mock_is_host_accessible):
        """
        Check return value if host inaccessible.

        :param mock_is_valid_ip: mock of is_valid_ip method.
        :param mock_is_host_accessible: mock of is_host_accessible method.
        """
        self.mock_node_config_dict.get('customer_0').ip = TEST_IP
        self.mock_node_config_dict.get('customer_0').type = TEST_TYPE
        self.mock_node_config_dict.get('customer_0').eq_prompt = TEST_EQ_PROMPT
        self.mock_node_config_dict.get('customer_0').username = TEST_USERNAME
        self.mock_node_config_dict.get('customer_0').password = TEST_PASSWORD

        mock_is_valid_ip.return_value = True
        mock_is_host_accessible.return_value = False

        self.assertFalse(validators.validate_nodes(self.mock_node_config_dict, CONFIG_FILE_NAME))

    @mock.patch(INPUT_VALIDATORS + 'is_host_accessible')
    @mock.patch(INPUT_VALIDATORS + 'is_valid_ip')
    def test_validate_nodes_success(self, mock_is_valid_ip, mock_is_host_accessible):
        """
        Check the return value if the parameters are valid.

        :param mock_is_valid_ip: mock of is_valid_ip method.
        :param mock_is_host_accessible: mock of is_host_accessible method.
        """
        self.mock_node_config_dict.get('customer_0').ip = TEST_IP
        self.mock_node_config_dict.get('customer_0').type = TEST_TYPE
        self.mock_node_config_dict.get('customer_0').eq_prompt = TEST_EQ_PROMPT
        self.mock_node_config_dict.get('customer_0').username = TEST_USERNAME
        self.mock_node_config_dict.get('customer_0').password = TEST_PASSWORD

        mock_is_valid_ip.return_value = True
        mock_is_host_accessible.return_value = True

        self.assertTrue(validators.validate_nodes(self.mock_node_config_dict, CONFIG_FILE_NAME))


class InputValidatorsValidateBackupLocationTestCase(unittest.TestCase):
    """Class to test validate_backup_location."""

    def setUp(self):
        """ Setting up test constants/variables."""
        with mock.patch(BACKUP_SETTINGS + 'BackupConfig') as backup_config:
            self.mock_backup_config = backup_config

    @mock.patch(INPUT_VALIDATORS + 'os')
    def test_validate_backup_location_no_path(self, mock_os):
        """
        Check return value if path does not exist.

        :param mock_os:  mock of os library.
        """
        mock_os.path.exists.return_value = False
        self.assertFalse(validators.validate_backup_location(self.mock_backup_config))

    @mock.patch(INPUT_VALIDATORS + 'os')
    def test_validate_backup_location_existing_path(self, mock_os):
        """
        Test return value if the path exists.

        :param mock_os: mock of os library.
        """
        mock_os.path.exists.return_value = True
        self.assertTrue(validators.validate_backup_location(self.mock_backup_config))


class InputValidatorsValidateNodesBackupLocationTestCase(unittest.TestCase):
    """Class to test validate_nodes_backup_location."""

    def setUp(self):
        """Setting up test constants/variables."""
        with mock.patch(INPUT_VALIDATORS + 'ScriptSettings') as script_settings:
            self.mock_script_settings = script_settings

        with mock.patch(INPUT_VALIDATORS + 'CustomLogger') as logger:
            self.mock_logger = logger

    @mock.patch(INPUT_VALIDATORS + 'validate_nodes')
    def test_validate_nodes_backup_location_invalid_node(self, mock_validate_nodes):
        """
        Check raise of exceptions if the node is invalid.

        :param mock_validate_nodes: mock of validate_nodes method.
        """
        mock_validate_nodes.side_effect = [Exception("Error")]

        with self.assertRaises(Exception) as e:
            validators.validate_nodes_backup_location(CONFIG_FILE_NAME, self.mock_script_settings,
                                                      self.mock_logger)
        self.assertEqual("Error", e.exception.message)

    @mock.patch(INPUT_VALIDATORS + 'validate_backup_location')
    def test_validate_nodes_backup_location_invalid_backup_location(self,
                                                                    mock_validate_backup_location):
        """
        Check raise of exception if the backup location is invalid.

        :param mock_validate_backup_location:  mock of validate_backup_location method.
        """
        mock_validate_backup_location.side_effect = [Exception("Error")]

        with self.assertRaises(Exception) as e:
            validators.validate_nodes_backup_location(CONFIG_FILE_NAME, self.mock_script_settings,
                                                      self.mock_logger)
        self.assertEqual("Error", e.exception.message)

    def test_validate_nodes_backup_location_success(self):
        """Test return value if parameters are valid."""
        self.assertTrue(validators.validate_nodes_backup_location(CONFIG_FILE_NAME,
                                                                  self.mock_script_settings,
                                                                  self.mock_logger))

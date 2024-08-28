##############################################################################
# COPYRIGHT Ericsson 2018
#
# The copyright to the computer program(s) herein is the property of
# Ericsson Inc. The programs may be used and/or copied only with written
# permission from Ericsson Inc. or in accordance with the terms and
# conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
############################################################################

# For unable to import
# For the snake_case comments (invalid test names)
# pylint: disable=C0103,E0401

"""Module for unit testing the validation in main.py script."""

import unittest

import mock

from network_backup_onsite.main import validate_backup_file_onsite, \
    validate_backup_folder_and_files_onsite

MAIN = 'network_backup_onsite.main.'
TEST_PATH = 'test_path_'
TEST_FILE = 'test_file'
TEST_NUMBER_NODES = 1


class NodeBackupHandlerValidateBackupFileOnsiteTestCase(unittest.TestCase):
    """Test case to test validate_backup_file_onsite method."""

    @mock.patch('network_backup_onsite.backup_settings.BackupConfig')
    @mock.patch('network_backup_onsite.logger.CustomLogger')
    @mock.patch(MAIN + 'os')
    def test_validate_backup_file_onsite_failure(self, mock_os, mock_logger, mock_backup_config):
        """
        Check return value if the execution fails.

        :param mock_os: mock of os library.
        :param mock_logger: mock instance of CustomLogger.
        :param mock_backup_config:  mock instance of BackupConfig.
        """
        mock_os.path.isfile.return_value = TEST_FILE
        mock_os.path.getsize.return_value = 3
        mock_backup_config.backup_size = 2

        self.assertFalse(validate_backup_file_onsite(mock_backup_config, TEST_FILE, mock_logger))

    @mock.patch('network_backup_onsite.backup_settings.BackupConfig')
    @mock.patch('network_backup_onsite.logger.CustomLogger')
    @mock.patch(MAIN + 'os')
    def test_validate_backup_file_onsite_success(self, mock_os, mock_logger, mock_backup_config):
        """
        Check return value if execution is successful.

        :param mock_os: mock of os library.
        :param mock_logger: mock instance of CustomLogger.
        :param mock_backup_config:  mock instance of BackupConfig.
        """
        mock_os.path.getsize.return_value = 2
        mock_backup_config.min_backup_size = 1

        self.assertTrue(validate_backup_file_onsite(mock_backup_config, TEST_FILE, mock_logger))


class NodeBackupHandlerValidateBackupFolderAndFilesOnsiteTestCase(unittest.TestCase):
    """Test case to test validate_backup_folder_and_files_onsite method."""

    @mock.patch('network_backup_onsite.backup_settings.BackupConfig')
    @mock.patch('network_backup_onsite.logger.CustomLogger')
    @mock.patch(MAIN + 'os')
    def test_validate_backup_folder_and_files_onsite_not_enough_files(self, mock_os, mock_logger,
                                                                      mock_backup_config):
        """
        Check return value if the number of files is improper.

        :param mock_os: mock of os library.
        :param mock_logger: mock of CustomLogger.
        :param mock_backup_config: mock of BackupConfig.
        """
        mock_os.listdir.return_value = ""
        mock_os.path.isfile.return_value = True
        mock_os.path.join.return_value = TEST_PATH

        self.assertFalse(validate_backup_folder_and_files_onsite(TEST_NUMBER_NODES,
                                                                 mock_backup_config, TEST_PATH,
                                                                 mock_logger))

    @mock.patch('network_backup_onsite.backup_settings.BackupConfig')
    @mock.patch(MAIN + 'validate_backup_file_onsite')
    @mock.patch('network_backup_onsite.logger.CustomLogger')
    @mock.patch(MAIN + 'os')
    def test_validate_backup_folder_and_files_onsite_validation_failure(self, mock_os,
                                                                        mock_logger,
                                                                        mock_validate_backup_file,
                                                                        mock_backup_config):
        """
        Test the return value if folder validation fails.

        :param mock_os: mock of os library.
        :param mock_logger: mock of CustomLogger.
        :param mock_validate_backup_file: mock of validate_backup_file method.
        :param mock_backup_config: mock of BackupConfig.
        """
        mock_os.listdir.return_value = ""
        mock_os.path.isfile.return_value = True
        mock_os.path.join.return_value = TEST_PATH
        mock_validate_backup_file.return_value = False

        self.assertFalse(validate_backup_folder_and_files_onsite(TEST_NUMBER_NODES,
                                                                 mock_backup_config, TEST_PATH,
                                                                 mock_logger))

    @mock.patch('network_backup_onsite.backup_settings.BackupConfig')
    @mock.patch(MAIN + 'validate_backup_file_onsite')
    @mock.patch('network_backup_onsite.logger.CustomLogger')
    @mock.patch(MAIN + 'os')
    def test_validate_backup_folder_and_files_onsite_success(self, mock_os, mock_logger,
                                                             mock_validate_backup_file,
                                                             mock_backup_config):
        """
        Check the return value if arguments are valid.

        :param mock_os: mock of os library.
        :param mock_logger: mock of CustomLogger.
        :param mock_validate_backup_file: mock of validate_backup_file method.
        :param mock_backup_config: mock of BackupConfig.
        """
        mock_os.listdir.return_value = TEST_FILE
        mock_os.path.isfile.return_value = True
        mock_os.path.join.return_value = TEST_FILE
        mock_validate_backup_file.return_value = True

        self.assertTrue(validate_backup_folder_and_files_onsite(9, mock_backup_config, TEST_PATH,
                                                                mock_logger))

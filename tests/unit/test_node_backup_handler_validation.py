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

"""Module for unit testing the node_backup_handler.py script."""

import datetime
import unittest

import mock

from network_backup_onsite.node_backup_handler import TIME_FORMAT, create_backup_folder_onsite

NODE_BACKUP_HANDLER = 'network_backup_onsite.node_backup_handler.'
TEMPLATE = 'template_1'
TEST_PATH = 'test_path_'
TEST_FILE = 'test_file'
TEST_NUMBER_NODES = 1
TEST_HOST = "10.0.2.1@user"


class MainCreateBackupFolderOnsiteTestCase(unittest.TestCase):
    """Test case to test create_backup_folder_onsite method."""

    @mock.patch(NODE_BACKUP_HANDLER + 'create_path')
    @mock.patch(NODE_BACKUP_HANDLER + 'CustomLogger')
    @mock.patch(NODE_BACKUP_HANDLER + 'os')
    def test_create_backup_folder_onsite_raise_exception(self, mock_os, mock_logger,
                                                         mock_create_path):
        """
        Test the raise of exception if folder was not created.

        :param mock_os: mocked os library.
        :param mock_logger: mocked instance of CustomLogger.
        :param mock_create_path: mocked backup folder path.
        """
        mock_os.path.exists.return_value = False
        mock_create_path.return_value = False

        now = datetime.datetime.now()
        mock_bkp_folder_name = TEMPLATE + now.strftime(TIME_FORMAT)
        mock_os.path.join.return_value = mock_bkp_folder_name

        error_msg = "Failed to create backup folder {} onsite.".format(mock_bkp_folder_name)

        with self.assertRaises(Exception) as cex:
            create_backup_folder_onsite(TEMPLATE, TEST_PATH, mock_logger)

        self.assertEqual(error_msg, cex.exception.message)

    @mock.patch(NODE_BACKUP_HANDLER + 'create_path')
    @mock.patch(NODE_BACKUP_HANDLER + 'CustomLogger')
    @mock.patch(NODE_BACKUP_HANDLER + 'os')
    def test_create_backup_folder_onsite_new_folder(self, mock_os, mock_logger, mock_create_path):
        """
        Test the returning file if backup folder was created.

        :param mock_os: mocked os library.
        :param mock_logger: mocked instance of CustomLogger.
        :param mock_create_path: mocked backup folder path.
        """
        mock_os.path.exists.return_value = False
        mock_create_path.return_value = True

        now = datetime.datetime.now()
        mock_bkp_folder_name = TEMPLATE + now.strftime(TIME_FORMAT)
        mock_os.path.join.return_value = mock_bkp_folder_name

        result = create_backup_folder_onsite(TEMPLATE, TEST_PATH, mock_logger)

        self.assertEqual(mock_bkp_folder_name, result)

    @mock.patch(NODE_BACKUP_HANDLER + 'create_path')
    @mock.patch(NODE_BACKUP_HANDLER + 'CustomLogger')
    @mock.patch(NODE_BACKUP_HANDLER + 'os')
    def test_create_backup_folder_onsite_existing_folder(self, mock_os, mock_logger,
                                                         mock_create_path):
        """
        Test the returning file if backup folder already exists.

        :param mock_os: mocked os library.
        :param mock_logger: mocked instance of CustomLogger.
        :param mock_create_path: mocked backup folder path.
        """
        mock_os.path.exists.return_value = True
        mock_create_path.return_value = True

        now = datetime.datetime.now()
        mock_bkp_folder_name = TEMPLATE + now.strftime(TIME_FORMAT)
        mock_os.path.join.return_value = mock_bkp_folder_name

        result = create_backup_folder_onsite(TEMPLATE, TEST_PATH, mock_logger)

        self.assertEqual(mock_bkp_folder_name, result)

##############################################################################
# COPYRIGHT Ericsson 2018
#
# The copyright to the computer program(s) herein is the property of
# Ericsson Inc. The programs may be used and/or copied only with written
# permission from Ericsson Inc. or in accordance with the terms and
# conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
##############################################################################

# For the snake_case comments
# pylint: disable=C0103

"""This module is for unit tests from the utils.py script."""

import os
import unittest

import mock

from network_backup_onsite import utils

SCRIPT_PATH = os.path.dirname(__file__)
TMP_DIR = os.path.join(SCRIPT_PATH, "temp_dir")
VALID_COMMAND = "echo Hello World!\n"
VALID_HOST = '127.0.0.1'
INVALID_HOST = "2.3.4."
INVALID_COMMAND = 'bla bla bla'
TIME_SLEEP = 3
FILE_NAME = "volume_file"
DEFAULT_FILE_SIZE = 100 * 1024
TEMPLATE = "folder1"


class UtilsCreatePathTestCase(unittest.TestCase):
    """Test Cases for create_path method in utils.py."""

    @classmethod
    @mock.patch('os.makedirs', autospec=True)
    def test_create_path_with_valid_path(cls, mock_make_dirs):
        """
        Test if destination directory is created when valid path is provided.

        :param mock_make_dirs: mocking os.makedirs method.
        """
        utils.create_path(TMP_DIR)
        mock_make_dirs.assert_called_once_with(TMP_DIR)

    def test_create_path_with_no_arguments(self):
        """ Test if path is created when no argument is provided."""
        with self.assertRaises(TypeError):
            utils.create_path()

    def test_create_path_with_multiple_arguments(self):
        """Test that when attempt creating path with multiple arguments raise TypeError."""
        with self.assertRaises(TypeError):
            utils.create_path(TMP_DIR, TMP_DIR)

    @classmethod
    @mock.patch.object(os.path, 'exists')
    def test_create_path_already_exists(cls, mock_exists):
        """
        Test if existence of path is being checked.

        :param mock_exists: mocking os.path.exists method.
        """
        utils.create_path(TMP_DIR)
        mock_exists.assert_called_once_with(TMP_DIR)


class UtilsRunRemoteCommandTestCase(unittest.TestCase):
    """Test Cases for popen_communicate method in utils.py."""

    @mock.patch("network_backup_onsite.utils.TIMEOUT")
    def test_run_remote_command_valid_host_and_command(self, mock_timeout):
        """
        Test open pipe with valid host and valid command.

        :param mock_timeout: mocking backup.utils.TIMEOUT constant.
        """
        mock_timeout.return_value = 20
        stdout, _ = utils.popen_communicate(VALID_HOST, VALID_COMMAND)
        self.assertEqual(stdout, b"Hello World!\n")
        stdout, _ = utils.popen_communicate('localhost', VALID_COMMAND)
        self.assertEqual(b"Hello World!\n", stdout)

    def test_run_remote_command_invalid_host(self):
        """Test open pipe with invalid host."""
        stdout, _ = utils.popen_communicate(INVALID_HOST, VALID_COMMAND)
        self.assertEqual("", stdout)

    def test_run_remote_command_invalid_command(self):
        """Test open pipe with invalid command."""

        stdout, _ = utils.popen_communicate(VALID_HOST, INVALID_COMMAND)
        self.assertEqual("", stdout)


class UtilsIsValidIpTestCase(unittest.TestCase):
    """Test Cases for is_valid_ip method in utils.py."""

    def test_is_valid_ip(self):
        """Test if ip is valid."""
        self.assertTrue(utils.is_valid_ip(VALID_HOST))

    def test_is_valid_ip_invalid_ip(self):
        """Test invalid ip."""
        self.assertFalse(utils.is_valid_ip(INVALID_HOST))


class UtilsValidateHostIsAccessibleTestCase(unittest.TestCase):
    """Test Cases for validate_host_is_accessible method in utils.py."""

    def test_validate_host_is_accessible(self):
        """ Test if valid host is accessible."""
        self.assertTrue(utils.is_host_accessible("localhost"))

    def test_validate_host_is_accessible_invalid_host(self):
        """Test invalid host is not accessible."""
        self.assertFalse(utils.is_host_accessible(INVALID_HOST))

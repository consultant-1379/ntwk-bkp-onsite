##############################################################################
# COPYRIGHT Ericsson 2018
#
# The copyright to the computer program(s) herein is the property of
# Ericsson Inc. The programs may be used and/or copied only with written
# permission from Ericsson Inc. or in accordance with the terms and
# conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
##############################################################################

"""Module for exception handlers."""

from enum import Enum


class ExceptionCodes(Enum):
    """Enum custom codes for errors."""

    DefaultExceptionCode = 30
    InvalidPath = 31
    EmptyValue = 32
    InvalidValue = 33
    CannotCreatePath = 34
    InvalidIPAddress = 35
    CannotAccessHost = 36
    MissingSupportContactSection = 37
    MissingNodeSection = 38

    ErrorSendingEmail = 40

    ConfigurationFileReadError = 51
    ConfigurationFileParsingError = 52
    ConfigurationFileOptionError = 53


class BasicException(Exception):
    """Class for defining the structure of custom exceptions."""

    def __init__(self, message, code):
        """
        Constructor.

        :param message: the message.
        :param code: exit code.
        """
        super(BasicException, self).__init__(message, code)
        self.message = message
        self.code = code

    def __str__(self):
        """Prepare string representation."""
        return "Error: {}. {}".format(self.code.value, self.message)

    def __repr__(self):
        """Return string representation."""
        return self.__str__()


class NotificationHandlerException(BasicException):
    """Exception class to refer error raised from NotificationHandler."""

    def __init__(self, message, code=None):
        """
        Constructor.

        :param message: the message.
        :param code: exit code.
        """
        super(NotificationHandlerException, self).__init__(message, code)
        self.message = message
        self.code = code if code else ExceptionCodes.DefaultExceptionCode


class BackupSettingsException(BasicException):
    """Exception class to refer error raised from backup_settings.py script."""

    def __init__(self, message, code=None):
        """
        Constructor.

        :param message: the message.
        :param code: exit code.
        """
        super(BackupSettingsException, self).__init__(message, code)
        self.message = message
        self.code = code if code else ExceptionCodes.DefaultExceptionCode

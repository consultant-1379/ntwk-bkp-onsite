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

# For import error
# pylint: disable=E0401

"""Module for notification features (formatting and sending emails)."""

import json
import os

import requests
from requests.exceptions import RequestException

from network_backup_onsite import __version__
from network_backup_onsite.exceptions import ExceptionCodes, \
    NotificationHandlerException
from network_backup_onsite.logger import CustomLogger
from network_backup_onsite.utils import get_cli_arguments

DEFAULT_DOMAIN = "ericsson.com"

SCRIPT_FILE = os.path.basename(__file__).split('.')[0]
SEP1 = "-------------------------------------------------------------------------------------------"
SEP2 = "==========================================================================================="


class NotificationHandler:
    """Responsible for handling the BUR notification mails."""

    # types of e-mail notification
    OTHER = 0
    SUCCESS = 1
    ERROR = 2

    def __init__(self, email_to, email_url, logger, email_domain=None):
        """
        Initialize Notification Handler object.

        :param email_to: where to send notification email.
        :param email_url: which email service to use.
        :param logger: which logger to use.
        :return: true, if success, false, otherwise.
        """
        self.email_to = email_to
        self.email_url = email_url
        self.email_domain = email_domain if email_domain else DEFAULT_DOMAIN
        self.logger = CustomLogger(SCRIPT_FILE, logger.log_root_path, logger.log_file_name,
                                   logger.log_level)

    def send_mail(self, sender, subject, message):
        """
        Prepare and send notification e-mail whenever an error happens during BUR process.

        Read e-mail service configuration attribute EMAIL_URL.

        :param sender: notification e-mail sender.
        :param subject: notification e-mail subject.
        :param message: notification e-mail message.
        :return: true, if success.
        :raise RequestException: if email can't be sent.
        """
        if not sender.strip():
            raise Exception("An empty sender was informed.")

        from_sender = "{}@{}".format(str(sender).strip().lower(), self.email_domain)

        self.logger.log_info("Sending e-mail from {} to {} with subject '{}'."
                             .format(from_sender, self.email_to, subject))

        personalizations = [{"to": [{"email": self.email_to}], "subject": subject}]

        json_string = {"personalizations": personalizations,
                       "from": {"email": from_sender},
                       "content": [{"type": "text/html", "value": message}]}

        post_data = json.dumps(json_string).encode("utf8")
        headers = {'cache-control': 'no-cache', 'content-type': 'application/json'}

        try:
            response = requests.post(self.email_url,
                                     data=post_data,
                                     headers=headers,
                                     verify=False,
                                     timeout=10)  # nosec

            response.raise_for_status()

        except RequestException as error:
            raise NotificationHandlerException("Failed to send e-mail to {}. Cause: {}"
                                               .format(self.email_to, error.message),
                                               ExceptionCodes.ErrorSendingEmail)

        self.logger.info("E-mail sent successfully to: '{}'.".format(self.email_to))

        return True

    def send_error_email(self, node_name, subject, error_list, error_code=None):
        """
        Process the arguments to create an error e-mail notification, then send it.

        Log the errors that happened during the process.

        :param node_name: node under any process that caused the error, used as a sender.
        :param subject: error subject.
        :param error_list: list of errors that happened during the process.
        :param error_code: in case of system exit, inform the error code.
        :return: self.send_mail method.
        """
        if not isinstance(error_list, list):
            error_list = [error_list]

        if error_list:
            self.logger.error("{} Cause:".format(subject))
            for error in error_list:
                self.logger.error(error)

        message = self._prepare_email_body(self.ERROR, error_list, error_code)

        return self.send_mail(node_name, subject, message)

    def send_success_email(self, node_name, subject, success_list):
        """
        Process the arguments to create a success e-mail notification, then send it.

        :param node_name: deployment under any process that was finished, used as a sender.
        :param subject: briefly information about the process.
        :param success_list: list of success messages.
        :return: self.send_mail method.
        """
        if not isinstance(success_list, list):
            success_list = [success_list]

        message = self._prepare_email_body(self.SUCCESS, success_list)

        return self.send_mail(node_name, subject, message)

    def send_warning_email(self, node_name, subject, warning_list):
        """
        Process the arguments to create a warning  e-mail notification, then send it.

        :param node_name: deployment under any process that is running, used as a sender.
        :param subject: briefly information about the process.
        :param warning_list: list of warning messages.
        :return: self.send_mail method.
        """
        if not isinstance(warning_list, list):
            warning_list = [warning_list]

        message = self._prepare_email_body(self.OTHER, warning_list)

        return self.send_mail(node_name, subject, message)

    def _prepare_email_body(self, type_email, message_list, error_code=None):
        """
        Prepare the e-mail notification message.

        :param type_email: if it's a warning, error or success e-mail.
        :param message_list: warning, error or success message list during the process.
        :param error_code: in case of system exit, inform the error code.
        :return: a formatted e-mail body with all the errors from error_list and error_code.
        """
        email_body = self._get_cli_arguments_into_email_body()

        if type_email == self.ERROR and message_list:
            email_body += "The following errors happened during this operation:<br>"

        if type_email == self.SUCCESS and message_list:
            email_body += "The following operations were successfully finished:<br>"

        email_body += self._get_lines_from_list(message_list)

        if type_email == self.ERROR and error_code:
            email_body += "System stopped with error code: {}.".format(error_code)

        email_body += "<br><br>"
        email_body += "ntwk_bkp Version: " + __version__

        return email_body

    def _get_lines_from_list(self, email_text_list):
        """
        Transform a list of messages into a full text message.

        :param email_text_list: list of messages.
        :return: a formatted text with break lines.
        """
        full_text = ""

        if email_text_list:
            for line in email_text_list:
                if line and isinstance(line, list):
                    full_text += self._get_lines_from_list(line)
                elif line:
                    full_text += "{}<br>".format(line)

        return full_text

    @staticmethod
    def _get_cli_arguments_into_email_body():
        """
        Get console input and include to the email body.

        :return: a line for any e-mail with information about CLI arguments.
        """
        cli_message_line = "ntwk_bkp ran with no arguments.<br>"

        provided_args = get_cli_arguments()

        if provided_args:
            cli_message_line = "ntwk_bkp ran with the following arguments:<br>"
            cli_message_line += "{}<br><br>".format(provided_args)

        return cli_message_line

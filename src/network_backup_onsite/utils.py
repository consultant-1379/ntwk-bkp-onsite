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
# pylint: disable=C0103

"""Module to handle helper functions."""

import os
import socket
from subprocess import PIPE, Popen
import sys
from threading import Timer
import time


LOG_SUFFIX = "log"

SUCCESS_FLAG_FILE = "BACKUP_OK"

LOG_ROOT_PATH_CLI = "--log_root_path"

TIMEOUT = 120
LOG_LEVEL = "LogLevel=ERROR"

PLATFORM_NAME = str(sys.platform).lower()


def get_home_dir():
    """
    Get home directory for the current user.

    :return: home directory.
    """
    return os.path.expanduser("~")


def create_path(path):
    """
    Create a path in the local storage.

    :param path: path to be created.
    :return: true if path already exists or was successfully created, false otherwise.
    """
    if os.path.exists(path):
        return True

    try:
        os.makedirs(path)
    except OSError:
        return False

    return True


def popen_communicate(host, command, timeout=TIMEOUT):
    """
    Use Popen library to communicate to a remote server by using ssh protocol.

    :param host: remote host to connect.
    :param command: command to execute on remote server.
    :param timeout: timeout to wait for the process to finish.
    :return: pair stdout, stderr from communicate command, empty string pair, otherwise.
    """
    if host == "" or command == "":
        return "", ""

    ssh = Popen(['ssh', '-o', LOG_LEVEL, host, 'bash'],
                stdin=PIPE, stdout=PIPE, stderr=PIPE)

    timer = Timer(timeout, lambda process: process.kill(), [ssh])

    try:
        timer.start()
        stdout, stderr = ssh.communicate(command)
    finally:
        if not timer.is_alive():
            stderr = "Command '{}' timeout.".format(command)
        timer.cancel()

    return stdout, stderr


def to_seconds(duration):
    """
    Converts time string to second, where string is of form 3h, 5m, 20s etc.

    :param duration: str with numeric value suffixed with h, s, or m.
    :return: seconds represented by the duration as int type.
    :raises ValueError, KeyError: if the string cannot be parsed.
    """

    try:
        units = {"s": 1, "m": 60, "h": 3600}
        return int(float(duration[:-1]) * units[duration[-1]])

    except KeyError:
        raise KeyError("Invalid time unit (must be 's', 'h' or 'm')")
    except (ValueError, NameError):
        raise ValueError("Wrong format. It must be number + time unit (3s or 4m or 5h)")


def is_valid_ip(ip):
    """
    Validate if provided IP is valid.

    :param ip: IP in string format to be validated.
    :return: true if ip is valid, false, otherwise.
    """
    try:
        socket.inet_aton(ip)
    except socket.error:
        return False

    return True


def is_host_accessible(ip):
    """
    Validate host is accessible.

    :param ip: remote host IP.
    :return: true, if host is accessible, false, otherwise.
    """
    with open(os.devnull, "w") as devnull:
        ret_code = Popen(["ping", "-c", "1", ip], stdout=devnull, stderr=devnull).wait()
        return ret_code == 0


def format_time(elapsed_time, time_format="%H:%M:%S"):
    """
    Display a float time according to the format string.

    :param elapsed_time: float time representation.
    :param time_format: format string.
    :return: formatted time.
    """
    return time.strftime(time_format, time.gmtime(elapsed_time))


def get_existing_root_path(destination_path):
    """
    Get the physical path, to perform disk space check on it.

    :param destination_path: the provided path where BUR will store backup data.
    :return: tuple: true, destination path after shrinking, informative message,
    if the destination path or path head exists or tuple: false, if neither the
    destination path nor the path head exist.
    """
    starts_with_dot = str(destination_path)[0] == '.'
    absolute_path = os.path.isabs(destination_path)
    if not starts_with_dot and not absolute_path:
        log_message = "The destination path '{}' is invalid. It should start with '.' or '/'." \
                      ".".format(destination_path)

        return False, destination_path, log_message

    original_bkp_destination = destination_path
    while not os.path.exists(destination_path):
        if destination_path.strip():
            destination_path, _ = os.path.split(destination_path)
        else:
            log_message = "No part of the destination path: {} exists.".format(
                original_bkp_destination)

            return False, destination_path, log_message

    log_message = "The destination path to check after shrinking: {}.".format(destination_path)

    return True, destination_path, log_message


def get_cli_arguments():
    """
    Get and parse console.

    :return: the passed ntwk_bkp CLI arguments in a list.
    """
    sys.argv.pop(0)  # remove the script's name from the argument list.
    provided_args = str(sys.argv)
    return provided_args


def to_bytes(file_size):
    """
    Converts file size string to bytes.

    :param file_size: size fo file.
    :return: file size as integer.
    :raises KeyError, ValueError: if the string can't be parsed.
    """
    try:
        units = {"B": 1, "KB": 1000, "MB": 1000000, "GB": 1000000000}

        if "GB" in file_size or "MB" in file_size or "KB" is file_size:
            return int(float(file_size[:-2]) + units[file_size[-2:]])

        return int(float(file_size[:-1]) + units[file_size[-1]])

    except KeyError:
        raise KeyError("Size Unit invalid (must be 'B', 'KB', 'MB' or 'GB')")
    except (ValueError, NameError):
        raise ValueError("Wrong format. It must be number + szie unit (1B or 2KB or 3MB or 4GB)")

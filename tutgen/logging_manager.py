#!/usr/bin/env python3.11

"""
LoggingManager

A simple logging manager module for configuring and using a logger.

This module provides a `LoggingManager` class, which is designed to simplify
logging configuration and usage. It allows you to easily set the logging level
and provides methods for logging messages at different severity levels.

Example:
    If this module is run as a standalone script, it will demonstrate the
    basic usage of the `LoggingManager` by logging messages at different levels.

Note:
    When using this module in your own code, you can customize the logger name
    and logging level as needed.

Author: Roman Parise
Date: Date Created
"""

# First-party imports
import logging


class LoggingManager:
    """
    A simple logging manager class for configuring and using a logger.

    Args:
        name (str): The name of the logger, which helps identify the source of log messages.
        log_level (int, optional): The logging level to use. Defaults to logging.DEBUG.

    Attributes:
        logger (logging.Logger): The logger instance.

    Methods:
        log_debug(message: str) -> None: Log a debug message.
        log_info(message: str) -> None: Log an info message.
        log_warning(message: str) -> None: Log a warning message.
        log_error(message: str) -> None: Log an error message.
        log_critical(message: str) -> None: Log a critical message.
    """

    def __init__(self, name: str, log_level: int = logging.DEBUG) -> None:
        """
        Initialize the LoggingManager with the specified log level.
        """
        logging.basicConfig(level=log_level)
        self.logger = logging.getLogger(name)

    def log_debug(self, message: str) -> None:
        """
        Log a debug message.

        Args:
            message (str): The message to log.
        """
        self.logger.debug(message)

    def log_info(self, message: str) -> None:
        """
        Log an info message.

        Args:
            message (str): The message to log.
        """
        self.logger.info(message)

    def log_warning(self, message: str) -> None:
        """
        Log a warning message.

        Args:
            message (str): The message to log.
        """
        self.logger.warning(message)

    def log_error(self, message: str) -> None:
        """
        Log an error message.

        Args:
            message (str): The message to log.
        """
        self.logger.error(message)

    def log_critical(self, message: str) -> None:
        """
        Log a critical message.

        Args:
            message (str): The message to log.
        """
        self.logger.critical(message)


if __name__ == "__main__":
    # Example usage
    logger = LoggingManager(__name__)
    logger.log_debug("This is a debug message.")
    logger.log_info("This is an info message.")
    logger.log_warning("This is a warning message.")
    logger.log_error("This is an error message.")
    logger.log_critical("This is a critical message.")

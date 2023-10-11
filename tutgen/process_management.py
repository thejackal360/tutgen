#!/usr/bin/env python3.11

"""
Process Management

This module provides classes for managing subshell processes and executing commands within them.

The `SubshellManager` class is a singleton that manages subshell processes associated with labels.
It provides methods to add, retrieve, and remove subshell processes.

The `SubshellCommand` class is a base class for subshell commands, and it initializes the logger
and the `SubshellManager` instance for managing subshells.

The `StartSubshell` class is a command for starting a subshell process. It sets the PS1 prompt
and adds the subshell to the `SubshellManager`.

The `ExecuteSubshellCommand` class is used to execute commands within a subshell.
It sends the command to the subshell and waits for an optional expected output.
It uses the `SubshellManager` to retrieve the subshell process.

The `TerminateSubshell` class is a command for terminating a subshell. It forcefully terminates
the subshell process and removes it from the `SubshellManager`.

Usage:
    If run as a script, it starts a subshell, executes a series of commands, and then terminates
    the subshell.

Example:
    start_subshell_command = StartSubshell("subshell1")
    start_subshell_command.execute()
    
    commands_to_execute = [
        ('[ -n "$(lsof -ti :8000)" ] && kill -KILL $(lsof -ti :8000)', None),
        ("python3.11 -m http.server &", None),
        (
            'url="http://0.0.0.0:8000/" ; \
                curl -Is "$url" | grep -q "HTTP/1.0 200 OK" && echo "1" || echo "0"',
            "1",
        ),
    ]
    
    for test_command, expected_output in commands_to_execute:
        execute_command = ExecuteSubshellCommand(
            "subshell1", test_command, expect=expected_output
        )
        execute_command.execute()
    
    terminate_subshell_command = TerminateSubshell("subshell1")
    terminate_subshell_command.execute()

Note:
    This script relies on the external library pexpect,
    which needs to be installed to run the script successfully.

Author:
    Roman Parise
"""

# Standard imports
from typing import Optional, Dict

# Third-party imports
import pexpect

# Project imports
from .logging_manager import LoggingManager
from .command import Command


PS1 = "> "


def singleton(cls):
    """
    A decorator that ensures a class has only one instance and provides a way
    to access that instance.

    Args:
        cls: The class to be decorated as a singleton.

    Returns:
        Callable: A function that returns the singleton instance of the decorated class.
    """
    instances = {}

    def get_instance(*args, **kwargs):
        """
        Get the singleton instance of the decorated class, creating it if it doesn't exist.

        Args:
            *args: Positional arguments to pass to the class constructor.
            **kwargs: Keyword arguments to pass to the class constructor.

        Returns:
            object: The singleton instance of the decorated class.
        """
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class SubshellManager:
    """
    Singleton class for managing subshell processes and labels.
    """

    def __init__(self) -> None:
        """
        Initialize the SubshellManager instance.

        Attributes:
            subshell_processes (dict): A dictionary to store subshell processes with labels as keys.
                                      The values are instances of pexpect.spawn.
        """
        self.subshell_processes: Dict[str, pexpect.spawn] = {}

    def add_subshell(self, label: str, subshell_process: pexpect.spawn):
        """
        Add a subshell process to the manager with a given label.

        Args:
            label (str): The label to associate with the subshell process.
            subshell_process (pexpect.spawn): The subshell process to be added.

        Raises:
            ValueError: If a subshell with the same label already exists in the manager.
        """
        if label in self.subshell_processes:
            raise ValueError(f"A subshell with label '{label}' already exists.")
        self.subshell_processes[label] = subshell_process

    def get_subshell(self, label: str) -> Optional[pexpect.spawn]:
        """
        Retrieve a subshell process by its label.

        Args:
            label (str): The label associated with the subshell process.

        Returns:
            pexpect.spawn or None: The subshell process corresponding to the label,
                                   or None if no such label exists.
        """
        return self.subshell_processes.get(label)

    def remove_subshell(self, label: str):
        """
        Remove a subshell process from the manager by its label.

        Args:
            label (str): The label associated with the subshell process.
        """
        del self.subshell_processes[label]


class SubshellCommand(Command):
    """
    Base class for subshell commands.
    """

    def __init__(self, subshell_label: str):
        self.subshell_label = subshell_label
        self.logger = LoggingManager(__name__).logger
        assert self.logger, "Logger is not initialized."
        self.subshell_manager = SubshellManager()
        assert self.subshell_manager, "Subshell manager is not initialized."


class StartSubshell(SubshellCommand):
    """
    Class for starting a subshell process.
    """

    def execute(self) -> None:
        subshell_command = "bash"
        subshell_process = pexpect.spawn(subshell_command)
        assert subshell_process, "Could not create subshell process"
        subshell_process.sendline(f"PS1={repr(PS1)}")
        subshell_process.expect(PS1)
        self.logger.debug("Subshell started.")
        try:
            self.subshell_manager.add_subshell(self.subshell_label, subshell_process)
        except ValueError as ve:
            self.logger.error(
                "Failed to add subshell '%s'. Subshell with the same label already exists: %s",
                self.subshell_label,
                ve,
            )


class ExecuteSubshellCommand(SubshellCommand):
    """
    Class for executing commands in a subshell.
    """

    def __init__(
        self,
        label: str,
        command: str,
        expect: Optional[str] = None,
    ):
        super().__init__(label)
        self.command = command
        self.expect = expect

    def execute(self):
        try:
            subshell_process = self.subshell_manager.get_subshell(self.subshell_label)
        except KeyError as ke:
            self.logger.debug(
                "No subshell named '%s' is running: %s", self.subshell_label, ke
            )
            return

        assert subshell_process, "No subshell is running."

        self.logger.debug("Executing command...")
        subshell_process.sendline(self.command)
        if self.expect:
            self.logger.debug("Waiting for %s", repr(self.expect))
            subshell_process.expect(self.expect)
            self.logger.debug("Output: %s", subshell_process.before)
        self.logger.debug("Waiting for PS1=%s", repr(PS1))
        subshell_process.expect(PS1)
        self.logger.debug("Successfully executed command: %s", self.command)


class TerminateSubshell(SubshellCommand):
    """
    Class for terminating the subshell process.
    """

    def execute(self):
        try:
            subshell_process = self.subshell_manager.get_subshell(self.subshell_label)
        except KeyError as ke:
            self.logger.debug(
                "No subshell named '%s' is running: %s", self.subshell_label, ke
            )
            return

        assert subshell_process, "No subshell is running."

        self.logger.debug("Terminating subshell...")
        subshell_process.terminate(force=True)
        subshell_process.wait()
        self.logger.debug("Subshell terminated.")

        try:
            SubshellManager().remove_subshell(self.subshell_label)
        except KeyError as ke:
            self.logger.debug(
                "No subshell named '%s' is running: %s", self.subshell_label, ke
            )


if __name__ == "__main__":
    # Starting subshell
    start_subshell_command = StartSubshell("subshell1")
    start_subshell_command.execute()

    commands_to_execute = [
        ('[ -n "$(lsof -ti :8000)" ] && kill -KILL $(lsof -ti :8000)', None),
        ("python3.11 -m http.server &", None),
        (
            'url="http://0.0.0.0:8000/" ; \
                curl -Is "$url" | grep -q "HTTP/1.0 200 OK" && echo "1" || echo "0"',
            "1",
        ),
    ]

    # Executing commands in subshell
    for test_command, expected_output in commands_to_execute:
        execute_command = ExecuteSubshellCommand(
            "subshell1", test_command, expect=expected_output
        )
        execute_command.execute()

    # Terminating subshell
    terminate_subshell_command = TerminateSubshell("subshell1")
    terminate_subshell_command.execute()

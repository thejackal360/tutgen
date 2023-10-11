#!/usr/bin/env python3.11

"""
Command

This module defines a set of command classes for managing various processes related to video
creation.

The `Command` class is an abstract base class for command objects, providing a common interface for
executing different types of commands.

The `CreateClipCommand` class is a command for creating a video clip with narration. It
allows specifying a text-to-speech (TTS) strategy to use for generating audio narration.
This class is part of the larger process management system but specifically handles the
generation of video clips with narration.

Please refer to the specific command classes and their docstrings for details on their usage.

Note:
    This script relies on the external library moviepy,
    which needs to be installed to run the script successfully.

Author:
    Roman Parise
"""

# First-party imports
from abc import ABC, abstractmethod
from os import environ
from typing import Optional

# Third-party imports
from moviepy.editor import AudioFileClip

# Project imports
from .logging_manager import LoggingManager
from .video_receiver import VideoReceiver
from .tts_strategy import GoogleTTSStrategy, TTSStrategy, VoicemakerTTSStrategy


class Command(ABC):
    """
    An abstract base class for command objects.
    """

    @abstractmethod
    def execute(self):
        """
        Execute the command.
        """


class CreateClipCommand(Command):
    """
    A command to create a video clip with narration.
    """

    def __init__(self, tts_strategy: Optional[TTSStrategy] = None) -> None:
        """
        Initialize the CreateClipCommand.

        Args:
            tts_strategy (Optional[TTSStrategy]): The text-to-speech strategy to use.
        """
        super().__init__()
        self.receiver = None
        self.final_video_obj = None
        self.tts_strategy: Optional[TTSStrategy] = None
        self.logger = LoggingManager(__name__).logger
        if tts_strategy is None:
            for key in environ:
                if key == "VOICEMAKER_TOKEN":
                    self.tts_strategy = VoicemakerTTSStrategy()
                    self.logger.debug("Using Voicemaker text-to-speech")
                    break
        else:
            self.tts_strategy = tts_strategy
        if self.tts_strategy is None:
            self.tts_strategy = GoogleTTSStrategy()
            self.logger.debug("Using Google text-to-speech")
        assert self.tts_strategy, "No TTS strategy set."

    def set_receiver(self, receiver: VideoReceiver):
        """
        Set the video receiver for the command.

        Args:
            receiver (VideoReceiver): The video receiver.
        """
        self.receiver = receiver

    def create_narrator_audio(self, text: str) -> AudioFileClip:
        """
        Create a temporary MP3 file from the given text.

        Args:
            text (str): The text to convert to audio.

        Returns:
            AudioFileClip: The created temporary audio clip.
        """
        self.logger.debug("Creating temporary MP3...")

        assert self.tts_strategy, "No TTS strategy set."
        return_audio = self.tts_strategy.generate_audio(text)  # type: ignore
        assert return_audio, "Failed to generate audio."

        self.logger.debug("return_audio length = %.2f", return_audio.duration)

        return return_audio

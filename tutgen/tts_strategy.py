#!/usr/bin/env python3.11

"""
Text-to-Speech Strategies

This module provides different strategies for generating audio from text using third-party
libraries.
"""

# First-party imports
from abc import ABC, abstractmethod
from os import environ
from tempfile import NamedTemporaryFile

# Third-party imports
from voicemaker import Voicemaker
from gtts import gTTS
from moviepy.editor import AudioFileClip


class TTSStrategy(ABC):
    """
    Abstract base class for text-to-speech strategies.

    Subclasses must implement the `generate_audio` method.
    """

    @abstractmethod
    def generate_audio(self, text: str) -> AudioFileClip:
        """
        Generate audio from text and return an AudioFileClip.

        Args:
            text (str): The text to convert to audio.

        Returns:
            AudioFileClip: An audio clip representing the generated audio.
        """


class GoogleTTSStrategy(TTSStrategy):
    """
    Text-to-speech strategy using the gTTS library.
    """

    def generate_audio(self, text: str) -> AudioFileClip:
        """
        Generate audio from text using gTTS and return an AudioFileClip.

        Args:
            text (str): The text to convert to audio.

        Returns:
            AudioFileClip: An audio clip representing the generated audio.
        """
        with NamedTemporaryFile(suffix=".mp3", delete=False) as temp_mp3:
            tts = gTTS(text=text, lang="en")
            tts.save(temp_mp3.name)
            return AudioFileClip(temp_mp3.name)


class VoicemakerTTSStrategy(TTSStrategy):
    """
    Text-to-speech strategy using the Voicemaker library.
    """

    def generate_audio(self, text: str) -> AudioFileClip:
        """
        Generate audio from text using Voicemaker and return an AudioFileClip.

        Args:
            text (str): The text to convert to audio.

        Returns:
            AudioFileClip: An audio clip representing the generated audio.
        """
        vm_handler = Voicemaker()
        token = environ["VOICEMAKER_TOKEN"]
        vm_handler.set_token(token)
        with NamedTemporaryFile(suffix=".mp3", delete=False) as temp_mp3:
            vm_handler.generate_audio_to_file(temp_mp3.name, text)
            return AudioFileClip(temp_mp3.name)

#!/usr/bin/env python3.11

"""
Code Animation Generation

This script defines a Python class called `CodeAnimationGenerator`, which is
used for generating code animation videos by combining code snippets with audio
narration. The primary purpose of this script is to automate the process of creating
instructional videos that feature code demonstrations.

The `CodeAnimationGenerator` class takes a list of text mappings, intro and
outro code snippets, and various optional parameters as input. It calculates
the timing for narration and code typing, concatenates the narrator's audio clips
with pauses, and generates a code animation video. The resulting video is added
to a specified receiver for further processing.

Usage:
    When executed as a standalone script, this file demonstrates the usage of
    the `CodeAnimationGenerator` class by generating a code animation video based
    on provided input data and saving the final video to a file.

Example:
    ```
    text_mapping = [
        {
            "narration_text": "This is narration 1.",
            "code_text": "echo $BLAH",
        }
    ]
    INTRO_CODE = "export BLAH=1; clear"
    OUTRO_CODE = "clear"

    receiver = VideoReceiver()
    FINAL_VIDEO_NAME = "final_video.mp4"

    animation_generator = CodeAnimationGenerator(text_mapping, INTRO_CODE, OUTRO_CODE)
    animation_generator.set_receiver(receiver)
    animation_generator.execute()
    receiver.dump_file(FINAL_VIDEO_NAME)

    print(f"Animation video saved to {FINAL_VIDEO_NAME}")
    ```

Note:
    This script relies on external libraries such as MoviePy and Mako,
    which need to be installed to run the script successfully.

Author:
    Roman Parise
"""

# First-party imports
import os
import subprocess
import tempfile
from typing import Any, Dict, List

# Third-party imports
from mako.template import Template
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_audioclips
import pkg_resources
from pydub import AudioSegment

# Project imports
from .logging_manager import LoggingManager
from .video_receiver import VideoReceiver
from .command import CreateClipCommand

DEFAULT_DELAY = 500  # Default delay in milliseconds


class CodeAnimationGenerator(CreateClipCommand):
    """
    Class for generating code animation videos by combining narration and code snippets.

    This class allows you to create code animation videos with specified timing and narration.
    It takes a list of dictionaries, each containing narration and code text, and animates
    them in the order provided. You can also specify intro and outro code snippets, typing
    speed, theme, and video dimensions.

    Args:
        text_mapping (List[Dict[str, Any]]): A list of dictionaries, where each dictionary
            represents a pair of narration and code text to be animated. Each dictionary
            should have the keys "narration_text" (str) and "code_text" (str or List[str]).
        intro_code (str): Code snippet to be displayed at the beginning of the animation.
        outro_code (str): Code snippet to be displayed at the end of the animation.
        typing_speed_ms (int, optional): Typing speed in milliseconds for code animation
            (default is 75).
        theme (str, optional): VHS theme for the animation effect (default is "Cobalt Neon").
        width (int, optional): Width of the terminal window in pixels (default is 1920).
        height (int, optional): Height of the terminal window in pixels (default is 1080).
        **kwargs: Additional keyword arguments for future extensions.

    Note:
        The `text_mapping` parameter should be a list of dictionaries, where each dictionary
        contains narration text (a string) and code text (either a string or a list of strings).
        Narration text represents the spoken content for a particular code demonstration, and
        code text represents the code to be animated.

    Example:
        ```
        text_mapping = [
            {
                "narration_text": "This is narration 1.",
                "code_text": "echo $BLAH",
            },
            {
                "narration_text": "This is narration 2.",
                "code_text": [
                    "for i in range(5):",
                    "    print(i)",
                ],
            },
        ]
        INTRO_CODE = "export BLAH=1; clear"
        OUTRO_CODE = "clear"

        animation_generator = CodeAnimationGenerator(
            text_mapping, INTRO_CODE, OUTRO_CODE, typing_speed_ms=100, theme="Cobalt Neon",
            width=1280, height=720
        )
        ```
    """

    def __init__(
        self,
        text_mapping: List[Dict[str, Any]],
        intro_code: str,
        outro_code: str,
        *args,
        typing_speed_ms: int = 75,
        theme: str = "Cobalt Neon",
        width: int = 1920,
        height: int = 1080,
        **kwargs,
    ) -> None:
        """
        Initialize the CodeAnimationGenerator.
        """
        super().__init__(*args, **kwargs)
        self.text_mapping = text_mapping
        self.intro_code = intro_code
        self.outro_code = outro_code
        self.typing_speed_ms = typing_speed_ms
        self.theme = theme
        self.width = width
        self.height = height
        self.logger = LoggingManager(__name__).logger

    def calculate_timing_info(self) -> List[Dict[str, Any]]:
        """
        Calculate waiting times and durations for multiple text pairs of narration and code.

        Returns:
            List[Dict[str, any]]: A list of dictionaries, each containing the following information:
                - "time_to_wait_for_typing" (int): Time to wait for typing in milliseconds.
                - "time_to_wait_for_narration" (int): Time to wait for narration in milliseconds.
                - "narrator_audio" (AudioFileClip): Narration MP3 file clip.
                - "narration_text" (str): The provided narration text.
                - "code_text" (str): The provided code text.
        """
        timing_info = []

        for item in self.text_mapping:
            narration_text = item["narration_text"]
            code_text = "\n".join(item["code_text"])

            # Create a temporary MP3 for narration
            narrator_audio = self.create_narrator_audio(narration_text)
            assert narrator_audio, "Failed to create narrator audio"

            # Calculate the duration of the code in milliseconds
            code_duration_ms = self.typing_speed_ms * len(code_text)

            # Get the duration of the narration MP3 in milliseconds
            narration_duration_ms = narrator_audio.duration * 1000

            # Calculate waiting times
            time_to_wait_for_typing = max(0, code_duration_ms - narration_duration_ms)
            time_to_wait_for_narration = max(
                0, narration_duration_ms - code_duration_ms
            )

            # Log debug information
            log_message = "Time to wait for typing: %d ms"
            self.logger.debug(log_message, time_to_wait_for_typing)
            log_message = "Time to wait for narration: %d ms"
            self.logger.debug(log_message, time_to_wait_for_narration)

            # Append the results to the timing_info list
            timing_info.append(
                {
                    "time_to_wait_for_typing": time_to_wait_for_typing,
                    "time_to_wait_for_narration": time_to_wait_for_narration,
                    "narrator_audio": narrator_audio,
                    "narration_text": narration_text,
                    "code_text": code_text,
                }
            )

        return timing_info

    def concatenate_narrator_clips(
        self, timing_dicts: List[Dict[str, Any]]
    ) -> AudioFileClip | None:
        """
        Concatenate narrator audio clips with specified pauses in between.

        Args:
            timing_dicts (List[Dict[str, Any]]): A list of timing dictionaries, where each
                dictionary contains the following keys:
                - "narrator_audio": An AudioFileClip representing the narrator's audio clip.
                - "time_to_wait_for_typing": Time in seconds to wait before appending the next clip.

        Returns:
            AudioFileClip | None: The concatenated audio clip, or None if the input list is empty.

        Note:
            This function uses the tempfile library to create temporary audio files for processing
            and cleans them up afterward.
        """
        # Generate input dictionary
        narrator_audio_dict: Dict[AudioFileClip, int] = {
            timing_dict["narrator_audio"]: timing_dict["time_to_wait_for_typing"]
            for timing_dict in timing_dicts
        }

        # Stitch the narration audio segments
        final_audio_clip_list = []
        temp_files = []

        for narrator_audio, time_to_wait in narrator_audio_dict.items():
            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                narrator_audio_path = temp_file.name

                # Write audio content to the temporary file
                self.logger.debug("Writing audio to %s", narrator_audio_path)
                narrator_audio.write_audiofile(narrator_audio_path)
                audio_segment = AudioSegment.from_mp3(narrator_audio_path)

                one_second_of_silence = AudioSegment.silent(
                    duration=DEFAULT_DELAY + time_to_wait
                )
                audio_with_pause = audio_segment + one_second_of_silence

                # Export the modified audio to the temporary file
                self.logger.debug("Exporting modified audio to %s", narrator_audio_path)
                audio_with_pause.export(narrator_audio_path, format="mp3")

                # Create an AudioFileClip from the temporary file
                self.logger.debug("Creating AudioFileClip from %s", narrator_audio_path)
                narrator_audio = AudioFileClip(narrator_audio_path)
                final_audio_clip_list.append(narrator_audio)

                # Store the temporary file for cleanup
                temp_files.append(narrator_audio_path)

        final_audio_clip = concatenate_audioclips(final_audio_clip_list)

        # Clean up temporary files
        for temp_file in temp_files:
            self.logger.debug("Cleaning up temporary file: %s", temp_file)
            os.remove(temp_file)

        return final_audio_clip

    def format_tape_file(self, input_dict: Dict[str, Any]) -> List[str]:
        """
        Format a tape file based on the provided input data.

        Args:
            input_dict (Dict[str, Any]): A dictionary containing input data.

        Returns:
            List[str]: A list containing the names of the temporary tape and MP4 files.
        """
        # Create a Mako template object
        template_path = pkg_resources.resource_filename("tutgen", "animation.template")
        template = Template(filename=template_path)

        with tempfile.NamedTemporaryFile(
            suffix=".tape", mode="w", delete=False
        ) as temp_tape:
            temp_tape_name, _ = os.path.splitext(temp_tape.name)
            temp_mp4_name = temp_tape_name + ".mp4"

            # Render the template with the provided data
            rendered_content = template.render(
                animation_file_path=temp_mp4_name,
                typing_speed_ms=self.typing_speed_ms,
                width=self.width,
                height=self.height,
                intro_code=self.intro_code,
                outro_code=self.outro_code,
                input_dict=input_dict,
                DEFAULT_DELAY=DEFAULT_DELAY,
            )
            temp_tape.write(rendered_content)

            self.logger.debug(
                "Created tape file: %s, MP4 file: %s",
                temp_tape.name,
                temp_mp4_name,
            )

            return [temp_tape.name, temp_mp4_name]

    def execute(self):
        """
        Generate a code animation video by combining narration and code
        snippets according to specified timing.

        This function calculates the timing for narration and code typing,
        concatenates the narrator's audio clips with pauses, and generates
        a code animation video. It uses the provided text_mapping, intro_code,
        and outro_code to create the animation.

        Raises:
            AssertionError: If any critical step in the execution fails.

        Note:
            The generated animation video is added to the receiver.

        Example Usage:
            # Sample input data
            text_mapping = [
                {
                    "narration_text": "This is narration 1.",
                    "code_text": "echo $BLAH",
                }
            ]
            INTRO_CODE = "export BLAH=1; clear"
            OUTRO_CODE = "clear"

            # Initialize the CodeAnimationGenerator
            animation_generator = CodeAnimationGenerator(text_mapping, INTRO_CODE, OUTRO_CODE)

            # Generate the animation video
            animation_generator.set_receiver(receiver)
            animation_generator.execute()
            receiver.dump_file(FINAL_VIDEO_NAME)
        """
        # Calculate timing dictionaries
        timing_dicts = self.calculate_timing_info()

        audio = self.concatenate_narrator_clips(timing_dicts)
        assert audio, "Failed to concatenate narrator audio clips"
        audio_duration = audio.duration

        # Create a new dictionary for code text and narration timing
        new_dict: Dict[str, int] = {
            d["code_text"]: d["time_to_wait_for_narration"] for d in timing_dicts
        }

        log_message = "Generated new_dict: %s, intro_code: %s, outro_code: %s"
        self.logger.debug(log_message, new_dict, self.intro_code, self.outro_code)

        temp_tape_name, temp_mp4_name = self.format_tape_file(new_dict)

        subprocess.run(
            f"vhs {temp_tape_name}",
            shell=True,
            check=True,
        )

        video = VideoFileClip(temp_mp4_name)

        assert audio
        assert video

        video.audio = audio
        video.duration = audio_duration

        assert self.receiver

        self.receiver.add_clip(video)


if __name__ == "__main__":
    receiver = VideoReceiver()
    FINAL_VIDEO_NAME = "final_video.mp4"

    # Sample input data
    example_text_mapping = [
        {
            "narration_text": "This is narration 1.",
            "code_text": "echo $BLAH",
        }
    ]
    INTRO_CODE = "export BLAH=1; clear"
    OUTRO_CODE = "clear"

    # Initialize the CodeAnimationGenerator
    animation_generator = CodeAnimationGenerator(
        example_text_mapping, INTRO_CODE, OUTRO_CODE
    )

    # Generate the animation video
    animation_generator.set_receiver(receiver)
    animation_generator.execute()
    receiver.dump_file(FINAL_VIDEO_NAME)

    print(f"Animation video saved to {FINAL_VIDEO_NAME}")

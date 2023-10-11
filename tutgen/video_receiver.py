#!/usr/bin/env python3.11

"""
VideoReceiver

This module defines a VideoReceiver class that demonstrates the Command design pattern.
The VideoReceiver class receives and concatenates video clips, representing commands that can
be executed. It encapsulates these commands as objects, allowing for flexible and
extensible video processing operations.

The VideoReceiver class provides methods for adding video clips and dumping the final
result to an output file.

Note:
    This script relies on the external library moviepy,
    which needs to be installed to run the script successfully.

Author:
    Roman Parise
"""

# Third-party imports
from moviepy.editor import VideoFileClip, concatenate_videoclips

# Project imports
from .logging_manager import LoggingManager


class VideoReceiver:
    """
    Class for receiving and concatenating video clips.
    """

    def __init__(self):
        """
        Initializes a new VideoReceiver.

        Attributes:
            final_video (VideoFileClip or None): The final concatenated video clip.
            logger (Logger): The logger for this class.
        """
        self.final_video = None
        self.logger = LoggingManager(__name__).logger

    def add_clip(self, clip: VideoFileClip):
        """
        Concatenates the current VideoFileClip with the clip provided as an argument
        and overwrites the current VideoFileClip.

        Args:
            clip (VideoFileClip): The VideoFileClip to be concatenated.
        """
        assert clip.audio, "Audio is required for video concatenation."
        assert (
            clip.duration == clip.audio.duration
        ), "Audio and video durations must match."
        if self.final_video is None:
            self.logger.debug("Adding first clip!")
            self.final_video = clip
        else:
            self.logger.debug("Adding next clip!")
            assert self.final_video, "self.final_video is undefined."
            assert self.final_video.audio, "self.final_video has no audio."
            check_video_duration = self.final_video.duration + clip.duration
            check_audio_duration = self.final_video.audio.duration + clip.audio.duration
            self.final_video = concatenate_videoclips([self.final_video, clip])
            assert self.final_video, "self.final_video is undefined."
            assert self.final_video.audio, "self.final_video has no audio."
            assert (
                check_video_duration == self.final_video.duration
            ), "Video durations do not match."
            assert (
                check_video_duration == check_audio_duration
            ), "Video and audio durations do not match."
            assert (
                check_audio_duration == self.final_video.audio.duration
            ), "Audio durations do not match."

    def dump_file(self, output_filename="output.mp4"):
        """
        Saves the full movie to an mp4 file using write_videofile.

        Args:
            output_filename (str): The name of the output video file.
        """
        if self.final_video is not None:
            self.final_video.write_videofile(output_filename)
        else:
            self.logger.debug("No clips to dump. Please add clips first.")

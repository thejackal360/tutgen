#!/usr/bin/env python3.11

"""
Browser Interaction and Recording

This script defines a Python class called `BrowserInteraction`, which is used for
interacting with a web browser, recording activities, and combining them with audio
narration to create a video. The primary purpose of this script is to automate the
process of capturing web browser interactions and generating instructional videos.

The `BrowserInteraction` class takes a URL to navigate to, a narration text, and an
optional viewport size as input. It utilizes the Playwright library to control a
headless Chromium browser, record browser activities, and capture video content.
The generated video is then combined with audio narration to create a final
instructional video.

Usage:
    When executed as a standalone script, this file demonstrates the usage of the
    `BrowserInteraction` class by recording interactions with a specified URL and
    saving the resulting video to a file.

Example:
    ```
    TEST_URL = "https://www.google.com"
    browser_interaction = BrowserInteraction(TEST_URL, "This is a narrator test")
    browser_interaction.execute()
    ```

Note:
    This script relies on external libraries such as MoviePy and Playwright, which
    need to be installed to run the script successfully.

Author:
    Roman Parise
"""

# First-party imports
from typing import Optional

# Third-party imports
from moviepy.editor import VideoFileClip
from playwright.sync_api import sync_playwright, ViewportSize

# Project imports
from .command import CreateClipCommand
from .video_receiver import VideoReceiver
from .logging_manager import LoggingManager


class BrowserInteraction(CreateClipCommand):
    """
    A class for interacting with a web browser and recording activities.

    Args:
        url (str): The URL to navigate to.
        text (str): The text for narration.
        viewport (Optional[ViewportSize]): A dictionary specifying the viewport size
                                  (default: {"width": 1920, "height": 1080}).
    """

    def __init__(
        self,
        url: str,
        text: str,
        *args,
        viewport: Optional[ViewportSize] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.url = url
        self.browser = None
        self.context = None
        self.page = None
        self.logger = LoggingManager(__name__).logger
        self._sync_playwright = sync_playwright().start()
        if viewport is None:
            self.viewport = ViewportSize(width=1920, height=1080)
        else:
            self.viewport = viewport
        self.check_viewport()
        self.text = text

    def check_viewport(self):
        """
        Check the validity of the viewport attribute.

        This function verifies that the `self.viewport` attribute exists and contains
        both 'width' and 'height' keys, ensuring that it represents a valid viewport
        configuration.

        Raises:
            AssertionError: If the `self.viewport` attribute is missing, doesn't
                            have exactly two keys, or lacks either 'width' or 'height'.

        Example:
            # Valid viewport configuration
            self.viewport = {"width": 800, "height": 600}
            self.check_viewport()  # No AssertionError raised

            # Invalid viewport configurations
            self.viewport = None
            self.check_viewport()  # AssertionError raised

            self.viewport = {"width": 1024}
            self.check_viewport()  # AssertionError raised

            self.viewport = {"height": 768}
            self.check_viewport()  # AssertionError raised
        """
        assert self.viewport, "self.viewport is None"
        assert len(self.viewport.keys()) == 2, "self.viewport is not a valid viewport"
        assert "width" in self.viewport.keys(), "self.viewport is missing 'width'"
        assert "height" in self.viewport.keys(), "self.viewport is missing 'height'"

    def start_browser(self):
        """
        Launches a headless Chromium browser and returns a new page.

        Returns:
            page (playwright.sync_api.Page): The new browser page.
        """
        self.browser = self._sync_playwright.chromium.launch(headless=True)
        self.context = self.browser.new_context(
            record_video_dir="/tmp",
            viewport=self.viewport,
            screen=self.viewport,
            record_video_size=self.viewport,
            device_scale_factor=2.0,
            is_mobile=False,
            has_touch=False,
            color_scheme="light",
            record_har_mode="full",
            record_har_content="embed",
        )
        self.page = self.context.new_page()

    def execute(self):
        """
        Records browser activities for the specified URL and time period.
        """

        # Start the browser
        self.start_browser()
        assert self.browser, "Browser is None"
        assert self.context, "Context is None"
        assert self.page, "Page is None"
        self.logger.debug("Browser started.")

        # Navigate to the URL
        self.page.goto(self.url, wait_until="domcontentloaded")
        self.logger.debug("Navigated to URL: %s", self.url)

        # Check if narration text is provided and create temporary MP3 audio
        self.logger.debug("Creating MP3 audio for narration...")
        narrator_audio = self.create_narrator_audio(self.text)
        assert narrator_audio, "Could not create narrator audio"
        self.logger.debug("Narrator audio created!")

        # Close the browser
        self.context.close()
        self.logger.debug("Context closed.")
        self.browser.close()
        self.logger.debug("Browser closed.")

        # Combine the video and audio
        playwright_video_obj = self.page.video
        assert playwright_video_obj, "No video found"
        video_path = playwright_video_obj.path()
        video = VideoFileClip(video_path)

        self.logger.debug(
            "Adding audio to the video..."
        )  # Debug statement for audio processing
        # Add a 1 second silence at the end of the video
        video.audio = narrator_audio
        video.duration = narrator_audio.duration

        self.logger.debug(
            "Writing the final video file..."
        )  # Debug statement for video processing

        assert self.receiver, "Receiver is None"
        self.receiver.add_clip(video)


if __name__ == "__main__":
    receiver = VideoReceiver()
    FINAL_VIDEO_NAME = "final_video.mp4"

    # Test the BrowserInteraction class
    TEST_URL = "https://www.google.com"

    browser_interaction = BrowserInteraction(
        TEST_URL,
        "This is a narrator test",
    )
    browser_interaction.set_receiver(receiver)
    browser_interaction.execute()
    receiver.dump_file(FINAL_VIDEO_NAME)

    print(f"Animation video saved to {FINAL_VIDEO_NAME}")

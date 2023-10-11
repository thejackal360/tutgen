#!/usr/bin/env python3.11

"""
Video Command Invoker (Command Design Pattern)

This Python script defines the `VideoInvoker` class, a central component in the Command
design pattern for executing video-related commands. It manages the video generation
process and serves as the invoker in the pattern.

The `VideoInvoker` class provides methods for executing video commands, including
starting subshells, running code animations, and interacting with a web browser to
create instructional videos. It collaborates with classes like `CodeAnimationGenerator`,
`BrowserInteraction`, and `ProcessManagement` to record video segments and assemble
them into a final video.

Usage:
    To create and execute a sequence of video commands, initialize an instance of
    the `VideoInvoker` class and use its methods. This class works with command objects
    that encapsulate specific actions and parameters.

Example:
    ```python
    invoker = VideoInvoker()

    # Create command objects
    animation_generator = CodeAnimationGenerator(text_mapping, INTRO_CODE, OUTRO_CODE)
    start_subshell = StartSubshell("server_subshell")
    run_server = ExecuteSubshellCommand("server_subshell", "python3.11 test_server.py &")
    browser_interaction = BrowserInteraction("http://localhost:5000/", "Webpage narration")
    kill_subshell = TerminateSubshell("server_subshell")

    # Execute command objects
    invoker.execute_command(animation_generator)
    invoker.execute_command(start_subshell)
    invoker.execute_command(run_server)
    invoker.execute_command(browser_interaction)
    invoker.execute_command(kill_subshell)

    FINAL_VIDEO_NAME = "final_video.mp4"
    invoker.dump_file(FINAL_VIDEO_NAME)
    ```

Author:
    Roman Parise
"""

# Project imports
from .video_receiver import VideoReceiver
from .command import Command, CreateClipCommand
from .code_animation_generator import CodeAnimationGenerator
from .browser_interaction import BrowserInteraction
from .process_management import StartSubshell, ExecuteSubshellCommand, TerminateSubshell


class VideoInvoker:
    """
    A class that invokes video-related commands.
    """

    def __init__(self):
        """
        Initializes a VideoInvoker with a VideoReceiver.
        """
        self.video_receiver = VideoReceiver()

    def execute_command(self, command: Command):
        """
        Executes a given command.

        Args:
            command (Command): The command to execute.
        """
        if isinstance(command, CreateClipCommand):
            command.set_receiver(self.video_receiver)
            command.execute()
        else:
            command.execute()

    def dump_file(self, output_filename: str = "output.mp4"):
        """
        Saves the full movie to an mp4 file using write_videofile.

        Args:
            output_filename (str): The name of the output video file.
        """
        self.video_receiver.dump_file(output_filename)


if __name__ == "__main__":
    invoker = VideoInvoker()

    # Write Flask server
    text_mapping = [
        {
            "narration_text": "First, we're going to make the necessary imports.",
            "code_text": """
vim test_server.py
ifrom flask import Flask

""",
        },
        {
            "narration_text": "Then, we're going to instantiate our webapp and create a route.",
            "code_text": """
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

""",
        },
        {
            "narration_text": "Finally, we'll run the app.",
            "code_text": """
if __name__ == '__main__':
    app.run()

""",
        },
        {
            "narration_text": "We're now going to run the server.",
            "code_text": """
<Escape>
:x

""",
        },
    ]
    INTRO_CODE = "rm -rf test_server.py; clear"
    OUTRO_CODE = "rm -rf test_server.py; clear"

    # Initialize the CodeAnimationGenerator
    animation_generator = CodeAnimationGenerator(text_mapping, INTRO_CODE, OUTRO_CODE)
    invoker.execute_command(animation_generator)

    # Start subshell for server
    start_subshell = StartSubshell("server_subshell")
    invoker.execute_command(start_subshell)

    # Run server in subshell
    run_server = ExecuteSubshellCommand(
        "server_subshell", "python3.11 test_server.py &"
    )
    invoker.execute_command(run_server)

    # Test the BrowserInteraction class
    browser_interaction = BrowserInteraction(
        "http://localhost:5000/",
        "As you can see, the webpage is rendered as expected.",
    )
    invoker.execute_command(browser_interaction)

    # Kill subshell
    kill_subshell = TerminateSubshell("server_subshell")
    invoker.execute_command(kill_subshell)

    FINAL_VIDEO_NAME = "final_video.mp4"
    invoker.dump_file(FINAL_VIDEO_NAME)
    print(f"Animation video saved to {FINAL_VIDEO_NAME}")

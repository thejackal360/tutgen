#!/usr/bin/env python3.11

"""
This script is used to generate a video with code animations and interactions
from a JSON configuration file.

It imports several modules and classes to handle different aspects of the video generation process.
"""

# First-party imports
import argparse
from json import load as json_load
from subprocess import run

# Project imports
from .code_animation_generator import CodeAnimationGenerator
from .browser_interaction import BrowserInteraction
from .process_management import StartSubshell, ExecuteSubshellCommand, TerminateSubshell
from .video_invoker import VideoInvoker


def main():
    """
    Parse command-line arguments, read the JSON configuration file,
    and generate a video with code animations and interactions.

    The function performs the following steps:
    1. Parse the command-line arguments to get the path to the JSON configuration file.
    2. Read the JSON configuration file to extract information about the video.
    3. Execute the specified commands, including code animations and browser interactions.
    4. Save the generated animation video to a file.

    The configuration file should define various commands to be executed,
    along with intro and outro code segments.
    The resulting animation video is saved with the specified or default name.

    Usage:
    python script.py config.json

    Args:
        json_file (str): Path to the JSON configuration file.

    Example:
    python script.py config.json
    """
    parser = argparse.ArgumentParser(
        description="""Generate a video with code animations and
               interactions from a JSON configuration file."""
    )
    parser.add_argument(
        "json_file", type=str, help="Path to the JSON configuration file."
    )
    args = parser.parse_args()
    with open(args.json_file, "r", encoding="utf-8") as json_file:
        config = json_load(json_file)

    commands = config.get("commands", {})
    intro_code = "\n".join(config.get("intro_outro", {}).get("intro_code", []))
    outro_code = "\n".join(config.get("intro_outro", {}).get("outro_code", []))
    invoker = VideoInvoker()

    run(intro_code, check=True, shell=True)

    for command in commands:
        if command["type"] == "StartSubshell":
            start_subshell = StartSubshell(command["name"])
            invoker.execute_command(start_subshell)
        elif command["type"] == "ExecuteSubshell":
            execute_subshell = ExecuteSubshellCommand(
                command["subshell_name"], command["command"]
            )
            invoker.execute_command(execute_subshell)
        elif command["type"] == "BrowserInteraction":
            browser_interaction = BrowserInteraction(command["url"], command["text"])
            invoker.execute_command(browser_interaction)
        elif command["type"] == "TerminateSubshell":
            terminate_subshell = TerminateSubshell(command["name"])
            invoker.execute_command(terminate_subshell)
        elif command["type"] == "CodeAnimationGenerator":
            text_mapping = command["text_mapping"]
            code_animation_generator = CodeAnimationGenerator(
                text_mapping, intro_code, outro_code
            )
            invoker.execute_command(code_animation_generator)

    run(outro_code, check=True, shell=True)

    output_video_name = config.get("output_video_name", "final_video.mp4")
    invoker.dump_file(output_video_name)
    print(f"Animation video saved to {output_video_name}")


if __name__ == "__main__":
    main()

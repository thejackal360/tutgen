tutgen is a tool for generating coding tutorials from a JSON file. A sample file called test.json is provided in the repo:

```
{
    "commands":
        [
            {"type" : "CodeAnimationGenerator",
             "text_mapping" : [
                {
                    "narration_text": "First, we're going to make the necessary imports.",
                    "code_text": ["vim test_server.py",
                                  "iimport flask",
                                  "app = flask.Flask(__name__)"]
                },
                {
                    "narration_text": "Then, we're going to instantiate our webapp and create a route.",
                    "code_text": ["@app.route('/')",
                                  "def hello():",
                                  "    return 'Hello World!'"]
                },
                {
                    "narration_text": "Finally, we'll run the app.",
                    "code_text": ["if __name__ == '__main__':",
                                  "    app.run()"]
                },
                {
                    "narration_text": "We're now going to run the server.",
                    "code_text": ["<Escape>",
                                  ":x"]
                }
            ]
        },
        {"type" : "StartSubshell",
         "name" : "server_subshell"},
        {"type" : "ExecuteSubshell",
         "subshell_name" : "server_subshell",
         "command" : "python3.11 test_server.py &"},
        {"type" : "BrowserInteraction",
         "url" : "http://localhost:5000/",
         "text" : "As you can see, the webpage is rendered as expected."},
        {"type" : "TerminateSubshell",
         "name" : "server_subshell"}
        ],
    "output_video_name" : "final_video.mp4",
     "intro_outro" : {
        "intro_code": ["rm -rf test_server.py",
                       "clear"],
        "outro_code": ["rm -rf test_server.py",
                       "clear"]
    }
}
```

## Getting Started

You can install "tutgen" by following these steps:

1. **Clone the Repository**:

   First, clone the "tutgen" repository to your local machine using `git`:

   ```bash
   git clone https://github.com/thejackal360/tutgen.git
   ```

2. **Install ffmpeg**:

    Before using "tutgen," you need to install ffmpeg. If you're using Ubuntu, you can do so with the following command:
    ```bash
    sudo apt-get update
    sudo apt-get install ffmpeg
    ```

3. **Install VHS**:

    VHS is a tool used for generating the coding animations. Follow the instructions on their Github: https://github.com/charmbracelet/vhs

4. **Install Python Dependencies**:
    Navigate to the project directory where you cloned "tutgen" and use the following command to install the required dependencies from the requirements.txt file:

    ```bash
    pip install -r requirements.txt
    ```

5. **Install the Package**:
    To install the "tutgen" package, use the following command:
    ```bash
    pip install .
    ```

6. **Run the Tutorial Generator**:
    Once the package is installed, you can run the tutorial generator by using the following command:
    ```bash
    tutgen -h
    ```

    The repo contains a test.json file that you can use to test the tutorial generator.
    ```bash
    tutgen test.json
    ```

    A video named final_video.mp4 will be generated in the current directory.

## Platforms Tested

The following platforms have been tested:

- Ubuntu 22.04.3 LTS (Python 3.11)
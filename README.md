# This is pre-release software. Lots of bugs, low test coverage, etc

# Installation
## Setup venv
    virtualenv venv
    source venv/bin/activate

## Install prerequisites
    pip3 install -r requirements.txt

## Install vosk
[Download](https://alphacephei.com/vosk/models) the model of your choice and move it to a path that is reflected in `config.json`

## Install ollama
[Download](https://ollama.com/download) ollama.
Execute `ollama run [your-desired-model-name-here]` and ensure that you're able to interact with it

## Update config.json
Ensure that you add the desired vosk model path to `config.json`.
Update any of the other config values as you see fit.

# Run tests
From the root of repo:
`python3 -m unittest discover -s tests`

# Usage
Ensure you're using the venv `source venv/bin/activate`

Run `python3 main.py`

This will start the main loop which consists of:
* Performing an init sequence
* Listening to the system provided microphone until the eom phrase (customizable in config.json) is heard via vosk
* Transcribing the recorded audio via openai whisper
* Removing the command phrases from the transcription
* Sending the transcription as a prompt (plus configurable instructions) to the ollama served model
* Gathering the response from ollama and sending it to TTS
* Sending the TTS audio as an argument to launching an audio playing process
* Starting the loop again starting at the listening. This allows you to say "stop" if the audio response is too long

# This is pre-release software. Lots of bugs, low test coverage, etc
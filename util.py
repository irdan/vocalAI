import json
import os
import sys

def suppress_output():
    """Suppress stdout and stderr."""
    sys.stdout.flush()
    sys.stderr.flush()
    devnull = os.open(os.devnull, os.O_WRONLY)
    old_stdout = os.dup(sys.stdout.fileno())
    old_stderr = os.dup(sys.stderr.fileno())
    os.dup2(devnull, sys.stdout.fileno())
    os.dup2(devnull, sys.stderr.fileno())
    return old_stdout, old_stderr, devnull


def restore_output(old_stdout, old_stderr, devnull):
    """Restore stdout and stderr."""
    os.dup2(old_stdout, sys.stdout.fileno())
    os.dup2(old_stderr, sys.stderr.fileno())
    os.close(devnull)
    os.close(old_stdout)
    os.close(old_stderr)


def load_config(file_path):
    with open(file_path, 'r') as file:
        config_dict = json.load(file)
    return config_dict


class AppConfig:
    def __init__(self, config_dict):
        self.__dict__.update(config_dict)
#    def __init__(self, config_dict):
#        self.llm_url = config_dict["llm_url"]
#        self.llm_model = config_dict["llm_model"]
#        self.tts_model_path = config_dict["tts_model_path"]
#        self.whisper_model = config_dict["whisper_model"]
#        self.vosk_model_path = config_dict["vosk_model_path"]
#        self.stop_phrase = config_dict["stop_phrase"]
#        self.eom_phrase = config_dict["eom_phrase"]
#        self.end_session_phrase = config_dict["end_session_phrase"]
#        self.instructions = config_dict["instructions"]
#



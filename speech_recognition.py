import json
import logging
import numpy as np
import pyaudio
import re
import whisper
from event_manager import EventManager
from vosk import Model, KaldiRecognizer
from io import BytesIO

class SpeechRecognizer:
    _instance = None
    event_manager = EventManager.get_instance()
    logger = logging.getLogger(__name__)
    p = pyaudio.PyAudio()

    def __new__(cls, config):
        if cls._instance is None:
            cls._instance = super(SpeechRecognizer, cls).__new__(cls)
        return cls._instance

    def __init__(self, config, rate=16000, chunk=1024):
        self.config = config
        self.event_manager = SpeechRecognizer.event_manager
        self.event_manager.subscribe("audio_started", self.handle_audio_started)
        self.event_manager.subscribe("audio_stopped", self.handle_audio_stopped)
        self.logger = SpeechRecognizer.logger
        self.is_audio_playing = False
        self.end_session_flag = False
        self.speech_detected = False

        self.rate = rate
        self.chunk = chunk
        self.stream = SpeechRecognizer.p.open(format=pyaudio.paInt16,
                                  channels=1, # mono
                                  rate=rate,
                                  input=True,
                                  frames_per_buffer=chunk)

    def _load_fast_recognizer(self):
        self.model = Model(self.config.vosk_model_path)
        self.recognizer = KaldiRecognizer(self.model, self.rate)
        self.recognizer.SetWords(True)  # Enable word-level recognition

    def _load_whisper(self):
        self.whisper_model = whisper.load_model(self.config.whisper_model_name)

    def listen_until_stop_phrase(self):

        if not hasattr(self, "model"):
            self._load_fast_recognizer()

        audio_buffer = BytesIO()
        transcript = ""

        self.logger.debug("Listening until stop phrase")

        while True:
            data = self._read_audio_data()
            transcript += self._process_audio_data(data, audio_buffer)
            
            self.logger.info(f"You Said: '{transcript}'")

            if self._should_stop_recording(transcript):
                break

            self._handle_special_phrases(transcript)

        audio_buffer.seek(0)
        return audio_buffer

   # def listen_until_pause(self, audio_player):
   #     audio_buffer = BytesIO()
   #     total_silence_duration = 0
   #     max_silence = self.config.eom_pause_duration

   #     self.logger.debug("Listening until a pause")

   #     while True:
   #         data = self._read_audio_data()
   #         audio_buffer.write(data)
   #         is_silent = self._is_silent(data)

   #         recognized_text = self._process_audio_data(data, audio_buffer)
   #         if recognized_text != "":
   #             self._handle_commands(recognized_text)

   #         if not self.speech_detected:
   #             if not is_silent:
   #                 self.speech_detected = True
   #                 self.logger.debug("Speech detected, starting to monitor for pause")
   #         else:
   #             if is_silent:
   #                 total_silence_duration += len(data) / self.rate # duration in seconds
   #                 if total_silence_duration  >= max_silence:
   #                     self.logger.info("Sufficient pause detected, stopping listening")
   #                     break
   #             else:
   #                 total_silence_duration = 0

    def _is_silent(self, data):
        amplitude = self._calulate_amplitude(self, data)
        return amplitude < self.config.silence_threshold

    def _calulate_amplitude(self, data):
        samples = np.frombuffer(data, dtype=np.int16)
        avg_amplitude = np.mean(np.abs(samples))
        self.logger.debug(f"Average Amplitude: '{avg_amplitude}'")

        if avg_amplitude == 0:
            return -float('inf')
        else:
            amplitude_db = 20 * np.log10(avg_amplitude)
            return amplitude_db

    def _read_audio_data(self):
        return self.stream.read(self.chunk)

    def _process_audio_data(self, data, audio_buffer):
        audio_buffer.write(data)
        if self.recognizer.AcceptWaveform(data):
            result = json.loads(self.recognizer.Result())
            self.logger.info(f"Recognized text: '{result.get('text', '')}'")
            return result.get('text', '') + " "
        return ""

    def _should_stop_recording(self, transcript):
        if self.config.eom_phrase in transcript:
            self.logger.info(f"EOM phrase '{self.config.eom_phrase}' detected. Ending message.")
            return True
        return False

    def _handle_special_phrases(self, transcript):
        if self.config.end_session_phrase in transcript:
            self.logger.info(f"End session phrase '{self.config.end_session_phrase}' detected.")
            self.end_session_flag = True
        if self.config.stop_phrase  in transcript:
            self._react_to_stop_phrase()

    def _react_to_stop_phrase(self):
        if self.is_audio_playing:
            self.logger.debug("stop phrase detected and audio is playing, publishing event")
            self._publish_stop_audio()
        else:
            self.logger.debug("stop phrase detected in recognized text, no audio playing")

    def _publish_stop_audio(self):
        self.logger.debug("Internal call to _publish_stop_audio")
        self.logger.debug("Stopping audio playback")
        self.event_manager.publish("stop_audio", None)
        while (self.is_audio_playing):
            self.logger.debug("waiting for audio to stop")
        return BytesIO() # reset empty buffer, ready for new audio message

    def transcribe(self, audio_buffer):
        self.logger.debug("transcribing audio with whisper")
        audio_data = np.frombuffer(audio_buffer.getvalue(), dtype=np.int16).astype(np.float32) / 32768.0

        if not hasattr(self, 'whisper_model'):
            self._load_whisper()

        result = self.whisper_model.transcribe(audio_data)
        return result["text"]

    def handle_audio_started(self, _=None):
        self.logger.debug("handle_audio_started: setting flag to true")
        self.is_audio_playing = True

    def handle_audio_stopped(self, _=None):
        self.logger.debug("handle_audio_stopped: setting flag to false")
        self.is_audio_playing = False

    def remove_command_words(self, text_prompt):
        self.logger.debug("BEFORE removing command words: %s", text_prompt)
        command_words = [self.config.eom_phrase, self.config.end_session_phrase]
        pattern = re.compile("|".join(re.escape(word) for word in command_words), re.IGNORECASE)
        self.logger.debug("AFTER removing command words: %s", pattern.sub("", text_prompt))
        return pattern.sub("", text_prompt)

    def cleanup(self):
        self.logger.debug("Cleanup on speech_recognition!")
        self.stream.stop_stream()
        self.stream.close()


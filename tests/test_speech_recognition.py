import numpy as np
import unittest
import wave
from contextlib import contextmanager
from io import BytesIO
from unittest.mock import MagicMock, patch
from speech_recognition import SpeechRecognizer
from util import AppConfig, suppress_output, restore_output


class TestSpeechRecognizer(unittest.TestCase):

#    @classmethod
#    def setUpClass(cls):
#        config_dict = {
#            "vosk_model_path"       : "/home/d/ai-models/robotherapy/vosk-model-en-us-0.22",
#            "whisper_model_name"    : "small.en",
#            "stop_phrase"           : "stop",
#            "eom_phrase"            : "porcupine",
#            "end_session_phrase"    : "stop session"
#        }
#        config = AppConfig(config_dict)
#
#        cls.sr = SpeechRecognizer(config)

#        old_stdout, old_stderr, devnull = suppress_output()
#        try:
#            cls.speech_recognizer = SpeechRecognizer(config)
#        finally:
#            restore_output(old_stdout, old_stderr, devnull)

    def setUp(self):
        config_dict = {
            "vosk_model_path"       : "/home/d/ai-models/robotherapy/vosk-model-en-us-0.22",
            "whisper_model_name"    : "small.en",
            "stop_phrase"           : "stop",
            "eom_phrase"            : "porcupine",
            "end_session_phrase"    : "stop session"
        }
        config = AppConfig(config_dict)

        if hasattr(self, 'sr'):
            del self.sr

        self.sr = SpeechRecognizer(config)
        self.sr.logger = MagicMock()

    def tearDown(self):
        del self.sr

    def test_publish_stop_audio(self):
        with patch.object(self.sr.event_manager, 'publish', autospec=True) as mock_publish:
            self.sr.is_audio_playing = False
            self.sr._publish_stop_audio()
            mock_publish.assert_called_with("stop_audio", None)

    #def test_
        

#    def test_transcribe(self):
#        file_path = "tests/test_data/pcm_phrase.wav"
#        audio_buffer = BytesIO()
#        with wave.open(file_path, 'rb') as wave_file:
#            frames = wave_file.readframes(wave_file.getnframes())
#            audio_buffer.write(frames)
#            audio_buffer.seek(0)
#            from pydub import AudioSegment
#            from pydub.playback import play
#            #audio = AudioSegment.from_wav(audio_buffer)
#            audio = AudioSegment(
#                data=audio_buffer.getvalue(),
#                sample_width=wave_file.getsampwidth(),
#                frame_rate=wave_file.getframerate(),
#                channels=wave_file.getnchannels()
#            )
#            play(audio)
#            audio_buffer.seek(0)
#
#        transcribed_text = self.sr.transcribe(audio_buffer)
#        self.assertEqual("stop", transcribed_text)


    def test_handle_audio_started(self):
        self.sr.is_audio_playing = False
        self.assertFalse(self.sr.is_audio_playing)
        self.sr.handle_audio_started()
        self.assertTrue(self.sr.is_audio_playing)

    def test_handle_audio_stopped(self):
        self.sr.is_audio_playing = True
        self.assertTrue(self.sr.is_audio_playing)
        self.sr.handle_audio_stopped()
        self.assertFalse(self.sr.is_audio_playing)

    def test_remove_command_words(self):
        text = "this is a test phrase. " + self.sr.config.eom_phrase + ". " + self.sr.config.end_session_phrase + "."
        cleaned = self.sr.remove_command_words(text)
        self.assertEqual("this is a test phrase. . .", cleaned)

    def test_should_stop_recording(self):
        text = "Example words. " + self.sr.config.eom_phrase
        outcome = self.sr._should_stop_recording(text)
        self.assertTrue(outcome)

        text = "Example words."
        outcome = self.sr._should_stop_recording(text)
        self.assertFalse(outcome)

    @patch.object(SpeechRecognizer, '_publish_stop_audio', autospec=True)
    def test_react_to_stop_phrase(self, _publish_stop_audio):
        self.sr.is_audio_playing = True
        self.sr._react_to_stop_phrase()
        self.sr._publish_stop_audio.assert_called_once()

        self.sr.is_audio_playing = False
        self.sr._publish_stop_audio.reset_mock()
        self.sr._react_to_stop_phrase()
        self.sr._publish_stop_audio.assert_not_called()

    @patch.object(SpeechRecognizer, '_react_to_stop_phrase', autospec=True)
    def test_handle_special_phrases(self, _react_to_stop_phrase):
        self.sr.end_session_flag = False
        self.assertFalse(self.sr.end_session_flag)
        text = self.sr.config.end_session_phrase
        self.sr._handle_special_phrases(text)
        self.assertTrue(self.sr.end_session_flag)
        self.sr._react_to_stop_phrase.assert_called_once()

        text = self.sr.config.stop_phrase
        self.sr._react_to_stop_phrase.reset_mock()
        self.sr._handle_special_phrases(text)
        self.sr._react_to_stop_phrase.assert_called_once()

    def test_process_audio_data(self):
        pass
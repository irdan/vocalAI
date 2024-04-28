import unittest
from unittest.mock import MagicMock, patch
from vocalai.audio_player import AudioPlayer
import simpleaudio as sa


class TestAudioPlayer(unittest.TestCase):
    @patch('vocalai.audio_player.EventManager.get_instance')
    def setUp(self, mock_event_manager):
        self.mock_event_manager = mock_event_manager.return_value
        self.audio_player = AudioPlayer()
        self.audio_file = 'test.wav'

    def test_init(self):
        """Test initialization of AudioPlayer."""
        self.mock_event_manager.subscribe.assert_called_with("stop_audio", self.audio_player.stop)
        self.assertIsNone(self.audio_player.audio_thread)
        self.assertIsNone(self.audio_player.play_obj)

    @patch('vocalai.audio_player.sa.WaveObject.from_wave_file')
    def test_play_audio_starts_thread(self, mock_wave_obj):
        """Test that playing audio starts a new thread."""
        with patch('threading.Thread.start') as mock_thread_start:
            self.audio_player.play(self.audio_file)
            mock_thread_start.assert_called_once()

    @patch('vocalai.audio_player.sa.WaveObject.from_wave_file')
    def test_play_audio_starts_playback(self, mock_wave_obj):
        """Test that audio playback starts."""
        mock_wave_obj.return_value.play.return_value.is_playing.return_value = True
        with patch('threading.Thread.start') as mock_thread_start:
            self.audio_player.play(self.audio_file)
            self.audio_player._play_audio(self.audio_file)
            self.mock_event_manager.publish.assert_any_call("audio_started", None)
            self.mock_event_manager.publish.assert_any_call("audio_stopped", None)

    @patch('threading.Thread')
    def test_stop_audio(self, mock_thread):
        """Test stopping the audio playback."""
        self.audio_player.audio_thread = mock_thread
        self.audio_player.play_obj = MagicMock()
        self.audio_player.play_obj.is_playing.return_value = True
        self.audio_player.stop()
        self.audio_player.play_obj.stop.assert_called_once()
        mock_thread.join.assert_called_with(timeout=1)
        self.mock_event_manager.publish.assert_called_with("audio_stopped", None)

    def test_is_playing(self):
        """Test is_playing method."""
        self.audio_player.play_obj = MagicMock()
        self.audio_player.play_obj.is_playing.return_value = True
        self.assertTrue(self.audio_player.is_playing())
        self.audio_player.play_obj.is_playing.return_value = False
        self.assertFalse(self.audio_player.is_playing())

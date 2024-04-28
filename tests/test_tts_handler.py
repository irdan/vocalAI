import unittest
import numpy as np
import torch
import wave
from unittest.mock import patch, MagicMock
from vocalai.tts_handler import TTSHandler



class MockConfig:
    def __init__(self, tts_model_path):
        self.tts_model_path = tts_model_path

class TestTTSHandler(unittest.TestCase):
    def setUp(self):
        self.config = MockConfig(tts_model_path="tts_models/en/jenny/jenny")

    @patch('torch.cuda.is_available')
    def test_init_with_no_cuda(self, mock_cuda_avail):
        """Test initialization raises when no CUDA is available."""
        mock_cuda_avail.return_value = False
        with self.assertRaises(RuntimeError) as context:
            tts_handler = TTSHandler(self.config)
        self.assertIn("TTS requires a GPU", str(context.exception))

    @patch('torch.cuda.is_available', return_value=True)
    @patch('TTS.api.TTS')
    def test_init_successful(self, mock_tts_class, mock_cuda_avail):
        """Test successful initialization with CUDA."""
        # Setup the mock to behave as expected
        mock_tts_instance = mock_tts_class.return_value
        mock_tts_instance.to.return_value = "cuda"

        # Trigger init function
        tts_handler = TTSHandler(self.config)

        # Asserts
        mock_tts_class.assert_called_once_with(self.config.tts_model_path)
        mock_tts_instance.to.assert_called_once_with("cuda")

    @patch('torch.cuda.is_available')
    @patch('TTS.api.TTS')
    def test_get_audio(self, mock_tts, mock_cuda_avail):
        """Test get_audio returns a BytesIO object with correct audio data."""
        mock_cuda_avail.return_value = True
        mock_tts_instance = mock_tts.return_value 
        mock_tts_instance.to.return_value.tts.return_value = np.array([0.1, -0.1, 0.2, -0.2], dtype=np.float32)

        tts_handler = TTSHandler(self.config)
        audio_buffer = tts_handler.get_audio("Hello world")
        # Check the contents of audio_buffer
        with wave.open(audio_buffer, 'rb') as wav_file:
            params = wav_file.getparams()
            frames = wav_file.readframes(params.nframes)
            self.assertEqual(params.nchannels, 1)
            self.assertEqual(params.sampwidth, 2)
            self.assertEqual(params.framerate, 48000)
            self.assertTrue(len(frames) > 0)

    @patch('torch.cuda.is_available')
    @patch('TTS.api.TTS')
    def test_exception_in_loading_model(self, mock_tts, mock_cuda_avail):
        """Test that an exception is raised if TTS model fails to load."""
        mock_cuda_avail.return_value = True
        mock_tts.side_effect = Exception("Loading error")
        with self.assertRaises(Exception) as context:
            self.config = MockConfig(tts_model_path="invalid/path/for/testing")
            tts_handler = TTSHandler(self.config)
        self.assertIn("failed to load TTS model: Loading error", str(context.exception))

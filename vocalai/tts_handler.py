import logging
import numpy as np
import torch
import wave
from io import BytesIO
from vocalai.util import suppress_output, restore_output

class TTSHandler:
    def __init__(self, config):
        from TTS.api import TTS # move import so it can be mocked in tests
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        if self.device != "cuda":
            raise RuntimeError("TTS requires a GPU")
        self.logger = logging.getLogger(__name__)

        old_stdout, old_stderr, devnull = suppress_output()
        try:
            self.tts_model = TTS(config.tts_model_path).to(self.device)
        except Exception as e:
            raise Exception(f"failed to load TTS model: {str(e)}")
        finally:
            restore_output(old_stdout, old_stderr, devnull)

    def get_audio(self, text):
        wav_samples = self.tts_model.tts(text=text)
        scaled_samples = np.int16(np.array(wav_samples, dtype=np.float32) * 32767)
        wav_buffer = BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_bytes:
            wav_bytes.setnchannels(1)
            wav_bytes.setsampwidth(2)
            wav_bytes.setframerate(48000)
            wav_bytes.writeframes(bytearray(scaled_samples))
        wav_buffer.seek(0)
        return wav_buffer


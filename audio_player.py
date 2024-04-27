import logging
import threading
import simpleaudio as sa
from event_manager import EventManager


class AudioPlayer:
    _lock = threading.Lock()

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.audio_thread = None
        self.event_manager = EventManager.get_instance()
        self.event_manager.subscribe("stop_audio", self.stop)
        self.play_obj = None
        self.logger.debug("AudioPlayer initialized and subscribed to stop_audio")

    def _play_audio(self, audio_file):
        with self.__class__._lock:
            if self.play_obj and self.play_obj.is_playing():
                self.logger.debug("An audio is already playing. Stopping it first.")
                self.stop()

            self.logger.debug(f"Starting to play audio file: {audio_file}")
            self.event_manager.publish("audio_started", None)
            try:
                wave_obj = sa.WaveObject.from_wave_file(audio_file)
                self.play_obj = wave_obj.play()
                self.play_obj.wait_done()
            except Exception as e:
                self.logger.error(f"failed to play audio: {str(e)}")
            finally:
                self.event_manager.publish("audio_stopped", None)
                self.logger.debug("Audio playback completed and audio_stopped event published")

    def play(self, audio_file):
        if self.audio_thread and self.audio_thread.is_alive():
            self.logger.debug("Stopping currently playing audio to start new audio")
            self.stop()
        self.audio_thread = threading.Thread(target=self._play_audio, args=(audio_file,))
        self.audio_thread.start()
        self.logger.debug(f"New audio process started for: {audio_file}")


    def stop(self, data=None):
        if self.play_obj and self.play_obj.is_playing():
            self.logger.debug("Stopping audio playback")
            self.play_obj.stop()
        if self.audio_thread:
            self.audio_thread.join(timeout=1)
        self.audio_thread = None
        self.event_manager.publish("audio_stopped", None)
        self.logger.debug("Audio process stopped and cleaned up")

    def is_playing(self):
        playing = self.play_obj is not None and self.play_obj.is_playing()
        self.logger.debug(f"Is audio playing? {'Yes' if playing else 'No'}")
        return playing

    def cleanup(self):
        self.logger.debug("Cleaning up AudioPlayer, stopping any playing audio")
        self.stop()
        self.event_manager.publish("audio_stopped", None)


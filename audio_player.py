import logging
import multiprocessing
from event_manager import EventManager
from pydub import AudioSegment
from pydub.playback import play



class AudioPlayer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.audio_process = None
        self.lock = multiprocessing.Lock()
        self.event_manager = EventManager.get_instance()
        self.event_manager.subscribe("stop_audio", self.stop)
        self.logger.debug("AudioPlayer initialized and subscribed to stop_audio")

    def _play_audio(self, audio_file):
        with self.lock:
                self.logger.debug(f"Starting to play audio file: {audio_file}")
                self.event_manager.publish("audio_started", None)
                audio_segment = AudioSegment.from_file(audio_file, format="wav")
                play(audio_segment)
                self.event_manager.publish("audio_stopped", None)
                self.logger.debug("Audio playback completed and audio_stopped event published")

    def play(self, audio_file):
        if self.audio_process and self.audio_process.is_alive():
            self.logger.debug("Stopping currently playing audio to start new audio")
            self.stop()
        self.audio_process = multiprocessing.Process(target=self._play_audio, args=(audio_file,))
        self.audio_process.start()
        self.logger.debug(f"New audio process started for: {audio_file}")


    def stop(self, data=None):
        if self.audio_process and self.audio_process.is_alive():
            self.logger.debug("Terminating audio process")
            self.audio_process.terminate()
            self.audio_process.join()
            self.event_manager.publish("audio_stopped", None)
        self.audio_process = None
        self.logger.debug("Audio process stopped and cleaned up")

    def is_playing(self):
        playing = self.audio_process is not None and self.audio_process.is_alive()
        self.logger.debug(f"Is audio playing? {'Yes' if playing else 'No'}")
        return playing

    def cleanup(self):
        self.logger.debug("Cleaning up AudioPlayer, stopping any playing audio")
        self.stop()
        self.event_manager.publish("audio_stopped", None)


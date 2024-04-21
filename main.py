import logging
from audio_player import AudioPlayer
from speech_recognition import SpeechRecognizer
from llm_interaction import LLMInteraction
from tts_handler import TTSHandler
from util import load_config, suppress_output, restore_output, AppConfig
from logger import setup_logging


def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    config_dict = load_config("config.json")
    config = AppConfig(config_dict)
    logger.info("Config loaded")

    old_stdout, old_stderr, devnull = suppress_output()
    try:
        audio_player = AudioPlayer()
        speech_recognizer = SpeechRecognizer(config)
        llm_interaction = LLMInteraction(config)
        tts_handler = TTSHandler(config)
    finally:
        restore_output(old_stdout, old_stderr, devnull)
    logger.info("Init completed")

    while True:
        logger.debug("Started main loop")
        audio_prompt = speech_recognizer.listen_until_stop_phrase()
        logger.debug("audio prompt acquired")
        text_prompt = speech_recognizer.transcribe(audio_prompt)
        logger.debug("text prompt acquired")
        cleaned_prompt = speech_recognizer.remove_command_words(text_prompt)
        logger.debug("cleaned prompt acquired")
        llm_answer = llm_interaction.query_llm(cleaned_prompt)
        logger.debug("llm answer acquired")
        audio_response = tts_handler.get_audio(llm_answer)
        logger.debug("audio response acquired")
        audio_player.play(audio_response)
        logger.debug("audio player completed")

        if speech_recognizer.end_session_flag:
            logger.debug("end session flag detected, breaking main loop")
            break

    logger.debug("running cleanup on audio_player and speech_recognizer")
    audio_player.cleanup()
    speech_recognizer.cleanup()
    logger.debug("end of file reached")

if __name__ == "__main__":
    main()

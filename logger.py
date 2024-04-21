import logging
import logging.handlers

def setup_logging(level=logging.DEBUG):
    # Root logger
    logger = logging.getLogger()
    logger.setLevel(level)

    # Syslog Handler
    syslog_handler = logging.handlers.SysLogHandler(address='/dev/log')
    syslog_formatter = logging.Formatter('%(name)s: [%(levelname)s] %(message)s')
    syslog_handler.setFormatter(syslog_formatter)
    logger.addHandler(syslog_handler)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - [%(levelname)s] %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)


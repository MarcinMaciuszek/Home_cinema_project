import sys
import logging

ENCODING = 'UTF-8'
LOG_FILE = "runtime.log"
LOG_TO_CONSOLE = True
LOG_LEVEL = logging.DEBUG


def logger_creation(name=None, logging_level=LOG_LEVEL):
    logger = logging.getLogger(name)
    logger.setLevel(logging_level)

    file_handler = logging.FileHandler(LOG_FILE, encoding=ENCODING)
    file_handler.setLevel(logging_level)

    if LOG_TO_CONSOLE:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(logging_level)

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s : %(message)s", datefmt='%d/%m/%Y %I:%M:%S %p')
    file_handler.setFormatter(formatter)
    if LOG_TO_CONSOLE:
        stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.debug("Logger: {} created.".format(name))
    return logger

import logging
import sys


class Logging:
    FORMATTER = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    LOG_FILE = "app.log"

    def __init__(self, logger_name):
        self.logger = logging.getLogger(logger_name)
        self._setup_logger()

    def _setup_logger(self):
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(self._get_console_handler())
        self.logger.propagate = False

    def _get_console_handler(self):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.FORMATTER)
        return console_handler

    @staticmethod
    def get_logger(logger_name) -> logging.Logger:
        return Logging(logger_name).logger

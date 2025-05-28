import logging
from logging.handlers import RotatingFileHandler
import sys


def setup_logger():
    # Create a logger instance
    logger = logging.getLogger("fda_db_checkup")
    logger.setLevel(logging.INFO)  # Default log level: INFO

    # Define log message format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Add console handler to output logs to stdout
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Add file handler to save logs to a file
    file_handler = RotatingFileHandler(
        "fda_db_checkup.log", maxBytes=10 * 1024 * 1024, backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


# Instantiate the logger for use across the application
logger = setup_logger()

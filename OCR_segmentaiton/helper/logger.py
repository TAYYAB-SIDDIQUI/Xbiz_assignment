# logger.py
import logging

def setup_logger(name, log_file, level=logging.DEBUG):
    """Setup a logger to write to a file."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding multiple handlers if called multiple times
    if not logger.handlers:
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)

        # Log format
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

    return logger

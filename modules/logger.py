# system imports
import os

# Logging imports
import logging


def assert_log_path(log_path: str):
    """
    Assert that the log path is a valid file path.
    If the directory does not exist, it will be created.
    """
    log_dir = os.path.dirname(log_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
        logging.info(f"Created log directory: {log_dir}")
    else:
        logging.info(f"Log directory already exists: {log_dir}")
    
    return log_path

def setup_logger(log_path: str, clear_log: bool = False):
    """
    Setup the logger for the application.
    """
    log_path = assert_log_path(log_path)
    # Create the logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    if logger.hasHandlers() and clear_log:
        logger.handlers.clear()

    # File Handler
    file_handler = logging.FileHandler(log_path, mode='w')
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('TERMINAL: %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


    logger.info(f"Log path: {log_path}")
    
    return logger

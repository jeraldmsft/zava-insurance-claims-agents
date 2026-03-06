"""Logging configuration for Zava Insurance voice agent."""
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='🎤 [ZAVA-VOICE] %(asctime)s - %(levelname)s - %(message)s',
        datefmt="%H:%M:%S"
    )
    for lib in ["azure", "azure.core", "azure.identity", "azure.ai", "urllib3"]:
        logging.getLogger(lib).setLevel(logging.WARNING)
    return logging.getLogger(__name__)

def get_logger(name: str = __name__):
    return logging.getLogger(name)

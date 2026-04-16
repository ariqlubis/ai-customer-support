from loguru import logger
import sys
import os

LOG_PATH = "logs/app.log"
logger.remove()

logger.add(
    sys.stdout,
    format="<green>{time}</green> | <level>{level}</level> | {message}",
    level='INFO'
)

logger.add(
    LOG_PATH,
    rotation='1 MB',
    retention='7 days',
    compression='zip',
    level='INFO'
)

def get_logger():
    return logger
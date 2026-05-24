import logging

logger = logging.getLogger(__name__)


def send_sms(phone: str, message: str) -> bool:
    logger.info("SMS adapter queued message to %s: %s", phone, message)
    return True

import re
from typing import Tuple

EMAIL_MASK = "|||EMAIL_ADDRESS|||"
PHONE_MASK = "|||PHONE_NUMBER|||"
IP_MASK = "|||IP_ADDRESS|||"

EMAIL_PATTERN = re.compile(r"[\w\.-]+@[\w\.-]+\.[A-Za-z]{2,}", re.IGNORECASE)
PHONE_PATTERN = re.compile(
    r"(?:\d{10}|\(\d{3}\)[-\s]?\d{3}[-\s]?\d{4}|\d{3}[-\s]\d{3}[-\s]\d{4})"
)
IP_PATTERN = re.compile(
    r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b"
)


def mask_emails(text: str) -> Tuple[str, int]:
    """
    Replace all email addresses in the input text with the EMAIL_MASK.
    Returns the masked text and the number of replacements made.
    """
    masked_text, count = EMAIL_PATTERN.subn(EMAIL_MASK, text)
    return masked_text, count


def mask_phone_numbers(text: str) -> Tuple[str, int]:
    """
    Replace common US phone number formats in the input text with the PHONE_MASK.
    Returns the masked text and the number of replacements made.
    """
    masked_text, count = PHONE_PATTERN.subn(PHONE_MASK, text)
    return masked_text, count


def mask_ips(text: str) -> Tuple[str, int]:
    """
    Replace IPv4 addresses in the input text with the IP_MASK.
    Returns the masked text and the number of replacements made.
    """
    masked_text, count = IP_PATTERN.subn(IP_MASK, text)
    return masked_text, count 
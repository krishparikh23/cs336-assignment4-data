from typing import Optional
from resiliparse.extract.html2text import extract_plain_text
from resiliparse.parse.encoding import detect_encoding


def extract_text_from_html_bytes(html_bytes: bytes) -> Optional[str]:
    """
    Extract plain text from HTML bytes, detecting encoding if necessary.
    """
    try:
        html_str = html_bytes.decode('utf-8')
    except UnicodeDecodeError:
        encoding = detect_encoding(html_bytes)
        html_str = html_bytes.decode(encoding, errors='replace')

    text = extract_plain_text(html_str)
    return text 
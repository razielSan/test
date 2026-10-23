from typing import Optional
from urllib.parse import urlparse


class BaseAppURL:
    HOST = "127.0.0.1"
    PORT = 8000


ALLOWED_ORIGINS = (
    f"http://{BaseAppURL.HOST}:{BaseAppURL.PORT}",
    "http://localhost:8000",
)

SAFE_METHODS = {
    "GET",
    "HEAD",
    "OPTIONS",
}


def origin_from_url(url: str) -> Optional[str]:
    """
    Вычисляет origin по url и возращает его, если строка
    не url возращает None

    >>> origin_from_url('https://example.com')
    'https://example.com'

    >>> origin_from_url('http://example.com/search')
    'http://example.com'

    >>> origin_from_url('example') is None
    True
    """
    parsed = urlparse(url)
    if parsed.scheme not in ["http", "https"] or not parsed.netloc:
        return None
    return f"{parsed.scheme}://{parsed.netloc}"


def get_origin_from_referer(referer: str) -> Optional[str]:
    if referer == "null":
        return None
    return origin_from_url(referer)

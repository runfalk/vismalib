import sys

__all__ = [
    "is_python2",
    "urljoin",
]

is_python2 = sys.version_info.major == 2

if is_python2:
    from urlparse import urljoin
else:
    from urllib.parse import urljoin

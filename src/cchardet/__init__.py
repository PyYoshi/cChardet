from . import _cchardet

version = (2, 2, 0, "alpha", 3)
__version__ = "2.2.0a3"


def _as_bytes(data):
    if isinstance(data, bytes):
        return data
    if isinstance(data, (bytearray, memoryview)):
        return bytes(data)
    raise TypeError("data must be bytes-like")


def detect(msg, *, max_bytes=None):
    """
    Args:
        msg: bytes-like object
        max_bytes: optional maximum number of bytes to examine
    Returns:
        {
            "encoding": str,
            "confidence": float,
            "language": str
        }
    """
    encoding, language, confidence = _cchardet.detect_with_details(_as_bytes(msg), max_bytes)
    if isinstance(encoding, bytes):
        encoding = encoding.decode()
    if isinstance(language, bytes):
        language = language.decode()

    if encoding == "MAC-CENTRALEUROPE":
        encoding = "maccentraleurope"

    return {"encoding": encoding, "confidence": confidence, "language": language}


def detect_all(msg, *, max_bytes=None):
    """Return every uchardet candidate in descending confidence order."""
    results = []
    for encoding, language, confidence in _cchardet.detect_all(_as_bytes(msg), max_bytes):
        encoding = encoding.decode()
        if encoding == "MAC-CENTRALEUROPE":
            encoding = "maccentraleurope"
        results.append(
            {
                "encoding": encoding,
                "confidence": confidence,
                "language": language.decode() if language is not None else None,
            }
        )
    return results


class UniversalDetector(object):
    def __init__(self):
        self._detector = _cchardet.UniversalDetector()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.close()
        return False

    def reset(self):
        self._detector.reset()

    def feed(self, data):
        self._detector.feed(_as_bytes(data))

    def close(self):
        self._detector.close()

    @property
    def done(self):
        return self._detector.done

    @property
    def result(self):
        encoding, language, confidence = self._detector.result
        if isinstance(encoding, bytes):
            encoding = encoding.decode()
        if isinstance(language, bytes):
            language = language.decode()
        return {"encoding": encoding, "confidence": confidence, "language": language}

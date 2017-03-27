from cchardet import _cchardet
from .version import __version__


def detect(msg):
    """
    Args:
        msg: str
    Returns:
        {
            "encoding": str,
            "confidence": float
        }
    """
    encoding, confidence = _cchardet.detect_with_confidence(msg)
    if isinstance(encoding, bytes):
        encoding = encoding.decode()
    return { "encoding": encoding, "confidence": confidence }

from ._cchardet import UniversalDetector as UniversalDetector, detect_with_confidence as detect_with_confidence
from .typedefs import DecodeResultDict
version = (2, 2, 0, "alpha", 3)
__version__ = "2.2.0a3"


def detect(msg: bytes) -> DecodeResultDict:
    """
    Args:
        msg: str
    Returns:
        {
            "encoding": str,
            "confidence": float
        }
    """
    encoding, confidence = detect_with_confidence(msg)
    if encoding is not None:
        encoding = encoding.decode()

    if encoding == "MAC-CENTRALEUROPE":
        encoding = "maccentraleurope"

    return {"encoding": encoding, "confidence": confidence}


__all__ = (
    "detect",
    "detect_with_confidence",
    "DecodeResultDict",
    "UniversalDetector",
    "__version__"
)

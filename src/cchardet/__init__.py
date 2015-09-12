#!/usr/bin/env python
# coding: utf-8

from . import _cchardet
from ._version import version as __version__

__all__ = ['__version__', 'detect']


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
    return {"encoding": encoding, "confidence": confidence}

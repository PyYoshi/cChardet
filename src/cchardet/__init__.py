#!/usr/bin/env python
# coding: utf-8

from cchardet import _cchardet

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

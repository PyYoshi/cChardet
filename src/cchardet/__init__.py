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
    return _cchardet.detect_with_confidence(msg)

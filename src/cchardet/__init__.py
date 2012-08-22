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
    # TODO: Unicode t = u"あいうえお" があった時の対処 "isinstance(t,unicode) == True"
    return _cchardet.detect_with_confidence(msg)

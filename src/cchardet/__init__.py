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


class Detector(object):
    """Wrap csd_consider with 'feed' feature."""

    def __init__(self):
        self._detector = _cchardet.Detector()

    def feed(self, data):
        self._detector.feed(data)

    def close(self):
        self._detector.close()

    @property
    def done(self):
        return self._detector.done

    @property
    def result(self):
        encoding, confidence = self._detector.result
        if isinstance(encoding, bytes):
            encoding = encoding.decode()
        return {"encoding": encoding, "confidence": confidence}

#!/usr/bin/env python
# coding: utf-8

from cchardet import _cchardet

def detect(msg):
    return _cchardet.detect(msg)

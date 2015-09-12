#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function

from unittest import TestCase
from os.path import dirname, abspath, join

# http://docs.python.org/library/codecs.html
# https://bitbucket.org/medoc/uchardet-enhanced/src/85fc77c3e058/libcharsetdetect/README.md

# Support codecs
# Big5
# EUC-JP
# EUC-KR
# GB18030
# gb18030
# HZ-GB-2312
# IBM855
# IBM866
# ISO-2022-CN
# ISO-2022-JP
# ISO-2022-KR
# ISO-8859-2
# ISO-8859-5
# ISO-8859-7
# ISO-8859-8
# KOI8-R
# Shift_JIS
# TIS-620
# UTF-8
# UTF-16BE
# UTF-16LE
# UTF-32BE
# UTF-32LE
# windows-1250
# windows-1251
# windows-1252
# windows-1253
# windows-1255
# x-euc-tw
# X-ISO-10646-UCS-4-2143
# X-ISO-10646-UCS-4-3412
# x-mac-cyrillic
import cchardet
import chardet
import pytest


_here = abspath(dirname(__file__))


def data_path(path):
    return join(_here, path)


@pytest.mark.parametrize(('path', 'encoding'), [
    (r'testdata/bg/ISO-8859-5/wikitop_bg_ISO-8859-5.txt', 'ISO-8859-5'),
    (r'testdata/bg/UTF-8/wikitop_bg_UTF-8.txt', 'UTF-8'),
    ('testdata/bg/WINDOWS-1251/wikitop_bg_WINDOWS-1251.txt', 'WINDOWS-1251'),
    ('testdata/cz/ISO-8859-2/wikitop_cz_ISO-8859-2.txt', 'ISO-8859-2'),
    ('testdata/cz/UTF-8/wikitop_cz_UTF-8.txt', 'UTF-8'),
    ('testdata/de/UTF-8/wikitop_de_UTF-8.txt', 'UTF-8'),
    ('testdata/de/WINDOWS-1252/wikitop_de_WINDOWS-1252.txt', 'WINDOWS-1252'),
    ('testdata/dk/UTF-8/wikitop_dk_UTF-8.txt', 'UTF-8'),
    ('testdata/dk/WINDOWS-1252/wikitop_dk_WINDOWS-1252.txt', 'WINDOWS-1252'),
    ('testdata/el/ISO-8859-7/wikitop_el_ISO-8859-7.txt', 'ISO-8859-7'),
    ('testdata/el/UTF-8/wikitop_el_UTF-8.txt', 'UTF-8'),
    ('testdata/en/UTF-8/wikitop_en_UTF-8.txt', 'UTF-8'),
    ('testdata/en/WINDOWS-1252/wikitop_en_WINDOWS-1252.txt', 'WINDOWS-1252'),
    ('testdata/es/UTF-8/wikitop_es_UTF-8.txt', 'UTF-8'),
    ('testdata/es/WINDOWS-1252/wikitop_es_WINDOWS-1252.txt', 'WINDOWS-1252'),
    ('testdata/fi/UTF-8/wikitop_fi_UTF-8.txt', 'UTF-8'),
    ('testdata/fi/WINDOWS-1252/wikitop_fi_WINDOWS-1252.txt', 'WINDOWS-1252'),
    ('testdata/fr/UTF-8/wikitop_fr_UTF-8.txt', 'UTF-8'),
    ('testdata/fr/WINDOWS-1252/wikitop_fr_WINDOWS-1252.txt', 'WINDOWS-1252'),
    ('testdata/he/UTF-8/wikitop_he_UTF-8.txt', 'UTF-8'),
    ('testdata/he/WINDOWS-1255/wikitop_he_WINDOWS-1255.txt', 'WINDOWS-1255'),
    ('testdata/hu/UTF-8/wikitop_hu_UTF-8.txt', 'UTF-8'),
    ('testdata/hu/ISO-8859-2/wikitop_hu_ISO-8859-2.txt', 'ISO-8859-2'),
    ('testdata/it/UTF-8/wikitop_it_UTF-8.txt', 'UTF-8'),
    ('testdata/it/WINDOWS-1252/wikitop_it_WINDOWS-1252.txt', 'WINDOWS-1252'),
    ('testdata/nl/UTF-8/wikitop_nl_UTF-8.txt', 'UTF-8'),
    ('testdata/nl/WINDOWS-1252/wikitop_nl_WINDOWS-1252.txt', 'WINDOWS-1252'),
    ('testdata/no/UTF-8/wikitop_no_UTF-8.txt', 'UTF-8'),
    ('testdata/no/WINDOWS-1252/wikitop_no_WINDOWS-1252.txt', 'WINDOWS-1252'),
    ('testdata/pl/UTF-8/wikitop_pl_UTF-8.txt', 'UTF-8'),
    ('testdata/pl/ISO-8859-2/wikitop_pl_ISO-8859-2.txt', 'ISO-8859-2'),
    ('testdata/pt/UTF-8/wikitop_pt_UTF-8.txt', 'UTF-8'),
    ('testdata/pt/WINDOWS-1252/wikitop_pt_WINDOWS-1252.txt', 'WINDOWS-1252'),
    ('testdata/ru/UTF-8/wikitop_ru_UTF-8.txt', 'UTF-8'),
    ('testdata/ru/WINDOWS-1251/wikitop_ru_WINDOWS-1251.txt', 'WINDOWS-1251'),
    ('testdata/ru/IBM855/wikitop_ru_IBM855.txt', 'IBM855'),
    ('testdata/ru/KOI8-R/wikitop_ru_KOI8-R.txt', 'KOI8-R'),
    ('testdata/ru/X-MAC-CYRILLIC/wikitop_ru_MACCYRILLIC.txt', 'MAC-CYRILLIC'),
    ('testdata/se/UTF-8/wikitop_se_UTF-8.txt', 'UTF-8'),
    ('testdata/se/WINDOWS-1252/wikitop_se_WINDOWS-1252.txt', 'WINDOWS-1252'),
    ('testdata/th/UTF-8/wikitop_th_UTF-8.txt', 'UTF-8'),
    ('testdata/th/TIS-620/utffool_th_TIS-620.txt', 'TIS-620'),
    ('testdata/th/TIS-620/wikitop_th_TIS-620.txt', 'TIS-620'),
    ('testdata/tr/UTF-8/wikitop_tr_UTF-8.txt', 'UTF-8'),
    ('testdata/tr/ISO-8859-9/wikitop_tr_ISO-8859-9.txt', 'ISO-8859-9'),
    ('testdata/zh/UTF-8/wikitop_zh_UTF-8.txt', 'UTF-8'),
    ('testdata/zh/GB18030/wikitop_zh_GB18030.txt', 'GB18030'),
])
def test_detect(path, encoding):
        with open(data_path(path), 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        assert encoding.lower() == detected_encoding['encoding'].lower()


@pytest.mark.parametrize(
    'detector',
    [chardet.detect, cchardet.detect],
    ids=lambda d: '%s.%s' % (d.__module__, d.func_name)
)
def test_speed(benchmark, detector):
    path = r"testdata/wikipediaJa_One_Thousand_and_One_Nights_SJIS.txt"
    with open(data_path(path), 'rb') as f:
        msg = f.read()

    @benchmark
    def encoding():
        return detector(msg)

    assert encoding['encoding'] == 'SHIFT_JIS'

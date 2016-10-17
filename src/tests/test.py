#!/usr/bin/env python
# coding: utf-8

import sys

from nose.tools import eq_

import cchardet

encodings_map = {
    r'tests/testdata/bg/ISO-8859-5/wikitop_bg_ISO-8859-5.txt': 'ISO-8859-5',
    r'tests/testdata/bg/UTF-8/wikitop_bg_UTF-8.txt': 'UTF-8',
    r'tests/testdata/bg/WINDOWS-1251/wikitop_bg_WINDOWS-1251.txt': 'WINDOWS-1251',
    r'tests/testdata/cz/ISO-8859-2/wikitop_cz_ISO-8859-2.txt': 'ISO-8859-2',
    r'tests/testdata/cz/UTF-8/wikitop_cz_UTF-8.txt': 'UTF-8',
    r'tests/testdata/de/UTF-8/wikitop_de_UTF-8.txt': 'UTF-8',
    r'tests/testdata/de/WINDOWS-1252/wikitop_de_WINDOWS-1252.txt': 'WINDOWS-1252',
    r'tests/testdata/dk/UTF-8/wikitop_dk_UTF-8.txt': 'UTF-8',
    r'tests/testdata/dk/WINDOWS-1252/wikitop_dk_WINDOWS-1252.txt': 'WINDOWS-1252',
    r'tests/testdata/el/ISO-8859-7/wikitop_el_ISO-8859-7.txt': 'ISO-8859-7',
    r'tests/testdata/el/UTF-8/wikitop_el_UTF-8.txt': 'UTF-8',
    r'tests/testdata/en/UTF-8/wikitop_en_UTF-8.txt': 'UTF-8',
    r'tests/testdata/en/WINDOWS-1252/wikitop_en_WINDOWS-1252.txt': 'WINDOWS-1252',
    r'tests/testdata/es/UTF-8/wikitop_es_UTF-8.txt': 'UTF-8',
    r'tests/testdata/es/WINDOWS-1252/wikitop_es_WINDOWS-1252.txt': 'WINDOWS-1252',
    r'tests/testdata/fi/UTF-8/wikitop_fi_UTF-8.txt': 'UTF-8',
    r'tests/testdata/fi/WINDOWS-1252/wikitop_fi_WINDOWS-1252.txt': 'WINDOWS-1252',
    r'tests/testdata/fr/UTF-8/wikitop_fr_UTF-8.txt': 'UTF-8',
    r'tests/testdata/fr/WINDOWS-1252/wikitop_fr_WINDOWS-1252.txt': 'WINDOWS-1252',
    r'tests/testdata/he/UTF-8/wikitop_he_UTF-8.txt': 'UTF-8',
    r'tests/testdata/he/WINDOWS-1255/wikitop_he_WINDOWS-1255.txt': 'WINDOWS-1255',
    r'tests/testdata/hu/UTF-8/wikitop_hu_UTF-8.txt': 'UTF-8',
    r'tests/testdata/hu/ISO-8859-2/wikitop_hu_ISO-8859-2.txt': 'ISO-8859-2',
    r'tests/testdata/it/UTF-8/wikitop_it_UTF-8.txt': 'UTF-8',
    r'tests/testdata/it/WINDOWS-1252/wikitop_it_WINDOWS-1252.txt': 'WINDOWS-1252',
    r'tests/testdata/nl/UTF-8/wikitop_nl_UTF-8.txt': 'UTF-8',
    r'tests/testdata/nl/WINDOWS-1252/wikitop_nl_WINDOWS-1252.txt': 'WINDOWS-1252',
    r'tests/testdata/no/UTF-8/wikitop_no_UTF-8.txt': 'UTF-8',
    r'tests/testdata/no/WINDOWS-1252/wikitop_no_WINDOWS-1252.txt': 'WINDOWS-1252',
    r'tests/testdata/pl/UTF-8/wikitop_pl_UTF-8.txt': 'UTF-8',
    r'tests/testdata/pl/ISO-8859-2/wikitop_pl_ISO-8859-2.txt': 'ISO-8859-2',
    r'tests/testdata/pt/UTF-8/wikitop_pt_UTF-8.txt': 'UTF-8',
    r'tests/testdata/pt/WINDOWS-1252/wikitop_pt_WINDOWS-1252.txt': 'WINDOWS-1252',
    r'tests/testdata/ru/UTF-8/wikitop_ru_UTF-8.txt': 'UTF-8',
    r'tests/testdata/ru/WINDOWS-1251/wikitop_ru_WINDOWS-1251.txt': 'WINDOWS-1251',
    r'tests/testdata/ru/IBM855/wikitop_ru_IBM855.txt': 'IBM855',
    r'tests/testdata/ru/KOI8-R/wikitop_ru_KOI8-R.txt': 'KOI8-R',
    r'tests/testdata/ru/X-MAC-CYRILLIC/wikitop_ru_MACCYRILLIC.txt': 'MAC-CYRILLIC',
    r'tests/testdata/se/UTF-8/wikitop_se_UTF-8.txt': 'UTF-8',
    r'tests/testdata/se/WINDOWS-1252/wikitop_se_WINDOWS-1252.txt': 'WINDOWS-1252',
    r'tests/testdata/th/UTF-8/wikitop_th_UTF-8.txt': 'UTF-8',
    r'tests/testdata/th/TIS-620/utffool_th_TIS-620.txt': 'TIS-620',
    r'tests/testdata/th/TIS-620/wikitop_th_TIS-620.txt': 'TIS-620',
    r'tests/testdata/tr/UTF-8/wikitop_tr_UTF-8.txt': 'UTF-8',
    r'tests/testdata/tr/ISO-8859-9/wikitop_tr_ISO-8859-9.txt': 'ISO-8859-9',
    r'tests/testdata/zh/UTF-8/wikitop_zh_UTF-8.txt': 'UTF-8',
    r'tests/testdata/zh/GB18030/wikitop_zh_GB18030.txt': 'GB18030',
}


class TestCChardet():
    def test_detect(self):
        for path, encoding in encodings_map.items():
            with open(path, 'rb') as f:
                msg = f.read()
                detected_encoding = cchardet.detect(msg)
                eq_(encoding.lower(), detected_encoding['encoding'].lower(), 'Invalid encoding: %s' % path)

    def test_detector(self):
        for path, encoding in encodings_map.items():
            detector = cchardet.Detector()
            with open(path, 'rb') as f:
                line = f.readline()
                while line:
                    detector.feed(line)
                    if detector.done:
                        break
                    line = f.readline()
            detector.close()
            detected_encoding = detector.result
            eq_(encoding.lower(), detected_encoding['encoding'].lower(), 'Invalid encoding: %s' % path)

    def test_detector_noresult(self):
        detector = cchardet.Detector()
        if sys.version_info[0] < 3:
            zero = '0'
        else:
            zero = b'0'
        detector.feed(zero)
        eq_(detector.done, False)
        eq_(detector.result, {'encoding': None, 'confidence': None})

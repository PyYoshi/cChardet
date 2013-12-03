#!/usr/bin/env python
# coding: utf-8

# nosetests --nocapture tests.py
from nose.tools import eq_

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

class TestCchardet():

    def test_detect_bg_iso88595(self):
        encoding = "ISO-8859-5"
        path = r"testdata/bg/ISO-8859-5/wikitop_bg_ISO-8859-5.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_bg_utf8(self):
        encoding = "UTF-8"
        path = r"testdata/bg/UTF-8/wikitop_bg_UTF-8.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_bg_windows1251(self):
        encoding = "WINDOWS-1251"
        path = r"testdata/bg/WINDOWS-1251/wikitop_bg_WINDOWS-1251.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_cz_iso88592(self):
        encoding = "ISO-8859-2"
        path = r"testdata/cz/ISO-8859-2/wikitop_cz_ISO-8859-2.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_cz_utf8(self):
        encoding = "UTF-8"
        path = r"testdata/cz/UTF-8/wikitop_cz_UTF-8.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_de_utf8(self):
        encoding = "UTF-8"
        path = r"testdata/de/UTF-8/wikitop_de_UTF-8.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_de_windows1252(self):
        encoding = "WINDOWS-1252"
        path = r"testdata/de/WINDOWS-1252/wikitop_de_WINDOWS-1252.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_dk_utf8(self):
        encoding = "UTF-8"
        path = r"testdata/dk/UTF-8/wikitop_dk_UTF-8.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_dk_windows1252(self):
        encoding = "WINDOWS-1252"
        path = r"testdata/dk/WINDOWS-1252/wikitop_dk_WINDOWS-1252.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_el_iso88597(self):
        encoding = "ISO-8859-7"
        path = r"testdata/el/ISO-8859-7/wikitop_el_ISO-8859-7.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_el_utf8(self):
        encoding = "UTF-8"
        path = r"testdata/el/UTF-8/wikitop_el_UTF-8.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_en_utf8(self):
        encoding = "UTF-8"
        path = r"testdata/en/UTF-8/wikitop_en_UTF-8.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_en_windows1252(self):
        encoding = "WINDOWS-1252"
        path = r"testdata/en/WINDOWS-1252/wikitop_en_WINDOWS-1252.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_es_utf8(self):
        encoding = "UTF-8"
        path = r"testdata/es/UTF-8/wikitop_es_UTF-8.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_es_windows1252(self):
        encoding = "WINDOWS-1252"
        path = r"testdata/es/WINDOWS-1252/wikitop_es_WINDOWS-1252.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_fi_utf8(self):
        encoding = "UTF-8"
        path = r"testdata/fi/UTF-8/wikitop_fi_UTF-8.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_fi_windows1252(self):
        encoding = "WINDOWS-1252"
        path = r"testdata/fi/WINDOWS-1252/wikitop_fi_WINDOWS-1252.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_fr_utf8(self):
        encoding = "UTF-8"
        path = r"testdata/fr/UTF-8/wikitop_fr_UTF-8.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_fr_windows1252(self):
        encoding = "WINDOWS-1252"
        path = r"testdata/fr/WINDOWS-1252/wikitop_fr_WINDOWS-1252.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_he_utf8(self):
        encoding = "UTF-8"
        path = r"testdata/he/UTF-8/wikitop_he_UTF-8.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_he_windows1255(self):
        encoding = "WINDOWS-1255"
        path = r"testdata/he/WINDOWS-1255/wikitop_he_WINDOWS-1255.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_hu_utf8(self):
        encoding = "UTF-8"
        path = r"testdata/hu/UTF-8/wikitop_hu_UTF-8.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_hu_iso55892(self):
        encoding = "ISO-8859-2"
        path = r"testdata/hu/ISO-8859-2/wikitop_hu_ISO-8859-2.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_it_utf8(self):
        encoding = "UTF-8"
        path = r"testdata/it/UTF-8/wikitop_it_UTF-8.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_it_windows1252(self):
        encoding = "WINDOWS-1252"
        path = r"testdata/it/WINDOWS-1252/wikitop_it_WINDOWS-1252.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_nl_utf8(self):
        encoding = "UTF-8"
        path = r"testdata/nl/UTF-8/wikitop_nl_UTF-8.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_nl_windows1252(self):
        encoding = "WINDOWS-1252"
        path = r"testdata/nl/WINDOWS-1252/wikitop_nl_WINDOWS-1252.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_no_utf8(self):
        encoding = "UTF-8"
        path = r"testdata/no/UTF-8/wikitop_no_UTF-8.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_no_windows1252(self):
        encoding = "WINDOWS-1252"
        path = r"testdata/no/WINDOWS-1252/wikitop_no_WINDOWS-1252.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_pl_utf8(self):
        encoding = "UTF-8"
        path = r"testdata/pl/UTF-8/wikitop_pl_UTF-8.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_pl_iso88592(self):
        encoding = "ISO-8859-2"
        path = r"testdata/pl/ISO-8859-2/wikitop_pl_ISO-8859-2.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_pt_utf8(self):
        encoding = "UTF-8"
        path = r"testdata/pt/UTF-8/wikitop_pt_UTF-8.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_pt_windows1252(self):
        encoding = "WINDOWS-1252"
        path = r"testdata/pt/WINDOWS-1252/wikitop_pt_WINDOWS-1252.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_ru_utf8(self):
        encoding = "UTF-8"
        path = r"testdata/ru/UTF-8/wikitop_ru_UTF-8.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_ru_windows1251(self):
        encoding = "WINDOWS-1251"
        path = r"testdata/ru/WINDOWS-1251/wikitop_ru_WINDOWS-1251.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_ru_ibm855(self):
        encoding = "IBM855"
        path = r"testdata/ru/IBM855/wikitop_ru_IBM855.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_ru_koi8r(self):
        encoding = "KOI8-R"
        path = r"testdata/ru/KOI8-R/wikitop_ru_KOI8-R.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_ru_maccyrillic(self):
        encoding = "MAC-CYRILLIC"
        path = r"testdata/ru/X-MAC-CYRILLIC/wikitop_ru_MACCYRILLIC.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_se_utf8(self):
        encoding = "UTF-8"
        path = r"testdata/se/UTF-8/wikitop_se_UTF-8.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_se_windows1252(self):
        encoding = "WINDOWS-1252"
        path = r"testdata/se/WINDOWS-1252/wikitop_se_WINDOWS-1252.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_th_utf8(self):
        encoding = "UTF-8"
        path = r"testdata/th/UTF-8/wikitop_th_UTF-8.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_th_tis620_1(self):
        encoding = "TIS-620"
        path = r"testdata/th/TIS-620/utffool_th_TIS-620.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_th_tis620_2(self):
        encoding = "TIS-620"
        path = r"testdata/th/TIS-620/wikitop_th_TIS-620.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_tr_utf8(self):
        encoding = "UTF-8"
        path = r"testdata/tr/UTF-8/wikitop_tr_UTF-8.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_tr_iso88599(self):
        encoding = "ISO-8859-9"
        path = r"testdata/tr/ISO-8859-9/wikitop_tr_ISO-8859-9.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_zh_utf8(self):
        encoding = "UTF-8"
        path = r"testdata/zh/UTF-8/wikitop_zh_UTF-8.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        print(detected_encoding)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

    def test_detect_zh_gb18030(self):
        encoding = "GB18030"
        path = r"testdata/zh/GB18030/wikitop_zh_GB18030.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        detected_encoding = cchardet.detect(msg)
        eq_(encoding.lower(),detected_encoding['encoding'].lower())

class TestCchardetSpeed():
    def test_speed(self):
        try:
            import chardet
            has_chardet = True
        except ImportError:
            has_chardet = False
        import time
        do_times = 5
        path = r"testdata/wikipediaJa_One_Thousand_and_One_Nights_SJIS.txt"
        with open(path, 'rb') as f:
            msg = f.read()
        # Test chardet
        if has_chardet:
            result_chardet = 0
            for i in range(do_times):
                start_chardet = time.time()
                chardet.detect(msg)
                result_chardet += (time.time() - start_chardet)
            print('chardet:',1/(result_chardet/do_times), 'call(s)/s')
        # Test cchardet
        result_cchardet = 0
        for i in range(do_times):
            start_cchardet = time.time()
            cchardet.detect(msg)
            result_cchardet += (time.time() - start_cchardet)
        print('cchardet:',1/(result_cchardet/do_times), 'call(s)/s')

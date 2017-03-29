import sys
import glob
import os
import string

from nose.tools import eq_
import cchardet

SKIP_LIST = [
    'tests/testdata/ja/utf-16le.txt',
    'tests/testdata/ja/utf-16be.txt',
    'tests/testdata/es/iso-8859-15.txt',
    'tests/testdata/da/iso-8859-1.txt',
    'tests/testdata/he/iso-8859-8.txt'
]

class TestCChardet():
    def test_ascii(self):
        detected_encoding = cchardet.detect(b'abcdefghijklmnopqrstuvwxyz')
        eq_(
            'ascii',
            detected_encoding['encoding'].lower(),
            'Expected %s, but got %s' % (
                'ascii',
                detected_encoding['encoding'].lower()
            )
        )

    def test_detect(self):
        testfiles = glob.glob('tests/testdata/*/*.txt')
        for testfile in testfiles:
            if testfile.replace("\\", "/") in SKIP_LIST:
                continue

            base = os.path.basename(testfile)
            expected_charset = os.path.splitext(base)[0]
            with open(testfile, 'rb') as f:
                msg = f.read()
                detected_encoding = cchardet.detect(msg)
                eq_(
                    expected_charset.lower(),
                    detected_encoding['encoding'].lower(),
                    'Expected %s, but got %s for "%s"' % (
                        expected_charset.lower(),
                        detected_encoding['encoding'].lower(),
                        testfile
                    )
                )

    def test_detector(self):
        detector = cchardet.UniversalDetector()
        with open("tests/samples/wikipediaJa_One_Thousand_and_One_Nights_SJIS.txt", 'rb') as f:
            print("===============================")
            line = f.readline()
            while line:
                detector.feed(line)
                if detector.done:
                    break
                line = f.readline()
        detector.close()
        detected_encoding = detector.result
        eq_(
            "shift_jis",
            detected_encoding['encoding'].lower(),
            'Expected %s, but got %s' % (
                "shift_jis",
                detected_encoding['encoding'].lower()
            )
        )

import glob
import os

import cchardet

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

SKIP_LIST = [
    "testdata/ja/utf-16le.txt",
    "testdata/ja/utf-16be.txt",
    "testdata/es/iso-8859-15.txt",
    "testdata/da/iso-8859-1.txt",
    "testdata/he/iso-8859-8.txt",
]

# Python can"t decode encoding
SKIP_LIST_02 = [
    "testdata/vi/viscii.txt",
    "testdata/zh/euc-tw.txt",
]
SKIP_LIST_02.extend(SKIP_LIST)


class TestCChardet:
    def test_ascii(self):
        detected_encoding = cchardet.detect(b"abcdefghijklmnopqrstuvwxyz")
        assert "ascii" == detected_encoding["encoding"].lower(), "Expected %s, but got %s" % (
            "ascii",
            detected_encoding["encoding"].lower(),
        )

    def test_detect(self):
        testfiles = glob.glob(SCRIPT_DIR + "/testdata/*/*.txt")
        for testfile in testfiles:
            if any(testfile.replace("\\", "/").endswith(skip) for skip in SKIP_LIST):
                print("Skip: %s" % testfile)
                continue

            base = os.path.basename(testfile)
            expected_charset = os.path.splitext(base)[0]
            with open(testfile, "rb") as f:
                msg = f.read()
                detected_encoding = cchardet.detect(msg)
                print("Test %s: %s" % (testfile, detected_encoding))
                assert detected_encoding["encoding"] is not None, (
                    'Expected %s, but got None for "%s"' % (expected_charset.lower(), testfile)
                )
                assert expected_charset.lower() == detected_encoding["encoding"].lower(), (
                    'Expected %s, but got %s for "%s"'
                    % (expected_charset.lower(), detected_encoding["encoding"].lower(), testfile)
                )

    def test_detector(self):
        detector = cchardet.UniversalDetector()
        with open(
            os.path.join(SCRIPT_DIR, "samples/wikipediaJa_One_Thousand_and_One_Nights_SJIS.txt"),
            "rb",
        ) as f:
            line = f.readline()
            while line:
                detector.feed(line)
                if detector.done:
                    break
                line = f.readline()
        detector.close()
        detected_encoding = detector.result
        assert "shift_jis" == detected_encoding["encoding"].lower(), "Expected %s, but got %s" % (
            "shift_jis",
            detected_encoding["encoding"].lower(),
        )

    def test_github_issue_20(self):
        """
        https://github.com/PyYoshi/cChardet/issues/20
        """
        msg = b"\x8f"

        cchardet.detect(msg)

        detector = cchardet.UniversalDetector()
        detector.feed(msg)
        detector.close()

    def test_decode(self):
        testfiles = glob.glob(SCRIPT_DIR + "/testdata/*/*.txt")
        for testfile in testfiles:
            if any(testfile.replace("\\", "/").endswith(skip) for skip in SKIP_LIST_02):
                print("Skip: %s" % testfile)
                continue

            with open(testfile, "rb") as f:
                msg = f.read()
                detected_encoding = cchardet.detect(msg)
                try:
                    msg.decode(detected_encoding["encoding"])
                except LookupError as e:
                    print(
                        "LookupError: { file=%s, encoding=%s }"
                        % (testfile, detected_encoding["encoding"])
                    )
                    raise e

    def test_utf8_with_bom(self):
        sample = b"\xef\xbb\xbf"
        detected_encoding = cchardet.detect(sample)
        assert "utf-8-sig" == detected_encoding["encoding"].lower(), "Expected %s, but got %s" % (
            "utf-8-sig",
            detected_encoding["encoding"].lower(),
        )

    def test_null_bytes(self):
        sample = b"ABC\x00\x80\x81"
        detected_encoding = cchardet.detect(sample)

        assert detected_encoding["encoding"] is None, (
            "Expected None, but got %s" % (detected_encoding["encoding"])
        )

import glob
import os

import cchardet

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
TESTDATA_DIR = os.path.join(SCRIPT_DIR, "..", "src", "ext", "uchardet", "test")

SKIP_LIST_DETECT = [
    "zh/gb18030.txt",

    # These are tests known to fail (not supported or not efficient
    # enough). We will have to take a closer look and fix these, but
    # there is no need to break the whole `make test` right now,
    # which may make actual regressions harder to notice.
    "ja/utf-16le.txt",
    "ja/utf-16be.txt",
    "es/iso-8859-15.txt",
    "da/iso-8859-1.txt",
    "he/iso-8859-8.txt",
]

# Python can"t decode encoding
SKIP_LIST_DEC = [
    "ka/georgian-academy.txt",
    "ka/georgian-ps.txt",
    "vi/viscii.txt",
    "zh/euc-tw.txt",
]
SKIP_LIST_DEC.extend(SKIP_LIST_DETECT)

class TestCChardet:
    def test_ascii(self):
        detected_encoding = cchardet.detect(b"abcdefghijklmnopqrstuvwxyz")
        got_enc = None
        if detected_encoding["encoding"] is not None:
            got_enc = detected_encoding["encoding"].lower()
        assert "ascii" == got_enc, "Expected %s, but got %s" % (
            "ascii",
            got_enc,
        )

    def test_detect(self):
        testfiles = glob.glob(TESTDATA_DIR + "/*/*.txt")
        for testfile in testfiles:
            if any(testfile.replace("\\", "/").endswith(skip) for skip in SKIP_LIST_DETECT):
                print("Skip: %s" % testfile)
                continue

            base = os.path.basename(testfile)
            expected_charset = os.path.splitext(base)[0]
            expected_charset = expected_charset.split(".")[0]
            if expected_charset == "mac-centraleurope":
                expected_charset = "maccentraleurope"
            with open(testfile, "rb") as f:
                msg = f.read()
                detected_encoding = cchardet.detect(msg)
                print("Test %s: %s" % (testfile, detected_encoding))
                got_enc = None
                if detected_encoding["encoding"] is not None:
                    got_enc = detected_encoding["encoding"].lower()
                assert got_enc is not None, (
                    'Expected %s, but got None for "%s"' % (expected_charset.lower(), testfile)
                )
                assert expected_charset.lower() == got_enc, (
                    'Expected %s, but got %s for "%s"'
                    % (expected_charset.lower(), got_enc, testfile)
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
        got_enc = None
        if detected_encoding["encoding"] is not None:
            got_enc = detected_encoding["encoding"].lower()
        assert "shift_jis" == got_enc, "Expected %s, but got %s" % (
            "shift_jis",
            got_enc,
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
        testfiles = glob.glob(TESTDATA_DIR + "/*/*.txt")
        for testfile in testfiles:
            if any(testfile.replace("\\", "/").endswith(skip) for skip in SKIP_LIST_DEC):
                print("Skip: %s" % testfile)
                continue

            with open(testfile, "rb") as f:
                msg = f.read()
                detected_encoding = cchardet.detect(msg)
                print("Test %s: %s" % (testfile, detected_encoding))
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
        got_enc = None
        if detected_encoding["encoding"] is not None:
            got_enc = detected_encoding["encoding"].lower()
        assert "utf-8" == got_enc, "Expected %s, but got %s" % (
            "utf-8",
            got_enc,
        )

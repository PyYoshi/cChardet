import glob
import os
import sys
import sysconfig
from concurrent.futures import ThreadPoolExecutor

import cchardet

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
TESTDATA_DIR = os.path.join(SCRIPT_DIR, "..", "src", "ext", "uchardet", "test")

SKIP_LIST_DETECT = [
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
    def test_free_threaded_build_keeps_gil_disabled(self):
        if sysconfig.get_config_var("Py_GIL_DISABLED"):
            assert not getattr(sys, "_is_gil_enabled")()

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
                assert got_enc is not None, 'Expected %s, but got None for "%s"' % (
                    expected_charset.lower(),
                    testfile,
                )
                assert expected_charset.lower() == got_enc, 'Expected %s, but got %s for "%s"' % (
                    expected_charset.lower(),
                    got_enc,
                    testfile,
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

    def test_detector_can_reset_after_close(self):
        detector = cchardet.UniversalDetector()
        detector.feed(b"plain ASCII")
        assert not detector.done
        detector.close()
        assert detector.done
        assert detector.result["encoding"] == "ASCII"

        detector.reset()
        assert not detector.done
        detector.feed("日本語".encode())
        detector.close()
        assert detector.result["encoding"] == "UTF-8"

    def test_detector_exposes_uchardet_early_completion(self):
        path = os.path.join(TESTDATA_DIR, "be/utf-8.txt")
        with open(path, "rb") as file:
            data = file.read()

        detector = cchardet.UniversalDetector()
        detector.feed(data)

        assert detector.done
        assert detector.result == cchardet.detect(data)

    def test_detect_is_thread_safe(self):
        samples = [b"plain ASCII", "日本語".encode(), "français".encode()]

        def detect_results(sample):
            return cchardet.detect(sample), cchardet.detect_all(sample)

        expected = [detect_results(sample) for sample in samples]
        repeated_samples = samples * 100
        with ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(detect_results, repeated_samples))
        assert results == expected * 100

    def test_detect_max_bytes(self):
        data = b"plain ASCII" + "日本語".encode()
        assert cchardet.detect(data, max_bytes=11)["encoding"] == "ASCII"
        assert cchardet.detect(data, max_bytes=0)["encoding"] is None
        try:
            cchardet.detect(data, max_bytes=-1)
        except ValueError:
            pass
        else:
            raise AssertionError("negative max_bytes must be rejected")

    def test_detect_all_includes_language(self):
        path = os.path.join(TESTDATA_DIR, "fr/windows-1252.txt")
        with open(path, "rb") as file:
            data = file.read()
        best = cchardet.detect(data)
        candidates = cchardet.detect_all(data)
        assert candidates[0] == best
        assert best["language"] == "fr"
        assert all(
            left["confidence"] >= right["confidence"]
            for left, right in zip(candidates, candidates[1:])
        )

    def test_language_weights_are_opt_in_and_persist_across_reset(self):
        path = os.path.join(TESTDATA_DIR, "ar/utf-8.txt")
        with open(path, "rb") as file:
            data = file.read()

        assert cchardet.detect(data)["language"] == "ar"
        weighted = cchardet.detect(data, language_weights={"AR": 0.1})
        assert weighted["language"] == "zh"

        detector = cchardet.UniversalDetector(language_weights={"ar": 0.1})
        for _ in range(2):
            detector.feed(data)
            detector.close()
            assert detector.result == weighted
            detector.reset()

    def test_language_weights_are_validated(self):
        for weights in ({"english": 1.0}, {"en": -0.1}, {"en": 1.1}, {"en": float("nan")}):
            try:
                cchardet.detect(b"plain ASCII", language_weights=weights)
            except ValueError:
                pass
            else:
                raise AssertionError(f"invalid language weights accepted: {weights}")

    def test_bytes_like_inputs(self):
        expected = cchardet.detect(b"plain ASCII")
        assert cchardet.detect(bytearray(b"plain ASCII")) == expected
        assert cchardet.detect(memoryview(b"plain ASCII")) == expected

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

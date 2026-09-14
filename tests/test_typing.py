from typing import assert_type

import cchardet


def test_public_api_types() -> None:
    result = cchardet.detect(memoryview(b"plain ASCII"), max_bytes=32)
    assert_type(result, cchardet.ResultDict)
    assert_type(result["encoding"], str | None)
    assert_type(result["confidence"], float | None)
    assert_type(result["language"], str | None)

    candidates = cchardet.detect_all(bytearray(b"plain ASCII"))
    assert_type(candidates, list[cchardet.ResultDict])

    with cchardet.UniversalDetector() as detector:
        detector.feed(b"plain ASCII")
    assert_type(detector.done, bool)
    assert_type(detector.result, cchardet.ResultDict)

import random

import cchardet


def test_one_shot_and_incremental_detection_are_consistent() -> None:
    random_source = random.Random(0)
    for _ in range(200):
        data = random_source.randbytes(random_source.randrange(4097))
        expected = cchardet.detect(data)

        detector = cchardet.UniversalDetector()
        offset = 0
        while offset < len(data):
            chunk_size = random_source.randrange(1, 128)
            detector.feed(data[offset : offset + chunk_size])
            offset += chunk_size
        detector.close()

        assert detector.result == expected


def test_detector_lifecycle_is_idempotent() -> None:
    detector = cchardet.UniversalDetector()
    detector.close()
    detector.close()
    assert detector.done
    assert detector.result == {"encoding": None, "confidence": None, "language": None}

    detector.reset()
    detector.feed(b"plain ASCII")
    detector.close()
    assert detector.result["encoding"] == "ASCII"

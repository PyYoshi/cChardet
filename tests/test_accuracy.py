from pathlib import Path

from benchmarks.accuracy import _evaluate, _normalize_language, _uchardet_samples


def test_normalize_language_names_and_codes() -> None:
    assert _normalize_language("fr") == "fr"
    assert _normalize_language("French") == "fr"
    assert _normalize_language("Japanese") == "ja"
    assert _normalize_language(None) is None
    assert _normalize_language("Unknown") is None


def test_uchardet_samples_derive_encoding_and_language(tmp_path: Path) -> None:
    sample = tmp_path / "fr" / "windows-1252.txt"
    sample.parent.mkdir()
    sample.write_bytes(b"sample")

    assert _uchardet_samples(tmp_path) == [("windows-1252", "fr", sample)]


def test_evaluate_reports_language_and_joint_accuracy(tmp_path: Path) -> None:
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    first.write_bytes(b"first")
    second.write_bytes(b"second")
    samples = [("utf-8", "fr", first), ("utf-8", "ja", second)]

    def detector(data: bytes) -> dict[str, object]:
        language = "French" if data == b"first" else None
        return {"encoding": "UTF-8", "language": language}

    result = _evaluate(detector, samples)

    assert result["compatible"] == 2
    assert result["language_correct"] == 1
    assert result["language_no_result"] == 1
    assert result["joint_correct"] == 1
    assert result["language_correct_percent"] == 50.0

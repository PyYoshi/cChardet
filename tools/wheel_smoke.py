"""Exercise the installed wheel rather than the source checkout."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import cchardet


def main() -> None:
    package_dir = Path(cchardet.__file__).parent
    assert (package_dir / "py.typed").is_file()
    assert (package_dir / "_cchardet.pyi").is_file()

    expected = cchardet.detect(b"plain ASCII")
    assert expected["encoding"] == "ASCII"
    assert cchardet.detect(bytearray(b"plain ASCII")) == expected
    assert cchardet.detect(memoryview(b"plain ASCII"), max_bytes=32) == expected

    french = ("Fran\u00e7ais, o\u00f9 \u00eates-vous ? Voil\u00e0 l'\u00e9t\u00e9.").encode(
        "windows-1252"
    )
    candidates = cchardet.detect_all(french)
    assert candidates
    assert candidates[0] == cchardet.detect(french)
    assert candidates[0]["language"] == "fr"

    detector = cchardet.UniversalDetector()
    detector.feed(french[:10])
    detector.feed(french[10:])
    detector.close()
    assert detector.result == candidates[0]

    with tempfile.TemporaryDirectory() as directory:
        sample = Path(directory) / "sample.txt"
        sample.write_bytes(french)
        output = subprocess.check_output(
            [sys.executable, "-m", "cchardet", "--json", str(sample)],
            text=True,
        )
        assert json.loads(output)["language"] == "fr"


if __name__ == "__main__":
    main()

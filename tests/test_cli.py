import argparse
import json
from io import BytesIO

import pytest

from cchardet.cli.cchardetect import language_weight, main, read_chunks


def test_read_chunks_respects_max_bytes():
    assert b"".join(read_chunks(BytesIO(b"abcdefgh"), 3, 5)) == b"abcde"


def test_json_output_and_max_bytes(monkeypatch, capsys, tmp_path):
    sample = tmp_path / "sample.txt"
    sample.write_bytes(b"plain ASCII" + "日本語".encode())
    monkeypatch.setattr(
        "sys.argv",
        ["cchardetect", "--json", "--max-bytes", "11", str(sample)],
    )

    main()

    result = json.loads(capsys.readouterr().out)
    assert result["path"] == str(sample)
    assert result["encoding"] == "ASCII"
    assert result["language"] is None


def test_language_weight_option(monkeypatch, capsys, tmp_path):
    sample = tmp_path / "sample.txt"
    sample.write_bytes("Беларуская мова і літаратура. Гэта доўгі тэкст.".encode())
    monkeypatch.setattr(
        "sys.argv",
        ["cchardetect", "--json", "--language-weight", "be=0", str(sample)],
    )

    main()

    result = json.loads(capsys.readouterr().out)
    assert result["language"] != "be"


def test_language_weight_parser_normalizes_language_code():
    assert language_weight("FR=0.25") == ("fr", 0.25)


@pytest.mark.parametrize("value", ["fr", "fra=0.5", "fr=-1", "fr=nan"])
def test_language_weight_parser_rejects_invalid_values(value):
    with pytest.raises(argparse.ArgumentTypeError):
        language_weight(value)

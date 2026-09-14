import json
from io import BytesIO

from cchardet.cli.cchardetect import main, read_chunks


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

import argparse
import json
import sys
from pathlib import Path
from typing import BinaryIO, Iterator

from .. import UniversalDetector, __version__


def read_chunks(
    file: BinaryIO, chunk_size: int, max_bytes: int | None = None
) -> Iterator[bytes]:
    remaining = max_bytes
    while remaining is None or remaining > 0:
        read_size = chunk_size if remaining is None else min(chunk_size, remaining)
        chunk = file.read(read_size)
        if not chunk:
            break
        yield chunk
        if remaining is not None:
            remaining -= len(chunk)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "files",
        nargs="*",
        help="Files to detect encoding of",
        type=Path,
    )
    parser.add_argument("--chunk-size", type=int, default=(256 * 1024))
    parser.add_argument("--max-bytes", type=int)
    parser.add_argument("--json", action="store_true", help="emit one JSON object per input")
    parser.add_argument("--version", action="version", version="%(prog)s {0}".format(__version__))
    args = parser.parse_args()
    if args.chunk_size < 1:
        parser.error("--chunk-size must be at least 1")
    if args.max_bytes is not None and args.max_bytes < 0:
        parser.error("--max-bytes must be non-negative")

    paths = args.files or [None]
    for path in paths:
        file = sys.stdin.buffer if path is None else path.open("rb")
        display_path = "<stdin>" if path is None else str(path)
        try:
            detector = UniversalDetector()
            for chunk in read_chunks(file, args.chunk_size, args.max_bytes):
                detector.feed(chunk)
            detector.close()
            result = detector.result
            if args.json:
                print(json.dumps({"path": display_path, **result}, sort_keys=True))
            else:
                language = f" ({result['language']})" if result["language"] else ""
                print(
                    f"{display_path}: {result['encoding']}{language} with confidence "
                    f"{result['confidence']}"
                )
        finally:
            if path is not None:
                file.close()


if __name__ == "__main__":
    main()

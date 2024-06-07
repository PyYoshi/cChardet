import argparse
import sys

from .. import UniversalDetector, __version__


def read_chunks(f, chunk_size):
    chunk = f.read(chunk_size)
    while chunk:
        yield chunk
        chunk = f.read(chunk_size)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "files",
        nargs="*",
        help="Files to detect encoding of",
        type=argparse.FileType("rb"),
        default=[sys.stdin.buffer],
    )
    parser.add_argument("--chunk-size", type=int, default=(256 * 1024))
    parser.add_argument("--version", action="version", version="%(prog)s {0}".format(__version__))
    args = parser.parse_args()

    for f in args.files:
        detector = UniversalDetector()
        for chunk in read_chunks(f, args.chunk_size):
            detector.feed(chunk)
        detector.close()
        print(
            "{file.name}: {result[encoding]} with confidence {result[confidence]}".format(
                file=f, result=detector.result
            )
        )


if __name__ == "__main__":
    main()

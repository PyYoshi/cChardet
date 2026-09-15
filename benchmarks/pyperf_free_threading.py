"""Compare cChardet throughput with regular and free-threaded CPython.

Install cChardet into each interpreter before running this script.  Corpus
files are content-deduplicated and loaded before pyperf starts timing.
"""

from __future__ import annotations

import hashlib
import sys
import sysconfig
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import pyperf

import cchardet


def _load_corpus(roots: list[Path]) -> list[bytes]:
    paths = sorted(
        {
            path
            for root in roots
            for path in ([root] if root.is_file() else root.rglob("*"))
            if path.is_file() and not any(part.startswith(".") for part in path.parts)
        }
    )
    if not paths:
        raise ValueError(f"no corpus files found under {roots}")
    unique: dict[bytes, bytes] = {}
    for path in paths:
        data = path.read_bytes()
        unique.setdefault(hashlib.sha256(data).digest(), data)
    return list(unique.values())


def _detect_batch(batch: list[bytes]) -> int:
    return sum(cchardet.detect(data)["encoding"] is not None for data in batch)


def _serial(corpus: list[bytes]) -> int:
    return _detect_batch(corpus)


def _parallel(executor: ThreadPoolExecutor, batches: list[list[bytes]]) -> int:
    return sum(executor.map(_detect_batch, batches))


def _add_worker_args(cmd: list[str], args: Any) -> None:
    for root in args.corpus or ():
        cmd.extend(("--corpus", str(root)))


def main() -> None:
    runner = pyperf.Runner(add_cmdline_args=_add_worker_args)
    runner.argparser.add_argument(
        "--corpus",
        action="append",
        type=Path,
        default=None,
        help="input file or directory (repeatable)",
    )
    args = runner.parse_args()
    roots = args.corpus or [Path("src/ext/uchardet/test"), Path("tests/samples")]
    corpus = _load_corpus(roots)
    gil_enabled = getattr(sys, "_is_gil_enabled", lambda: True)()
    runner.metadata.update(
        {
            "cchardet_version": cchardet.__version__,
            "cchardet_module": str(Path(cchardet.__file__).resolve()),
            "free_threaded_build": bool(sysconfig.get_config_var("Py_GIL_DISABLED")),
            "gil_enabled": gil_enabled,
            "corpus": ":".join(str(root.resolve()) for root in roots),
            "corpus_files": len(corpus),
            "corpus_bytes": sum(map(len, corpus)),
        }
    )

    _serial(corpus)
    runner.bench_func("cchardet: serial corpus", _serial, corpus)

    batches = [corpus[offset::4] for offset in range(4)]
    with ThreadPoolExecutor(max_workers=4) as executor:
        _parallel(executor, batches)
        runner.bench_func("cchardet: 4-thread corpus", _parallel, executor, batches)


if __name__ == "__main__":
    main()

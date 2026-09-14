"""Process-isolated cChardet, chardet, and charset-normalizer benchmark.

The corpus is read before timing in every pyperf worker. Pass ``--corpus``
more than once to combine inputs. Source checkout overrides can be supplied
with repeatable ``--pythonpath`` options.
"""

from __future__ import annotations

import hashlib
import importlib
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import pyperf


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


def _detect_batch(detector: Any, batch: list[bytes]) -> int:
    return sum(detector(data).get("encoding") is not None for data in batch)


def _serial(detector: Any, corpus: list[bytes]) -> int:
    return _detect_batch(detector, corpus)


def _parallel(
    executor: ThreadPoolExecutor,
    detector: Any,
    batches: list[list[bytes]],
) -> int:
    return sum(executor.map(lambda batch: _detect_batch(detector, batch), batches))


def _implementation_metadata() -> tuple[dict[str, Any], dict[str, str]]:
    cchardet = importlib.import_module("cchardet")
    chardet = importlib.import_module("chardet")
    charset_normalizer = importlib.import_module("charset_normalizer")
    kernel = importlib.import_module("chardet._kernel")
    mess_detector = importlib.import_module("charset_normalizer.md")
    coherence_detector = importlib.import_module("charset_normalizer.cd")
    modules = {
        "cchardet": cchardet,
        "chardet": chardet,
        "charset_normalizer": charset_normalizer,
    }
    metadata = {
        "cchardet_version": cchardet.__version__,
        "cchardet_module": str(Path(cchardet.__file__).resolve()),
        "chardet_version": chardet.__version__,
        "chardet_module": str(Path(chardet.__file__).resolve()),
        "charset_normalizer_version": charset_normalizer.__version__,
        "charset_normalizer_module": str(Path(charset_normalizer.__file__).resolve()),
        "chardet_kernel": str(Path(kernel.__file__).resolve()),
        "charset_normalizer_mess": str(Path(mess_detector.__file__).resolve()),
        "charset_normalizer_coherence": str(Path(coherence_detector.__file__).resolve()),
    }
    return {name: module.detect for name, module in modules.items()}, metadata


def _add_worker_args(cmd: list[str], args: Any) -> None:
    for root in args.corpus or ():
        cmd.extend(("--corpus", str(root)))
    for root in args.pythonpath or ():
        cmd.extend(("--pythonpath", str(root)))


def main() -> None:
    runner = pyperf.Runner(add_cmdline_args=_add_worker_args)
    runner.argparser.add_argument(
        "--corpus",
        action="append",
        type=Path,
        default=None,
        help="input file or directory (repeatable)",
    )
    runner.argparser.add_argument(
        "--pythonpath",
        action="append",
        type=Path,
        default=None,
        help="prepend a source tree when measuring a pure-Python fallback",
    )
    args = runner.parse_args()
    for root in reversed(args.pythonpath or ()):
        sys.path.insert(0, str(root.resolve()))
    roots = args.corpus or [
        Path("src/ext/uchardet/test"),
        Path("tests/samples"),
        Path("../charset_normalizer/data"),
    ]
    corpus = _load_corpus(roots)
    detectors, metadata = _implementation_metadata()
    metadata.update(
        {
            "corpus": ":".join(str(root.resolve()) for root in roots),
            "corpus_files": len(corpus),
            "corpus_bytes": sum(map(len, corpus)),
        }
    )
    runner.metadata.update(metadata)
    for name, detector in detectors.items():
        _serial(detector, corpus)
        runner.bench_func(f"{name}: serial corpus", _serial, detector, corpus)

        batches = [corpus[offset::4] for offset in range(4)]
        with ThreadPoolExecutor(max_workers=4) as executor:
            _parallel(executor, detector, batches)
            runner.bench_func(
                f"{name}: 4-thread corpus",
                _parallel,
                executor,
                detector,
                batches,
            )


if __name__ == "__main__":
    main()

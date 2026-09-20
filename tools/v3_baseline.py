# SPDX-License-Identifier: MIT
"""Record native fixture/model provenance and optional isolated benchmark runs."""

import argparse
import hashlib
import json
import os
import platform
import subprocess
from pathlib import Path


def command(*args: str) -> str:
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT).strip()


def inventory(root: Path, paths: list[Path]) -> list[dict[str, object]]:
    return [
        {
            "path": p.relative_to(root).as_posix(),
            "bytes": p.stat().st_size,
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
        }
        for p in sorted(paths)
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native", type=Path, default=Path("src/ext/uchardet"))
    parser.add_argument("--build", type=Path, required=True)
    parser.add_argument("--benchmark", action="store_true")
    parser.add_argument("--cpu", type=int)
    parser.add_argument("--iterations", type=int, default=100)
    args = parser.parse_args()
    if args.iterations < 1:
        parser.error("iterations must be positive")
    if args.cpu is not None:
        if not hasattr(os, "sched_setaffinity"):
            parser.error("CPU affinity is unavailable on this platform")
        os.sched_setaffinity(0, {args.cpu})
    root = args.native.resolve()
    build = args.build.resolve()
    fixtures = sorted(p for p in root.glob("test/[a-z][a-z]/*") if p.is_file())
    if not fixtures:
        parser.error("native fixture inventory is empty")
    cache = build / "CMakeCache.txt"
    executable = build / "benchmark/uchardet-benchmark"
    report = {
        "schema_version": 1,
        "native_commit": command("git", "-C", str(root), "rev-parse", "HEAD"),
        "native_dirty": command("git", "-C", str(root), "status", "--porcelain"),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python": platform.python_version(),
        "affinity": sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None,
        "fixtures": inventory(root, fixtures),
        "models": inventory(root, list(root.glob("src/LangModels/*.cpp"))),
        "cmake_cache": cache.read_text(),
        "benchmark_sha256": hashlib.sha256(executable.read_bytes()).hexdigest(),
        "timings": [],
    }
    report["fixture_manifest_sha256"] = hashlib.sha256(
        json.dumps(report["fixtures"], sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if args.benchmark:
        for mode in ("fresh", "reuse"):
            for chunk in (0, 64):
                argv = [str(executable), mode, str(args.iterations), str(chunk)]
                files = [str(p) for p in fixtures]
                # Separate untimed process warm-up; the executable also warms its loop.
                command(str(executable), mode, "1", str(chunk), *files)
                report["timings"].append({"command": argv, "output": command(*argv, *files)})
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

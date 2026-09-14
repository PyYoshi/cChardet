# Detector and performance analysis

This document records a local comparison made on 2026-09-15. It is intended
to make optimization decisions reproducible, rather than to present portable
headline numbers. The machine used an AMD Ryzen 7 8845HS (8 cores/16 threads)
and CPython 3.14.

## Implementations reviewed

### chardet

The current chardet implementation is a staged detector rather than the old
collection of Python ports of Mozilla probers. Its important performance
techniques are:

- definitive BOM, UTF, escape, magic-number, and markup checks before
  statistical work;
- a 200 KB default input limit, a smaller shared evidence window, and a 16 KB
  statistical-scoring window;
- compact dense bigram models, upper-bound pruning, and reuse of structural
  scores between stages;
- C-speed Python primitives such as `bytes.translate()` for byte scans;
- an optional compiled scoring kernel, while retaining a pure-Python path.

Its main advantage over cChardet is breadth and accuracy. Current wheels use a
mypyc-compiled kernel when one is available, so it must not be described or
benchmarked only as Pure Python.

### charset-normalizer

charset-normalizer avoids exhaustive whole-input work by sampling five
512-character regions by default. It prioritizes BOMs, declarations, ASCII,
and UTF-8, lazily decodes large inputs, caches mess/coherence calculations,
and stops testing unrelated single-byte families after a convincing
multibyte result. Its source remains usable as pure Python; published wheels
may use its optional Cython acceleration.

This makes its runtime less dependent on input length than an exhaustive
detector, although candidate decoding and language coherence are still
relatively expensive on the uchardet corpus.

### cChardet and uchardet

cChardet delegates the statistical work to native C++ and has a very small
Python API. This remains a clear advantage for small and medium inputs. The
weaknesses are that it examines the caller's entire buffer by default and
inherits uchardet's narrower encoding model set and known ambiguities.

The vendored source was the PyYoshi fork's `master` at `edae8e8` from 2023.
The header and implementation at that commit are byte-for-byte identical in
the fork and the official GitLab history: multiple candidates, confidence,
language results, weights, newer models, and the earlier safety fixes had
already gone upstream. The PyYoshi fork's `cchardet` branch was rebuilt from
official commit `06029ec` from 2025. The upstream four-commit delta changes no
detector model or C API; it adds an MSVC macro fix, a file-close fix, a CLI
default-language option, and a CMake minimum-version update. The previous fork
history remains available as `obsoleted-cchardet`, making both the upstream
base and cChardet-specific commits explicit.

The fork adds two focused fixes. The UTF-8 prober now rejects state-machine
errors instead of treating invalid bytes as continuation data. When UTF-8 is
therefore structurally rejected, a saturated GB18030 distribution is
calibrated strongly enough to beat an accidental single-byte match, but not
strongly enough to trigger early termination. This fixes the Chinese fixture
previously ranked below Macedonian/Windows-1251. The fork passes all 153
enabled uchardet tests; upstream `06029ec` passed 152. Across the two external
accuracy corpora the only three changed top results are corrections (one
GB18030 and two GB2312-compatible inputs), with no observed regression. GCC
additionally warns that `st` may be uninitialized in
`nsMBCSGroupProber::HandleData`; control-flow inspection suggests the relevant
positive-length loop always assigns it, but initializing it explicitly should
be proposed upstream to make that invariant unambiguous.

## Reproducible performance benchmark

`pyperf_compare.py` preloads and content-deduplicates the same files in every
worker, warms every detector, and records exact imported module paths. The
paths prove whether chardet's mypyc kernel and charset-normalizer's Cython
modules were loaded. A 166-file, 641,202-byte union of the three repositories'
fixtures was measured on CPython 3.14.2 with CPU affinity fixed to cores 4–7.

Optimized release wheels (`chardet 7.6.0`, `charset-normalizer 3.5.1`):

| Detector | Serial corpus | 4-thread corpus | 4-thread scaling |
|---|---:|---:|---:|
| cChardet 2.2.0a3 (Cython/C++) | 92.0 ms | 42.1 ms | 2.19x |
| chardet 7.6.0 (mypyc) | 129 ms | 209 ms | 0.62x |
| charset-normalizer 3.5.1 (Cython) | 88.7 ms | 110 ms | 0.81x |

The key result is that optimized charset-normalizer is slightly faster than
cChardet in this serial workload. cChardet is no longer categorically the
fastest detector. Releasing the GIL around each native detection does retain a
clear advantage for concurrent independent buffers.

Pure fallback paths from the sibling source checkouts, on the same corpus:

| Detector | Serial corpus | 4-thread corpus | 4-thread scaling |
|---|---:|---:|---:|
| cChardet 2.2.0a3 (Cython/C++) | 92.4 ms | 42.2 ms | 2.19x |
| chardet 7.6.1.dev32 (Python kernel) | 549 ms | 1.01 s | 0.54x |
| charset-normalizer 3.5.1 (`md.py`/`cd.py`) | 493 ms | 811 ms | 0.61x |

The thread measurements for both Python fallbacks are noisy because GIL
contention is itself workload-dependent; their slowdown, rather than an exact
ratio, is the useful conclusion. To reproduce the optimized-wheel run:

```bash
uv run --no-sync python benchmarks/pyperf_compare.py \
  --corpus src/ext/uchardet/test --corpus tests/samples \
  --corpus ../charset_normalizer/data --rigorous -o optimized.json
```

To exercise both sibling pure-Python checkouts without uninstalling the
optimized wheels:

```bash
uv run --no-sync python benchmarks/pyperf_compare.py \
  --pythonpath ../chardet/src --pythonpath ../charset_normalizer/src \
  --corpus src/ext/uchardet/test --corpus tests/samples \
  --corpus ../charset_normalizer/data --rigorous -o pure.json
```

`setup.py build_ext --inplace` was run in the locked uv environment before the
measurements, followed by `uv run --no-sync`, so uv's editable-package sync
cannot replace the extension while pyperf child processes are starting.

## Accuracy benchmark

Performance without accuracy is misleading. `accuracy.py` applies the same
three chardet evaluation predicates to every detector and reports each corpus
separately, avoiding a detector's own corpus being hidden in one aggregate
score. All three optimized modules listed above were loaded. The measured
revisions were chardet/test-data `b0c0d206`, Ousret/char-dataset `f9e293f2`,
and the bundled uchardet corpus at submodule revision `02d7e7a`.

| Corpus / detector | Exact alias-normalized | Compatible/superset | Decode-equivalent |
|---|---:|---:|---:|
| uchardet test-data (158): cChardet | 93.67% | 94.30% | 95.57% |
| uchardet test-data (158): chardet | 78.48% | 85.44% | 88.61% |
| uchardet test-data (158): charset-normalizer | 60.13% | 72.15% | 75.32% |
| chardet test-data (3,138): cChardet | 47.13% | 49.46% | 54.21% |
| chardet test-data (3,138): chardet | 91.91% | 94.46% | 99.46% |
| chardet test-data (3,138): charset-normalizer | 78.17% | 81.84% | 85.95% |
| charset-normalizer char-dataset (477): cChardet | 79.45% | 85.95% | 93.29% |
| charset-normalizer char-dataset (477): chardet | 86.37% | 91.19% | 98.74% |
| charset-normalizer char-dataset (477): charset-normalizer | 83.44% | 89.52% | 95.81% |

Exact normalizes codec aliases only. Compatible additionally accepts known
directional supersets. Decode-equivalent means the detected codec produces
functionally equivalent text for that particular byte string. These are not
interchangeable definitions, so the raw counts and no-result counts remain in
the script's JSON output. The uchardet accuracy report intentionally includes
all 158 fixtures; its C conformance suite excludes five known failures and
passes the other 153.

Where a corpus supplies an expected language, the report also normalizes ISO
639-1 codes and full language names before recording language-only and joint
encoding/language accuracy:

| Detector on uchardet corpus | Language | Encoding and language |
|---|---:|---:|
| cChardet | 95.57% | 91.14% |
| chardet | 87.34% | 76.58% |
| charset-normalizer | 56.33% | 45.57% |

```bash
uv run --no-sync python benchmarks/accuracy.py \
  --uchardet-corpus src/ext/uchardet/test \
  --chardet-corpus /path/to/chardet-test-data \
  --charset-normalizer-corpus /path/to/char-dataset
```

## Input-size behavior

One Shift_JIS sample was repeated without changing its content. chardet's
default 200 KB processing cap explains its nearly constant time. cChardet and
charset-normalizer continue to depend on total input size, although for
different reasons.

| Input | cChardet | chardet pure Python | charset-normalizer pure Python |
|---|---:|---:|---:|
| 336 KB | 1.88 ms | 79.0 ms | 8.69 ms |
| 3.36 MB | 6.10 ms | 69.3 ms | 51.0 ms |
| 33.6 MB | 58.9 ms | 69.5 ms | 515 ms |

At 33.6 MB, cChardet's lead over chardet narrows to about 1.18x. The new
optional `max_bytes` argument lets callers make the same explicit evidence
tradeoff without first copying a Python slice. After warming the detector,
the 33.6 MB sample took 59.1 ms with the full buffer, 2.01 ms with a 1 MB
limit, and 0.601 ms with a 200 KB limit (about 98x faster). The default remains
unlimited for compatibility.

## Changes validated

- Native detection calls release the GIL. This preserves single-worker speed
  and enables the 3.47x four-worker result above.
- `UniversalDetector` now keeps its native detector until object destruction,
  can be reset after `close()`, and frees it even when callers omit `close()`.
- `done` no longer becomes true after every successful `feed()` call. The C
  API's zero return value means success, not detection completion.
- Native failures are checked against the C API's actual nonzero error
  contract.
- The maintained uchardet fork rejects invalid UTF-8 state-machine sequences
  and correctly ranks the upstream GB18030 fixture; cChardet no longer skips
  that conformance case.
- `detect(..., max_bytes=N)` bounds native work without allocating `data[:N]`.
- Buffers larger than uchardet's internal 32-bit input length are fed in safe
  chunks rather than silently truncating the length.
- Optional language weights let callers apply domain knowledge without
  changing the default candidate ranking.
- Incremental detection now exposes uchardet's actual early-completion state
  and finalizes the result as soon as no more input is needed.
- C++ allocation exceptions at the Cython boundary are translated to Python
  exceptions rather than escaping through generated extension code.
- Deterministic arbitrary-byte tests verify that one-shot and incrementally
  chunked detection produce the same result.
- Link-time optimization was tested and rejected: approximately 63.4 ms for
  the corpus versus a normal-build steady result around 62.3 ms, with extra
  build time and portability risk.

## Recommended roadmap

1. Make the two external accuracy corpora reproducibly downloadable and pin
   their revisions. Keep all three corpora reported separately; do not optimize
   against uchardet's own test data alone.
2. Evaluate a documented default evidence limit for the next major release.
   Measure accuracy at 64 KB, 200 KB, and 1 MB before changing the compatible
   unlimited default.
3. Profile uchardet with a neutral corpus. The likely targets are repeated
   full-buffer passes across active probers, virtual dispatch in per-byte
   loops, and candidate work that cannot affect the winner. Apply staged
   UTF/BOM/ASCII fast paths and upper-bound pruning only with exact regression
   tests.
4. Extend fuzzing and sanitizer coverage around the Python-visible C API.
   Upstream has
   fixed several bounds and allocation defects since the original fork; keep
   the maintained fork rebased on official GitLab history so those fixes remain
   part of every cChardet build.
5. Consider SIMD only after the staged/capped algorithm is measured. Avoid
   `-march=native` in distributed wheels and dispatch any architecture-
   specific implementation at runtime.

The immediate conclusion is narrower than the historical marketing claim:
cChardet still has a meaningful concurrent-throughput advantage, but optimized
charset-normalizer matched or beat it serially here. Its competitive gaps are
accuracy, staged fast paths, and bounded large-input latency—not primarily the
cost of the thin Cython wrapper.

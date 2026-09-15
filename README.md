cChardet
========

[![PyPI version](https://badge.fury.io/py/cchardet.svg)](https://badge.fury.io/py/cchardet)
[![Run tests](https://github.com/PyYoshi/cChardet/actions/workflows/test.yml/badge.svg)](https://github.com/PyYoshi/cChardet/actions/workflows/test.yml)
[![Build Wheels](https://github.com/PyYoshi/cChardet/actions/workflows/build.yaml/badge.svg)](https://github.com/PyYoshi/cChardet/actions/workflows/build.yaml)

cChardet is a high-speed universal character encoding detector built on the
[PyYoshi/uchardet](https://github.com/PyYoshi/uchardet) fork, which tracks
[upstream uchardet](https://gitlab.freedesktop.org/uchardet/uchardet).

## Python support

cChardet supports CPython 3.11 through 3.14, including the free-threaded
CPython 3.14 build. Each version is tested on Linux, macOS, and Windows.

## Development

Install [uv](https://docs.astral.sh/uv/), clone this repository with its submodules,
then create the locked development environment and run the checks:

```bash
git submodule update --init --recursive
uv sync --locked
make check
```

Build and validate the source distribution and wheel with:

```bash
uv build
uv run twine check dist/*
```

## Supported Languages/Encodings

- International (Unicode)
  - UTF-8
  - UTF-16BE / UTF-16LE
  - UTF-32BE / UTF-32LE / X-ISO-10646-UCS-4-34121 / X-ISO-10646-UCS-4-21431
- Arabic
  - ISO-8859-6
  - WINDOWS-1256
- Bulgarian
  - ISO-8859-5
  - WINDOWS-1251
- Chinese
  - ISO-2022-CN
  - BIG5
  - EUC-TW
  - GB18030
  - HZ-GB-2312
- Croatian:
  - ISO-8859-2
  - ISO-8859-13
  - ISO-8859-16
  - Windows-1250
  - IBM852
  - MAC-CENTRALEUROPE
- Czech
  - Windows-1250
  - ISO-8859-2
  - IBM852
  - MAC-CENTRALEUROPE
- Danish
  - ISO-8859-1
  - ISO-8859-15
  - WINDOWS-1252
- English
  - ASCII
- Esperanto
  - ISO-8859-3
- Estonian
  - ISO-8859-4
  - ISO-8859-13
  - ISO-8859-13
  - Windows-1252
  - Windows-1257
- Finnish
  - ISO-8859-1
  - ISO-8859-4
  - ISO-8859-9
  - ISO-8859-13
  - ISO-8859-15
  - WINDOWS-1252
- French
  - ISO-8859-1
  - ISO-8859-15
  - WINDOWS-1252
- German
  - ISO-8859-1
  - WINDOWS-1252
- Greek
  - ISO-8859-7
  - WINDOWS-1253
- Hebrew
  - ISO-8859-8
  - WINDOWS-1255
- Hungarian:
  - ISO-8859-2
  - WINDOWS-1250
- Irish Gaelic
  - ISO-8859-1
  - ISO-8859-9
  - ISO-8859-15
  - WINDOWS-1252
- Italian
  - ISO-8859-1
  - ISO-8859-3
  - ISO-8859-9
  - ISO-8859-15
  - WINDOWS-1252
- Japanese
  - ISO-2022-JP
  - SHIFT_JIS
  - EUC-JP
- Korean
  - ISO-2022-KR
  - EUC-KR / UHC
- Lithuanian
  - ISO-8859-4
  - ISO-8859-10
  - ISO-8859-13
- Latvian
  - ISO-8859-4
  - ISO-8859-10
  - ISO-8859-13
- Maltese
  - ISO-8859-3
- Polish:
  - ISO-8859-2
  - ISO-8859-13
  - ISO-8859-16
  - Windows-1250
  - IBM852
  - MAC-CENTRALEUROPE
- Portuguese
  - ISO-8859-1
  - ISO-8859-9
  - ISO-8859-15
  - WINDOWS-1252
- Romanian:
  - ISO-8859-2
  - ISO-8859-16
  - Windows-1250
  - IBM852
- Russian
  - ISO-8859-5
  - KOI8-R
  - WINDOWS-1251
  - MAC-CYRILLIC
  - IBM866
  - IBM855
- Slovak
  - Windows-1250
  - ISO-8859-2
  - IBM852
  - MAC-CENTRALEUROPE
- Slovene
  - ISO-8859-2
  - ISO-8859-16
  - Windows-1250
  - IBM852
  - M

## Example

```python
import cchardet as chardet

with open(r"tests/samples/wikipediaJa_One_Thousand_and_One_Nights_SJIS.txt", "rb") as f:
    msg = f.read()
    result = chardet.detect(msg)
    print(result)

# Bound work for large inputs without copying msg[:200_000].
result = chardet.detect(msg, max_bytes=200_000)

# Inspect alternative encoding/language candidates ordered by confidence.
for candidate in chardet.detect_all(msg, max_bytes=200_000):
    print(candidate)

# Optionally downweight unlikely languages with ISO 639-1 codes. Values must
# be between 0 and 1; omitting this argument preserves the default ranking.
result = chardet.detect(msg, language_weights={"ru": 0.2, "uk": 0.2})
```

The CLI accepts the same opt-in weighting as repeatable arguments, for example
`cchardetect --language-weight ru=0.2 --language-weight uk=0.2 file.txt`.

cChardet ships [PEP 561](https://peps.python.org/pep-0561/) type information. The
`detect()` and `detect_all()` results are typed as `cchardet.ResultDict`, and
`bytes`, `bytearray`, and `memoryview` inputs are accepted by the type checker.

## Benchmark

```bash
uv sync --locked
uv run python tests/bench.py

# Process-isolated statistical benchmark (optimized installed builds).
uv run python setup.py build_ext --inplace
uv run --no-sync python benchmarks/pyperf_compare.py \
  --corpus src/ext/uchardet/test --corpus tests/samples \
  --corpus ../charset_normalizer/data --rigorous -o benchmark.json

# Measure the sibling Pure Python fallbacks under the same harness.
uv run --no-sync python benchmarks/pyperf_compare.py \
  --pythonpath ../chardet/src --pythonpath ../charset_normalizer/src \
  --corpus src/ext/uchardet/test --rigorous -o benchmark-pure.json

# Compare regular and free-threaded CPython installations independently.
uv run --no-sync python benchmarks/pyperf_free_threading.py \
  --corpus src/ext/uchardet/test --rigorous -o free-threading.json

# Compare encoding and language accuracy on separately reported corpora.
uv run --no-sync python benchmarks/accuracy.py \
  --uchardet-corpus src/ext/uchardet/test \
  --chardet-corpus /path/to/chardet-test-data \
  --charset-normalizer-corpus /path/to/char-dataset
```

### Results

See [the detector and performance analysis](docs/performance-analysis.md) for
the methodology, current results, limitations, and optimization roadmap.
External fixtures and detector-tuning changes follow the
[test data policy](docs/test-data-policy.md).
Maintainer release steps are documented in [the release process](docs/releasing.md).

## LICENSE

See **COPYING** file.

## Contact

- [Issues](https://github.com/PyYoshi/cChardet/issues?page=1&state=open)

## Support Platforms

- Windows x86, x86_64
- Linux x86_64, aarch64
- macOS x86_64, arm64

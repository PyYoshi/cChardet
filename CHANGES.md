# CHANGES

## 2.2.0 (2026-09-15)

- Support Python 3.11, 3.12, 3.13, and 3.14, and drop support for Python 3.10
  and earlier versions
- Modernize development, testing, and packaging around `uv`, current Cython, and
  current Python packaging standards
- Update to the maintained PyYoshi/uchardet fork while preserving the existing
  cChardet-compatible API
- Improve UTF-8 validation and GB18030 candidate ranking in the bundled uchardet
- Return language and confidence information from the detection APIs
- Add `detect_all()` for inspecting ranked encoding and language candidates
- Add optional language weights to the Python API and CLI without changing the
  default candidate ranking
- Accept `bytes`, `bytearray`, and `memoryview` inputs, and add `max_bytes` to
  bound detection work without slicing the input
- Stream input in `cchardetect`, with JSON output and configurable chunk and byte
  limits
- Expose uchardet's early-completion state for incremental detection and safely
  chunk inputs larger than its internal 32-bit length
- Ship PEP 561 type information for the public Python and Cython-extension APIs
- Add reproducible performance and accuracy comparisons for cChardet, chardet,
  and charset-normalizer, including their available native accelerators
- Build and test distributions across supported Python versions on Linux, macOS,
  and Windows, including ARM64 wheel coverage
- Add native sanitizer, arbitrary-byte consistency, and installed-wheel smoke
  tests

## 2.2.0-alpha.2 (2024-06-xx)

- Improve test codes and CI/CD workflows

## 2.2.0-alpha.1 (2024-06-07)

- support Python 3.10, 3.11, 3.12
- drop support for Python 3.6, 3.7, 3.8
- experimental support for arm64
- improve some CI/CD workflows
- migration from nose to pytest (#87)

## 2.1.7 (2020-10-27)

- support Python 3.9
- drop support for Python 3.5

## 2.1.6 (2020-03-17)

- drop support for Python 2.7
- support Github Actions
- update dev-dependencies

## 2.1.5 (2019-09-27)

- update language models (uchardet)
- add iso8859-2 test but disabled it
- support Python 3.8
- drop support for Python 3.4

## 2.1.4 (2018-09-27)

- disable LTO because become poor performance

## 2.1.3 (2018-09-26)

- support Python 3.7

## 2.1.2 (2018-09-26)

- enable [LTO](https://gcc.gnu.org/wiki/LinkTimeOptimization) for wheel builds
- update Cython

## 2.1.1 (2017-07-01)

- fix that different results with different chuck sizes
- fix that assignments to nsSMState in nsCodingStateMachine result in unspecified behavior
- include COPYING in package

## 2.1.0 (2017-05-15)

- add cchardetect CLI script ([#30](https://github.com/PyYoshi/cChardet/pull/30))[\@craigds](https://github.com/craigds)

## 2.0.1 (2017-04-25)

- fix an issue where UTF-8 with a BOM would not be detected as UTF-8-SIG (fix [#28](https://github.com/PyYoshi/cChardet/issues/28))
- pass NULL Byte to feed() / detect() (fix [#27](https://github.com/PyYoshi/cChardet/issues/27))

## 2.0.0 (2017-04-06)

- Improve tests

## 2.0a4 (2017-04-05)

- Update uchardet repo (Fix buffer overflow)

## 2.0a3 (2017-03-29)

- Implement UniversalDetector (like chardet)

## 2.0a2 (2017-03-28)

- Update uchardet repo (Fix memory leak)

## 2.0a1 (2017-03-28)

- Replace [uchardet-enhanced](https://bitbucket.org/medoc/uchardet-enhanced/overview) to [uchardet](https://github.com/PyYoshi/uchardet)
- Remove Detector class

## 1.1.3 (2017-02-26)

- Support AArch64

## 1.1.2 (2017-01-08)

- Support Python 3.6

## 1.1.1 (2016-11-05)

- Use len() function (9e61cb9e96b138b0d18e5f9e013e144202ae4067)
- Remove detect function in \_cchardet.pyx (25b581294fc0ae8f686ac9972c8549666766f695)
- Support manylinux1 wheel

## 1.1.0 (2016-10-17)

- Add Detector class
- Improve unit tests

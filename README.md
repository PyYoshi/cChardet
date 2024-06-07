cChardet
========

[![PyPI version](https://badge.fury.io/py/cchardet.svg)](https://badge.fury.io/py/cchardet)
[![Run tests](https://github.com/PyYoshi/cChardet/actions/workflows/test.yml/badge.svg)](https://github.com/PyYoshi/cChardet/actions/workflows/test.yml)
[![Build Wheels](https://github.com/PyYoshi/cChardet/actions/workflows/build.yaml/badge.svg)](https://github.com/PyYoshi/cChardet/actions/workflows/build.yaml)

cChardet is high speed universal character encoding detector. - binding to [uchardet](https://github.com/PyYoshi/uchardet).

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
```

## Benchmark

```bash
$ python setup.py build_ext -i -f
$ python tests/bench.py
```

### Results

CPU: AMD Ryzen 9 7950X3D

RAM: DDR5-5600MT/s 96GB

Platform: Ubuntu 24.04 amd64

#### Python 3.12.3

|                   | Request (call/s) |
|-------------------|------------------|
| chardet v5.2.0    | 1.1              |
| cchardet v2.2.0a1 | 2263.6           |

## LICENSE

See **COPYING** file.

## Contact

- [Issues](https://github.com/PyYoshi/cChardet/issues?page=1&state=open)

## Support Platforms

- Windows i686, x86_64
- Linux i686, x86_64
- macOS x86_64

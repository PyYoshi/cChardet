<!-- markdown to rst: http://johnmacfarlane.net/pandoc/try -->

# cChardet
This library is high speed universal character encoding detector. - binding to [charsetdetect](https://bitbucket.org/medoc/uchardet-enhanced/overview).

This library is faster than [chardet](http://pypi.python.org/pypi/chardet).
# Support codecs
*   Big5
*   EUC-JP
*   EUC-KR
*   GB18030
*   gb18030
*   HZ-GB-2312
*   IBM855
*   IBM866
*   ISO-2022-CN
*   ISO-2022-JP
*   ISO-2022-KR
*   ISO-8859-2
*   ISO-8859-5
*   ISO-8859-7
*   ISO-8859-8
*   KOI8-R
*   Shift_JIS
*   TIS-620
*   UTF-8
*   UTF-16BE
*   UTF-16LE
*   UTF-32BE
*   UTF-32LE
*   WINDOWS-1250
*   WINDOWS-1251
*   WINDOWS-1252
*   WINDOWS-1253
*   WINDOWS-1255
*   EUC-TW
*   X-ISO-10646-UCS-4-2143
*   X-ISO-10646-UCS-4-3412
*   x-mac-cyrillic
# Requires
*   Cython: [http://www.cython.org/](http://www.cython.org/)
	
e.g.) Ubuntu 12.04
	
	$sudo apt-get install build-essential python-dev cython
# Installation
	$cd /tmp

	$git clone git://github.com/PyYoshi/cChardet.git

	$cd cChardet

	$python setup.py build

	$sudo python setup.py install

or

	$sudo easy_install cchardet
# Example

```python
# coding: utf8
import cchardet
msg = file(r"test/testdata/wikipediaJa_One_Thousand_and_One_Nights_SJIS.txt").read()
result = cchardet.detect(msg)
print(result)
result2 = cchardet.detect_with_confidence(msg)
print(result2)
```
# Test
	$sudo easy_install or pip install -U chardet nose
	
	$cd test

	$nosetests --nocapture tests.py
# Benchmark
code: [tests.TestCchardetSpeed](https://github.com/PyYoshi/cChardet/blob/master/test/tests.py#L415)

sample: [test/testdata/wikipediaJa_One_Thousand_and_One_Nights_SJIS.txt](https://github.com/PyYoshi/cChardet/blob/master/test/testdata/wikipediaJa_One_Thousand_and_One_Nights_SJIS.txt)
### Performance:
CPU: Intel Core i7 860 2.8GHz

RAM: DDR3-1333 16GB

Platform: Windows 7 HP x64, Python 2.7.3 32-bit
### Result:

<table>
  <tr>
    <th></th><th>Request (call/s)</th><th>Result of encoding</th>
  </tr>
  <tr>
    <td>chardet</td><td>0.25</td><td>shift_jis</td>
  </tr>
  <tr>
    <td>cchardet</td><td>500.03</td><td>shift_jis</td>
  </tr>
</table>
# License
* This library files("cchardet.pyx","setup.py","tests.py") are "The MIT License".

* Other Libraries License: Please, look at the [ext](https://github.com/PyYoshi/cChardet/tree/master/src/ext) directory.
# Thanks
* [https://bitbucket.org/medoc/uchardet-enhanced/overview](https://bitbucket.org/medoc/uchardet-enhanced/overview)

* [http://www.cython.org/](http://www.cython.org/)
# Contact
[My blog](http://blog.remu.biz)

Sorry for my poor English :)
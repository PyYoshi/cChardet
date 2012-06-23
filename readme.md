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
*   windows-1250
*   windows-1251
*   windows-1252
*   windows-1253
*   windows-1255
*   x-euc-tw
*   X-ISO-10646-UCS-4-2143
*   X-ISO-10646-UCS-4-3412
*   x-mac-cyrillic

# Requires
*   Cython: [http://www.cython.org/](http://www.cython.org/)

*   uchardet-enhanced: [https://bitbucket.org/medoc/uchardet-enhanced/overview](https://bitbucket.org/medoc/uchardet-enhanced/overview)

# Install
### Build uchardet-enhanced
1.   $cd /tmp

2.   $hg clone https://bitbucket.org/medoc/uchardet-enhanced

3.   $cd uchardet-enhanced/libcharsetdetect

4.   $./configure

5.   $make

6.   $sudo make install

7.   $ls -la /usr/local/lib

8.   $ls -la /usr/local/include

### Build cChardet
1.   $cd /tmp

2.   $git clone git://github.com/PyYoshi/cChardet.git

3.   $cd cChardet

4.   $sudo pip install or easy_install -U cython. (If your os is Ubuntu, I recommend that you do "sudo apt-get install python-dev cython")

5.   $python setup.py build

6.   $sudo python setup.py install

# Example

```python
# coding: utf8
import cchardet
msg = file(r"testdata/wikipediaJa_One_Thousand_and_One_Nights_SJIS.txt").read()
result = cchardet.detect(msg)
print(result)
```

# Test
*   $sudo easy_install or pip install -U chardet nose

*   $nosetests --nocapture tests.py

# Benchmark
see [tests.TestCchardetSpeed](https://github.com/PyYoshi/cChardet/blob/master/tests.py#L416)

### Sample(shift_jis):
*   [testdata/wikipediaJa_One_Thousand_and_One_Nights_SJIS.txt](https://github.com/PyYoshi/cChardet/blob/master/testdata/wikipediaJa_One_Thousand_and_One_Nights_SJIS.txt)

### PC Spec.:
*   CPU: Intel Core i7 860 2.8GHz

*   RAM: DDR3-1333 16GB

*   Platform: Windows 7 HP x64, Python 2.7.3 32-bit

### Result:
*   chardet: 4.009999990463257s, shift_jis

*   cchardet: 0.0009999275207519531s, shift_jis

# License
* This library files("cchardet.pyx","setup.py","tests.py") are "The MIT License".

* Other Library License: Please, look at the "ext" directory.

# Contact
[My blog](http://blog.remu.biz)

Sorry for my poor English :)
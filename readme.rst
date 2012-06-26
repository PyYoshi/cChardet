cChardet
========

This library is high speed universal character encoding detector. -
binding to `charsetdetect`_.

This library is faster than `chardet`_.

Support codecs
==============

-  Big5
-  EUC-JP
-  EUC-KR
-  GB18030
-  gb18030
-  HZ-GB-2312
-  IBM855
-  IBM866
-  ISO-2022-CN
-  ISO-2022-JP
-  ISO-2022-KR
-  ISO-8859-2
-  ISO-8859-5
-  ISO-8859-7
-  ISO-8859-8
-  KOI8-R
-  Shift\_JIS
-  TIS-620
-  UTF-8
-  UTF-16BE
-  UTF-16LE
-  UTF-32BE
-  UTF-32LE
-  windows-1250
-  windows-1251
-  windows-1252
-  windows-1253
-  windows-1255
-  x-euc-tw
-  X-ISO-10646-UCS-4-2143
-  X-ISO-10646-UCS-4-3412
-  x-mac-cyrillic

Requires
========

-  Cython: `http://www.cython.org/`_

Install
=======

Build uchardet-enhanced
~~~~~~~~~~~~~~~~~~~~~~~

1. $cd /tmp

2. $git clone git://github.com/PyYoshi/cChardet.git

3. $cd cChardet

4. $python setup.py build

5. $sudo python setup.py install

Test
====

-  $sudo easy\_install or pip install -U chardet nose

-  $nosetests –nocapture tests.py

Benchmark
=========

see `tests.TestCchardetSpeed`_

Sample(shift\_jis):
~~~~~~~~~~~~~~~~~~~

-  `test/testdata/wikipediaJa\_One\_Thousand\_and\_One\_Nights\_SJIS.txt`_

PC Spec.:
~~~~~~~~~

-  CPU: Intel Core i7 860 2.8GHz

-  RAM: DDR3-1333 16GB

-  Platform: Windows 7 HP x64, Python 2.7.3 32-bit

Result:
~~~~~~~

-  chardet: 4.009999990463257s, shift\_jis

-  cchardet: 0.0009999275207519531s, shift\_jis

License
=======

-  This library files(“cchardet.pyx”,“setup.py”,“tests.py”) are “The MIT
   License”.

-  Other Library License: Please, look at the “ext” directory.

Thanks
======

-  `https://bitbucket.org/medoc/uchardet-enhanced/overview`_

-  `http://www.cython.org/`_

Contact
=======

`My blog`_

Sorry for my poor English :)

.. _charsetdetect: https://bitbucket.org/medoc/uchardet-enhanced/overview
.. _chardet: http://pypi.python.org/pypi/chardet
.. _`http://www.cython.org/`: http://www.cython.org/
.. _tests.TestCchardetSpeed: https://github.com/PyYoshi/cChardet/blob/master/test/tests.py#L415
.. _test/testdata/wikipediaJa\_One\_Thousand\_and\_One\_Nights\_SJIS.txt: https://github.com/PyYoshi/cChardet/blob/master/test/testdata/wikipediaJa_One_Thousand_and_One_Nights_SJIS.txt
.. _`https://bitbucket.org/medoc/uchardet-enhanced/overview`: https://bitbucket.org/medoc/uchardet-enhanced/overview
.. _My blog: http://blog.remu.biz

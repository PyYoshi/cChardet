
cChardet
========

cChardet is high speed universal character encoding detector. - binding
to
`charsetdetect <https://bitbucket.org/medoc/uchardet-enhanced/overview>`_.

Support codecs
--------------

-  Big5
-  EUC-JP
-  EUC-KR
-  GB18030
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
-  WINDOWS-1250
-  WINDOWS-1251
-  WINDOWS-1252
-  WINDOWS-1253
-  WINDOWS-1255
-  EUC-TW
-  X-ISO-10646-UCS-4-2143
-  X-ISO-10646-UCS-4-3412
-  x-mac-cyrillic

Requires
--------

-  Cython: `http://www.cython.org/ <http://www.cython.org/>`_

e.g.) Ubuntu 12.04

::

    $ sudo apt-get install build-essential python-dev cython

Installation
------------

::

    $ cd /tmp
    $ git clone git://github.com/PyYoshi/cChardet.git
    $ cd cChardet
    $ python setup.py build
    $ sudo python setup.py install

or

::

    $ sudo easy_install cchardet

Example
-------

::

    # -*- coding: utf-8 -*-
    import cchardet as chardet
    with open(r"test/testdata/wikipediaJa_One_Thousand_and_One_Nights_SJIS.txt", "rb") as f:
        msg = f.read()
    result = chardet.detect(msg)
    print(result)

Test
----

::

    $ sudo easy_install or pip install -U cchardet nose
    $ cd test
    $ nosetests --nocapture tests.py

Benchmark
---------

code:
`tests.TestCchardetSpeed <https://github.com/PyYoshi/cChardet/blob/master/test/tests.py#L461>`_

sample:
`test/testdata/wikipediaJa\_One\_Thousand\_and\_One\_Nights\_SJIS.txt <https://github.com/PyYoshi/cChardet/blob/master/test/testdata/wikipediaJa_One_Thousand_and_One_Nights_SJIS.txt>`_

Performance:
~~~~~~~~~~~~

CPU: Intel Core i7 860 2.8GHz

RAM: DDR3-1333 16GB

Platform: Kubuntu 12.04 amd64, Python 2.7.3 64-bit

Result:
~~~~~~~

::

	chardet:	0.32 (call/s)

	cchardet:	975.32 (call/s)

License
--------------

-  The MIT License:
   `src/cchardet <https://github.com/PyYoshi/cChardet/tree/master/src/cchardet>`_

-  Other Libraries License: Please, look at the
   `src/ext <https://github.com/PyYoshi/cChardet/tree/master/src/ext>`_
   directory.

Thanks
--------------

-  `uchardet-enhanced <https://bitbucket.org/medoc/uchardet-enhanced/overview>`_

-  `Cython <http://www.cython.org/>`_

Contact
--------------

`My blog <http://blog.remu.biz>`_

`Issues <https://github.com/PyYoshi/cChardet/issues?page=1&state=open>`_

Sorry for my poor English :)

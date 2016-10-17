cChardet
========

cChardet is high speed universal character encoding detector. - binding to `charsetdetect`_.

.. image:: https://badge.fury.io/py/cchardet.svg
   :target: https://badge.fury.io/py/cchardet
   :alt: PyPI version
.. image:: https://travis-ci.org/PyYoshi/cChardet.svg?branch=master
   :target: https://travis-ci.org/PyYoshi/cChardet
   :alt: Travis Ci build status
.. image:: https://ci.appveyor.com/api/projects/status/lwkc4rgf3gncb1ne/branch/master?svg=true
   :target: https://ci.appveyor.com/project/PyYoshi/cchardet/branch/master
   :alt: AppVeyor build status

Support codecs
--------------

- Big5
- EUC-JP
- EUC-KR
- GB18030
- HZ-GB-2312
- IBM855
- IBM866
- ISO-2022-CN
- ISO-2022-JP
- ISO-2022-KR
- ISO-8859-2
- ISO-8859-5
- ISO-8859-7
- ISO-8859-8
- KOI8-R
- Shift_JIS
- TIS-620
- UTF-8
- UTF-16BE
- UTF-16LE
- UTF-32BE
- UTF-32LE
- WINDOWS-1250
- WINDOWS-1251
- WINDOWS-1252
- WINDOWS-1253
- WINDOWS-1255
- EUC-TW
- X-ISO-10646-UCS-4-2143
- X-ISO-10646-UCS-4-3412
- x-mac-cyrillic

Requirements
------------

- `Cython`_

Example
-------

.. code-block:: python

    # -*- coding: utf-8 -*-
    import cchardet as chardet
    with open(r"src/tests/testdata/wikipediaJa_One_Thousand_and_One_Nights_SJIS.txt", "rb") as f:
        msg = f.read()
        result = chardet.detect(msg)
        print(result)


Benchmark
---------

.. code-block:: bash

    $ cd src/
    $ pip install chardet
    $ python tests/bench.py


Results
~~~~~~~

CPU: Intel(R) Core(TM) i3-4170 CPU @ 3.70GHz

RAM: DDR3 1600Mhz 16GB

Platform: Ubuntu 16.04 amd64

Python 2.7.12
^^^^^^^^^^^^^

+----------+------------------+
|          | Request (call/s) |
+==========+==================+
| chardet  | 0.26             |
+----------+------------------+
| cchardet | 1408.73          |
+----------+------------------+

Python 3.5.2
^^^^^^^^^^^^

+----------+------------------+
|          | Request (call/s) |
+==========+==================+
| chardet  | 0.28             |
+----------+------------------+
| cchardet | 1380.40          |
+----------+------------------+

License
-------

-  The MIT License: `src/cchardet`_
-  Other Libraries License: Please, look at the `src/ext`_ directory.

Thanks
------

-  `uchardet-enhanced`_
-  `Cython`_

Contact
-------

`Issues`_


.. _charsetdetect: https://bitbucket.org/medoc/uchardet-enhanced/overview
.. _Cython: http://www.cython.org/
.. _src/cchardet: https://github.com/PyYoshi/cChardet/tree/master/src/cchardet
.. _src/ext: https://github.com/PyYoshi/cChardet/tree/master/src/ext
.. _uchardet-enhanced: https://bitbucket.org/medoc/uchardet-enhanced/overview
.. _Issues: https://github.com/PyYoshi/cChardet/issues?page=1&state=open

#!/usr/bin/env python
# coding: utf-8

from distutils.core import setup, Extension
from Cython.Distutils import build_ext # use cython's buld_ext

setup(
    name = 'cchardet',
    author= 'PyYoshi',
    url = r"https://github.com/PyYoshi/cChardet",
    description = 'Universal encoding detector',
    long_description= """This library is high speed universal character encoding detector. - binding to charsetdetect.
This library is faster than chardet.
""",
    version = '0.1',
    classifiers = [
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Cython',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
    ],
    keywords = [
        'cython',
        'chardet',
        'universal character encoding detector',
        'charsetdetect'
    ],
    cmdclass = {'build_ext': build_ext},
    ext_modules = [
        Extension("cchardet",
            sources = ["cchardet.pyx"],
            libraries=['charsetdetect'],
            language="c",
        ),

    ]
)
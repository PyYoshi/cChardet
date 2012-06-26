#!/usr/bin/env python
# coding: utf-8

import ez_setup
ez_setup.use_setuptools()
import os,sys,platform,shutil
import subprocess
from setuptools import setup, Extension
import distutils.spawn as ds
from Cython.Distutils import build_ext

root = os.getcwd()
ext_dir = os.path.join(root,'ext_')
src_dir = os.path.join(root,'src')
build_dir = os.path.join(root,'build')
cchardet_dir = os.path.join(src_dir,'cchardet')
cchardet_source = os.path.join(cchardet_dir,"cchardet2.pyx")
charsetdetect_dir = os.path.join(ext_dir, 'libcharsetdetect')
charsetdetect_build_dir = os.path.join(charsetdetect_dir,'build')


cchardet_module = Extension("_cchardet",
    sources = [cchardet_source],
    #libraries = ['charsetdetect'],
    #include_dirs = [charsetdetect_dir],
    #library_dirs = [charsetdetect_build_dir],
    language = "c",
)

setup(
    name = 'cchardet',
    author= 'PyYoshi',
    url = r"https://github.com/PyYoshi/cChardet",
    description = 'Universal encoding detector',
    long_description= """This library is high speed universal character encoding detector. - binding to charsetdetect.
This library is faster than chardet.
""",
    version = '0.1',
    classifiers = [ # http://pypi.python.org/pypi?:action=list_classifiers
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
    ext_package='cchardet',
    package_dir = {'':src_dir},
    packages = ['cchardet'],
    cmdclass = {'build_ext': build_ext},
    ext_modules = [
        cchardet_module
    ],
)
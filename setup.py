#!/usr/bin/env python
# coding: utf-8

# python setup.py sdist --formats=gztar

import os
import sys
import platform

try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

import glob

try:
    import Cython.Compiler.Main as cython_compiler

    have_cython = True
except ImportError:
    have_cython = False
from distutils.command.build_ext import build_ext

DEBUG = False

src_dir = 'src'
ext_dir = os.path.join(src_dir, 'ext')
build_dir = 'build'
cchardet_dir = os.path.join(src_dir, 'cchardet/')
charsetdetect_dir = os.path.join(ext_dir, 'libcharsetdetect/')
nspr_emu_dir = os.path.join(charsetdetect_dir, 'nspr-emu/')
uchardet_dir = os.path.join(charsetdetect_dir, 'mozilla/extensions/universalchardet/src/base/')

if have_cython:
    pyx_sources = glob.glob(cchardet_dir + '*.pyx')
    sys.stderr.write('cythonize: %r\n' % (pyx_sources,))
    cython_compiler.compile(pyx_sources, options=cython_compiler.CompilationOptions(cplus=True))
cchardet_sources = glob.glob(cchardet_dir + '*.cpp')
sources = cchardet_sources + [os.path.join(charsetdetect_dir, 'charsetdetect.cpp')] + glob.glob(uchardet_dir + '*.cpp')

macros = []
extra_compile_args = []
extra_link_args = []

if platform.system() == 'Windows':
    macros.append(('WIN32', '1'))

if DEBUG:
    macros.append(('DEBUG_chardet', '1'))
    extra_compile_args.append('-g'),
    extra_link_args.append('-g'),

cchardet_module = Extension(
    'cchardet._cchardet',
    sources=sources,
    include_dirs=[uchardet_dir, nspr_emu_dir, charsetdetect_dir],
    language='c++',
    define_macros=macros,
)

setup(
    name='cchardet',
    author='PyYoshi',
    author_email='myoshi321go@gmail.com',
    url=r'https://github.com/PyYoshi/cChardet',
    description='Universal encoding detector. This library is faster than chardet.',
    long_description='''cChardet is high speed universal character encoding detector. - binding to charsetdetect.
This library is faster than chardet.
''',
    version='1.1.0',
    license='MIT License',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Cython',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    keywords=[
        'cython',
        'chardet',
        'charsetdetect'
    ],
    cmdclass={'build_ext': build_ext},
    package_dir={'': src_dir},
    packages=['cchardet', ],
    ext_modules=[
        cchardet_module
    ],
)

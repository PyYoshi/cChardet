#!/usr/bin/env python
# coding: utf-8

import os
import sys
import glob
import codecs
import re
from distutils.command.build_ext import build_ext
from distutils import sysconfig

try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

have_cython = True
try:
    import Cython.Compiler.Main as cython_compiler
except ImportError:
    have_cython = False

cchardet_dir = os.path.join("src", "cchardet") + os.path.sep
uchardet_dir = os.path.join("src", "ext", "uchardet", "src")

if have_cython:
    pyx_sources = glob.glob(cchardet_dir + '*.pyx')
    sys.stderr.write('cythonize: %r\n' % (pyx_sources,))
    cython_compiler.compile(
        pyx_sources, options=cython_compiler.CompilationOptions(cplus=True, compiler_directives={"language_level": 3}))

cchardet_sources = glob.glob(cchardet_dir + '*.cpp')
sources = cchardet_sources

uchardet_sources = [
    os.path.join(uchardet_dir, 'CharDistribution.cpp'),
    os.path.join(uchardet_dir, 'JpCntx.cpp'),
    os.path.join(uchardet_dir, 'LangModels','LangArabicModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels','LangBulgarianModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels','LangCroatianModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels','LangCzechModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels','LangEsperantoModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels','LangEstonianModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels','LangFinnishModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels','LangFrenchModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels','LangDanishModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels','LangGermanModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels','LangGreekModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels','LangHungarianModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels','LangHebrewModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels','LangIrishModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels','LangItalianModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels','LangLithuanianModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels','LangLatvianModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels','LangMalteseModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels','LangPolishModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels','LangPortugueseModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels','LangRomanianModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels','LangRussianModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels','LangSlovakModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels','LangSloveneModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels','LangSwedishModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels','LangSpanishModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels','LangThaiModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels','LangTurkishModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels','LangVietnameseModel.cpp'),
    os.path.join(uchardet_dir, 'nsHebrewProber.cpp'),
    os.path.join(uchardet_dir, 'nsCharSetProber.cpp'),
    os.path.join(uchardet_dir, 'nsBig5Prober.cpp'),
    os.path.join(uchardet_dir, 'nsEUCJPProber.cpp'),
    os.path.join(uchardet_dir, 'nsEUCKRProber.cpp'),
    os.path.join(uchardet_dir, 'nsEUCTWProber.cpp'),
    os.path.join(uchardet_dir, 'nsEscCharsetProber.cpp'),
    os.path.join(uchardet_dir, 'nsEscSM.cpp'),
    os.path.join(uchardet_dir, 'nsGB2312Prober.cpp'),
    os.path.join(uchardet_dir, 'nsMBCSGroupProber.cpp'),
    os.path.join(uchardet_dir, 'nsMBCSSM.cpp'),
    os.path.join(uchardet_dir, 'nsSBCSGroupProber.cpp'),
    os.path.join(uchardet_dir, 'nsSBCharSetProber.cpp'),
    os.path.join(uchardet_dir, 'nsSJISProber.cpp'),
    os.path.join(uchardet_dir, 'nsUTF8Prober.cpp'),
    os.path.join(uchardet_dir, 'nsLatin1Prober.cpp'),
    os.path.join(uchardet_dir, 'nsUniversalDetector.cpp'),
    os.path.join(uchardet_dir, 'uchardet.cpp')
]
sources += uchardet_sources

# Remove the "-Wstrict-prototypes" compiler option, which isn't valid for C++.
cfg_vars = sysconfig.get_config_vars()
for key, value in cfg_vars.items():
    if type(value) == str:
        cfg_vars[key] = value.replace("-Wstrict-prototypes", "")
        # O3を指定したところで速度が向上するかは疑問である
        # cfg_vars[key] = value.replace("-O2", "-O3")

cchardet_module = Extension(
    'cchardet._cchardet',
    sources=sources,
    include_dirs=[uchardet_dir],
    language='c++',
)


def read(f):
    return open(os.path.join(os.path.dirname(__file__), f)).read().strip()


with codecs.open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'src', 'cchardet', 'version.py'), 'r', 'latin1') as fp:
    try:
        version = re.findall(
            r"^__version__ = '([^']+)'\r?$", fp.read(), re.M)[0]
    except IndexError:
        raise RuntimeError('Unable to determine version.')

setup(
    name='faust-cchardet',
    author='PyYoshi',
    author_email='myoshi321go@gmail.com',
    url=r'https://github.com/faust-streaming/cChardet',
    description='cChardet is high speed universal character encoding detector.',
    long_description='\n\n'.join((read('README.rst'), read('CHANGES.rst'))),
    version=version,
    license='Mozilla Public License',
    classifiers=[
        'License :: OSI Approved :: Mozilla Public License 1.1 (MPL 1.1)',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Programming Language :: Cython',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10', 
        'Programming Language :: Python :: 3.11',
    ],
    keywords=[
        'cython',
        'chardet',
        'charsetdetect'
    ],
    cmdclass={'build_ext': build_ext},
    package_dir={'': 'src'},
    packages=['cchardet', ],
    scripts=['bin/cchardetect'],
    ext_modules=[
        cchardet_module
    ],
)

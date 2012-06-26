#!/usr/bin/env python
# coding: utf-8

import ez_setup
ez_setup.use_setuptools()
import os,platform
from setuptools import setup, Extension
from Cython.Distutils import build_ext

root = os.getcwd()
ext_dir = os.path.join(root,'ext')
src_dir = os.path.join(root,'src')
build_dir = os.path.join(root,'build')
cchardet_dir = os.path.join(src_dir,'cchardet')
cchardet_source = os.path.join(cchardet_dir,"cchardet.pyx")
charsetdetect_dir = os.path.join(ext_dir, 'libcharsetdetect')
nspr_emu_dir = os.path.join(charsetdetect_dir,"nspr-emu")
uchardet_dir = os.path.join(charsetdetect_dir,"mozilla/extensions/universalchardet/src/base")

uchardet_sources = [
    "ext/libcharsetdetect/charsetdetect.cpp",
    "ext/libcharsetdetect/mozilla/extensions/universalchardet/src/base/CharDistribution.cpp",
    "ext/libcharsetdetect/mozilla/extensions/universalchardet/src/base/JpCntx.cpp",
    "ext/libcharsetdetect/mozilla/extensions/universalchardet/src/base/LangBulgarianModel.cpp",
    "ext/libcharsetdetect/mozilla/extensions/universalchardet/src/base/LangCyrillicModel.cpp",
    "ext/libcharsetdetect/mozilla/extensions/universalchardet/src/base/LangCzechModel.cpp",
    "ext/libcharsetdetect/mozilla/extensions/universalchardet/src/base/LangFinnishModel.cpp",
    "ext/libcharsetdetect/mozilla/extensions/universalchardet/src/base/LangFrenchModel.cpp",
    "ext/libcharsetdetect/mozilla/extensions/universalchardet/src/base/LangGermanModel.cpp",
    "ext/libcharsetdetect/mozilla/extensions/universalchardet/src/base/LangGreekModel.cpp",
    "ext/libcharsetdetect/mozilla/extensions/universalchardet/src/base/LangHebrewModel.cpp",
    "ext/libcharsetdetect/mozilla/extensions/universalchardet/src/base/LangHungarianModel.cpp",
    "ext/libcharsetdetect/mozilla/extensions/universalchardet/src/base/LangPolishModel.cpp",
    "ext/libcharsetdetect/mozilla/extensions/universalchardet/src/base/LangSpanishModel.cpp",
    "ext/libcharsetdetect/mozilla/extensions/universalchardet/src/base/LangSwedishModel.cpp",
    "ext/libcharsetdetect/mozilla/extensions/universalchardet/src/base/LangThaiModel.cpp",
    "ext/libcharsetdetect/mozilla/extensions/universalchardet/src/base/LangTurkishModel.cpp",
    "ext/libcharsetdetect/mozilla/extensions/universalchardet/src/base/nsBig5Prober.cpp",
    "ext/libcharsetdetect/mozilla/extensions/universalchardet/src/base/nsCharSetProber.cpp",
    "ext/libcharsetdetect/mozilla/extensions/universalchardet/src/base/nsEscCharsetProber.cpp",
    "ext/libcharsetdetect/mozilla/extensions/universalchardet/src/base/nsEscSM.cpp",
    "ext/libcharsetdetect/mozilla/extensions/universalchardet/src/base/nsEUCJPProber.cpp",
    "ext/libcharsetdetect/mozilla/extensions/universalchardet/src/base/nsEUCKRProber.cpp",
    "ext/libcharsetdetect/mozilla/extensions/universalchardet/src/base/nsEUCTWProber.cpp",
    "ext/libcharsetdetect/mozilla/extensions/universalchardet/src/base/nsGB2312Prober.cpp",
    "ext/libcharsetdetect/mozilla/extensions/universalchardet/src/base/nsHebrewProber.cpp",
    "ext/libcharsetdetect/mozilla/extensions/universalchardet/src/base/nsLatin1Prober.cpp",
    "ext/libcharsetdetect/mozilla/extensions/universalchardet/src/base/nsMBCSGroupProber.cpp",
    "ext/libcharsetdetect/mozilla/extensions/universalchardet/src/base/nsMBCSSM.cpp",
    "ext/libcharsetdetect/mozilla/extensions/universalchardet/src/base/nsSBCharSetProber.cpp",
    "ext/libcharsetdetect/mozilla/extensions/universalchardet/src/base/nsSBCSGroupProber.cpp",
    "ext/libcharsetdetect/mozilla/extensions/universalchardet/src/base/nsSJISProber.cpp",
    "ext/libcharsetdetect/mozilla/extensions/universalchardet/src/base/nsUniversalDetector.cpp",
    "ext/libcharsetdetect/mozilla/extensions/universalchardet/src/base/nsUTF8Prober.cpp",
    ]

macros = []
if platform.system() == "Windows":
    macros.append(("WIN32","1"))

cchardet_module = Extension("_cchardet",
    sources = uchardet_sources+[cchardet_source],
    include_dirs = [uchardet_dir,nspr_emu_dir,charsetdetect_dir],
    language = "c++",
    define_macros=macros
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
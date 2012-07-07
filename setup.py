#!/usr/bin/env python
# coding: utf-8

# python setup.py sdist --formats=gztar

import ez_setup
ez_setup.use_setuptools()
import os,platform
from setuptools import setup, Extension
from Cython.Distutils import build_ext

DEBUG = False

root = os.getcwd()
src_dir = os.path.join(root,'src')
ext_dir = os.path.join(src_dir,'ext')
build_dir = os.path.join(root,'build')
cchardet_dir = os.path.join(src_dir,'cchardet')
cchardet_source = os.path.join(cchardet_dir,"cchardet.pyx")
cchardet_source2 = os.path.join(cchardet_dir,"__init__.py")
charsetdetect_dir = os.path.join(ext_dir, 'libcharsetdetect')
nspr_emu_dir = os.path.join(charsetdetect_dir,"nspr-emu")
uchardet_dir = os.path.join(charsetdetect_dir,"mozilla/extensions/universalchardet/src/base")

uchardet_sources = [
    os.path.join(charsetdetect_dir,"charsetdetect.cpp"),
    os.path.join(charsetdetect_dir,"mozilla/extensions/universalchardet/src/base/CharDistribution.cpp"),
    os.path.join(charsetdetect_dir,"mozilla/extensions/universalchardet/src/base/JpCntx.cpp"),
    os.path.join(charsetdetect_dir,"mozilla/extensions/universalchardet/src/base/LangBulgarianModel.cpp"),
    os.path.join(charsetdetect_dir,"mozilla/extensions/universalchardet/src/base/LangCyrillicModel.cpp"),
    os.path.join(charsetdetect_dir,"mozilla/extensions/universalchardet/src/base/LangCzechModel.cpp"),
    os.path.join(charsetdetect_dir,"mozilla/extensions/universalchardet/src/base/LangFinnishModel.cpp"),
    os.path.join(charsetdetect_dir,"mozilla/extensions/universalchardet/src/base/LangFrenchModel.cpp"),
    os.path.join(charsetdetect_dir,"mozilla/extensions/universalchardet/src/base/LangGermanModel.cpp"),
    os.path.join(charsetdetect_dir,"mozilla/extensions/universalchardet/src/base/LangGreekModel.cpp"),
    os.path.join(charsetdetect_dir,"mozilla/extensions/universalchardet/src/base/LangHebrewModel.cpp"),
    os.path.join(charsetdetect_dir,"mozilla/extensions/universalchardet/src/base/LangHungarianModel.cpp"),
    os.path.join(charsetdetect_dir,"mozilla/extensions/universalchardet/src/base/LangPolishModel.cpp"),
    os.path.join(charsetdetect_dir,"mozilla/extensions/universalchardet/src/base/LangSpanishModel.cpp"),
    os.path.join(charsetdetect_dir,"mozilla/extensions/universalchardet/src/base/LangSwedishModel.cpp"),
    os.path.join(charsetdetect_dir,"mozilla/extensions/universalchardet/src/base/LangThaiModel.cpp"),
    os.path.join(charsetdetect_dir,"mozilla/extensions/universalchardet/src/base/LangTurkishModel.cpp"),
    os.path.join(charsetdetect_dir,"mozilla/extensions/universalchardet/src/base/nsBig5Prober.cpp"),
    os.path.join(charsetdetect_dir,"mozilla/extensions/universalchardet/src/base/nsCharSetProber.cpp"),
    os.path.join(charsetdetect_dir,"mozilla/extensions/universalchardet/src/base/nsEscCharsetProber.cpp"),
    os.path.join(charsetdetect_dir,"mozilla/extensions/universalchardet/src/base/nsEscSM.cpp"),
    os.path.join(charsetdetect_dir,"mozilla/extensions/universalchardet/src/base/nsEUCJPProber.cpp"),
    os.path.join(charsetdetect_dir,"mozilla/extensions/universalchardet/src/base/nsEUCKRProber.cpp"),
    os.path.join(charsetdetect_dir,"mozilla/extensions/universalchardet/src/base/nsEUCTWProber.cpp"),
    os.path.join(charsetdetect_dir,"mozilla/extensions/universalchardet/src/base/nsGB2312Prober.cpp"),
    os.path.join(charsetdetect_dir,"mozilla/extensions/universalchardet/src/base/nsHebrewProber.cpp"),
    os.path.join(charsetdetect_dir,"mozilla/extensions/universalchardet/src/base/nsLatin1Prober.cpp"),
    os.path.join(charsetdetect_dir,"mozilla/extensions/universalchardet/src/base/nsMBCSGroupProber.cpp"),
    os.path.join(charsetdetect_dir,"mozilla/extensions/universalchardet/src/base/nsMBCSSM.cpp"),
    os.path.join(charsetdetect_dir,"mozilla/extensions/universalchardet/src/base/nsSBCharSetProber.cpp"),
    os.path.join(charsetdetect_dir,"mozilla/extensions/universalchardet/src/base/nsSBCSGroupProber.cpp"),
    os.path.join(charsetdetect_dir,"mozilla/extensions/universalchardet/src/base/nsSJISProber.cpp"),
    os.path.join(charsetdetect_dir,"mozilla/extensions/universalchardet/src/base/nsUniversalDetector.cpp"),
    os.path.join(charsetdetect_dir,"mozilla/extensions/universalchardet/src/base/nsUTF8Prober.cpp"),
]

macros = []
extra_compile_args = []
extra_link_args = []

if platform.system() == "Windows":
    macros.append(("WIN32","1"))

if DEBUG:
    macros.append(("DEBUG_chardet","1"))
    extra_compile_args.append("-g"),
    extra_link_args.append("-g"),

cchardet_module = Extension("cchardet._cchardet",
    sources = uchardet_sources+[cchardet_source],
    include_dirs = [uchardet_dir,nspr_emu_dir,charsetdetect_dir],
    language = "c++",
    define_macros=macros,
)

setup(
    name = 'cchardet',
    author = 'PyYoshi',
    author_email = 'yohihiro_dot_m_at_gmail_dot_com',
    url = r"https://github.com/PyYoshi/cChardet",
    description = 'Universal encoding detector. This library is faster than chardet.',
    long_description= """This library is high speed universal character encoding detector. - binding to charsetdetect.
This library is faster than chardet.
""",
    version = '0.3',
    license = 'MIT License',
    classifiers = [ # http://pypi.python.org/pypi?:action=list_classifiers
                    'Development Status :: 4 - Beta',
                    'License :: OSI Approved :: MIT License',
                    'Programming Language :: Cython',
                    'Programming Language :: Python',
                    'Topic :: Software Development :: Libraries',
                    ],
    keywords = [
        'cython',
        'chardet',
        'charsetdetect'
    ],
    cmdclass = {'build_ext': build_ext},
    package_dir = {"":src_dir},
    packages = ['cchardet',],
    ext_modules = [
        cchardet_module
    ],
)
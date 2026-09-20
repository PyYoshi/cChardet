#!/usr/bin/env python
# coding: utf-8

import glob
import os
import sys
import sysconfig

from setuptools import Extension, setup

cchardet_dir = "src/cchardet/"
uchardet_dir = "src/ext/uchardet/src"
cchardet_sources = glob.glob(cchardet_dir + "*.pyx")
sources = cchardet_sources

uchardet_sources = [
    os.path.join(uchardet_dir, "LangModels/LangArabicModel.cpp"),
    os.path.join(uchardet_dir, "LangModels/LangBelarusianModel.cpp"),
    os.path.join(uchardet_dir, "LangModels/LangBulgarianModel.cpp"),
    os.path.join(uchardet_dir, "LangModels/LangCatalanModel.cpp"),
    os.path.join(uchardet_dir, "LangModels/LangCroatianModel.cpp"),
    os.path.join(uchardet_dir, "LangModels/LangCzechModel.cpp"),
    os.path.join(uchardet_dir, "LangModels/LangDanishModel.cpp"),
    os.path.join(uchardet_dir, "LangModels/LangEnglishModel.cpp"),
    os.path.join(uchardet_dir, "LangModels/LangEsperantoModel.cpp"),
    os.path.join(uchardet_dir, "LangModels/LangEstonianModel.cpp"),
    os.path.join(uchardet_dir, "LangModels/LangFinnishModel.cpp"),
    os.path.join(uchardet_dir, "LangModels/LangFrenchModel.cpp"),
    os.path.join(uchardet_dir, "LangModels/LangGeorgianModel.cpp"),
    os.path.join(uchardet_dir, "LangModels/LangGermanModel.cpp"),
    os.path.join(uchardet_dir, "LangModels/LangGreekModel.cpp"),
    os.path.join(uchardet_dir, "LangModels/LangHebrewModel.cpp"),
    os.path.join(uchardet_dir, "LangModels/LangHindiModel.cpp"),
    os.path.join(uchardet_dir, "LangModels/LangHungarianModel.cpp"),
    os.path.join(uchardet_dir, "LangModels/LangIrishModel.cpp"),
    os.path.join(uchardet_dir, "LangModels/LangItalianModel.cpp"),
    os.path.join(uchardet_dir, "LangModels/LangLatvianModel.cpp"),
    os.path.join(uchardet_dir, "LangModels/LangLithuanianModel.cpp"),
    os.path.join(uchardet_dir, "LangModels/LangMacedonianModel.cpp"),
    os.path.join(uchardet_dir, "LangModels/LangMalteseModel.cpp"),
    os.path.join(uchardet_dir, "LangModels/LangNorwegianModel.cpp"),
    os.path.join(uchardet_dir, "LangModels/LangPolishModel.cpp"),
    os.path.join(uchardet_dir, "LangModels/LangPortugueseModel.cpp"),
    os.path.join(uchardet_dir, "LangModels/LangRomanianModel.cpp"),
    os.path.join(uchardet_dir, "LangModels/LangRussianModel.cpp"),
    os.path.join(uchardet_dir, "LangModels/LangSerbianModel.cpp"),
    os.path.join(uchardet_dir, "LangModels/LangSlovakModel.cpp"),
    os.path.join(uchardet_dir, "LangModels/LangSloveneModel.cpp"),
    os.path.join(uchardet_dir, "LangModels/LangSpanishModel.cpp"),
    os.path.join(uchardet_dir, "LangModels/LangSwedishModel.cpp"),
    os.path.join(uchardet_dir, "LangModels/LangThaiModel.cpp"),
    os.path.join(uchardet_dir, "LangModels/LangTurkishModel.cpp"),
    os.path.join(uchardet_dir, "LangModels/LangUkrainianModel.cpp"),
    os.path.join(uchardet_dir, "LangModels/LangVietnameseModel.cpp"),
    os.path.join(uchardet_dir, "CharDistribution.cpp"),
    os.path.join(uchardet_dir, "JpCntx.cpp"),
    os.path.join(uchardet_dir, "nsBig5Prober.cpp"),
    os.path.join(uchardet_dir, "nsCharSetProber.cpp"),
    os.path.join(uchardet_dir, "nsCJKDetector.cpp"),
    os.path.join(uchardet_dir, "nsEscCharsetProber.cpp"),
    os.path.join(uchardet_dir, "nsEscSM.cpp"),
    os.path.join(uchardet_dir, "nsEUCJPProber.cpp"),
    os.path.join(uchardet_dir, "nsEUCKRProber.cpp"),
    os.path.join(uchardet_dir, "nsEUCTWProber.cpp"),
    os.path.join(uchardet_dir, "nsGB2312Prober.cpp"),
    os.path.join(uchardet_dir, "nsHebrewProber.cpp"),
    os.path.join(uchardet_dir, "nsJohabProber.cpp"),
    os.path.join(uchardet_dir, "nsLanguageDetector.cpp"),
    os.path.join(uchardet_dir, "nsLatin1Prober.cpp"),
    os.path.join(uchardet_dir, "nsMBCSGroupProber.cpp"),
    os.path.join(uchardet_dir, "nsMBCSSM.cpp"),
    os.path.join(uchardet_dir, "nsSBCharSetProber.cpp"),
    os.path.join(uchardet_dir, "nsSBCSGroupProber.cpp"),
    os.path.join(uchardet_dir, "nsSJISProber.cpp"),
    os.path.join(uchardet_dir, "nsUniversalDetector.cpp"),
    os.path.join(uchardet_dir, "nsUTF8Prober.cpp"),
    os.path.join(uchardet_dir, "uchardet.cpp"),
]
sources += uchardet_sources

# Development-only opt-in; release builds keep their existing language standard.
cxx_standard = os.environ.get("CCHARDET_CXX_STANDARD")
if cxx_standard not in (None, "20"):
    raise ValueError("CCHARDET_CXX_STANDARD must be unset or '20'")

if sys.platform == "win32":
    extra_compile_args = ["/std:c++14", "/Zc:__cplusplus"]
else:
    extra_compile_args = ["-std=c++11"]
if cxx_standard == "20":
    extra_compile_args[0] = "/std:c++20" if sys.platform == "win32" else "-std=c++20"

# The Windows headers are shared by regular and free-threaded CPython, so the
# build must provide the configuration macro explicitly.
define_macros = []
if sys.platform == "win32" and sysconfig.get_config_var("Py_GIL_DISABLED"):
    define_macros.append(("Py_GIL_DISABLED", "1"))

setup(
    package_dir={"": "src"},
    packages=[
        "cchardet",
        "cchardet.cli",
    ],
    ext_modules=[
        Extension(
            "cchardet._cchardet",
            sources=sources,
            include_dirs=[uchardet_dir],
            language="c++",
            define_macros=define_macros,
            extra_compile_args=extra_compile_args,
        )
    ],
)

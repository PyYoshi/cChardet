#!/usr/bin/env python
# coding: utf-8

import glob
import os

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext
import sys

cchardet_dir = "src/cchardet/"
uchardet_dir = "src/ext/uchardet/src"
cchardet_sources = glob.glob(cchardet_dir + "*.cpp")
sources = cchardet_sources

uchardet_sources = [
    os.path.join(cchardet_dir, "_cchardet.pyx"),
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
print(sources)

class ccardet_build_ext(build_ext):
    user_options = build_ext.user_options + [
        ("cython-always", None, "run cythonize() even if .c files are present"),
        (
            "cython-annotate",
            None,
            "Produce a colorized HTML version of the Cython source.",
        ),
        ("cython-directives=", None, "Cythion compiler directives"),
    ]

    def initialize_options(self):
        super().initialize_options()
        self.cython_always = False
        self.cython_annotate = False
        self.cython_directives = None

    def finalize_options(self):
        return super().finalize_options()
    
    def finalize_options(self):
        need_cythonize = self.cython_always
        cfiles = {}

        for extension in self.distribution.ext_modules:
            for i, sfile in enumerate(extension.sources):
                if sfile.endswith(".pyx"):
                    prefix, ext = os.path.splitext(sfile)
                    cfile = prefix + ".c"

                    if os.path.exists(cfile) and not self.cython_always:
                        extension.sources[i] = cfile
                    else:
                        if os.path.exists(cfile):
                            cfiles[cfile] = os.path.getmtime(cfile)
                        else:
                            cfiles[cfile] = 0
                        need_cythonize = True

        if need_cythonize:

            # Double check Cython presence in case setup_requires
            # didn't go into effect (most likely because someone
            # imported Cython before setup_requires injected the
            # correct egg into sys.path.
            try:
                import Cython
            except ImportError:
                raise RuntimeError(
                    "please install cython to compile cchardet from source"
                )

            from Cython.Build import cythonize

            directives = {}
            if self.cython_directives:
                for directive in self.cython_directives.split(","):
                    k, _, v = directive.partition("=")
                    if v.lower() == "false":
                        v = False
                    if v.lower() == "true":
                        v = True
                    directives[k] = v
                self.cython_directives = directives

            self.distribution.ext_modules[:] = cythonize(
                self.distribution.ext_modules,
                compiler_directives=directives,
                annotate=self.cython_annotate,
                emit_linenums=self.debug,
            )

        return super().finalize_options()
        



setup(
    package_dir={"": "src"},
    packages=[
        "cchardet",
    ],
    ext_modules=[
        Extension(
            "cchardet._cchardet",
            sources=sources,
            include_dirs=[uchardet_dir],
            language="c++",
            extra_compile_args=['-std=c++11'] if sys.platform != "win32" else [], # Satisfy MSVC Compiler it should default to C++17
        )
    ],
    cmdclass={
        "build_ext":ccardet_build_ext
    }
)

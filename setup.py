#!/usr/bin/env python
# coding: utf-8

import os
import sys
import glob
from distutils.command.build_ext import build_ext

from setuptools import setup, Extension

have_cython = True
try:
    import Cython.Compiler.Main as cython_compiler
except ImportError:
    have_cython = False

cchardet_dir = 'src/cchardet/'
uchardet_dir = 'src/ext/uchardet/src'

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
    os.path.join(uchardet_dir, 'LangModels/LangArabicModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels/LangBulgarianModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels/LangCroatianModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels/LangCzechModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels/LangEsperantoModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels/LangEstonianModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels/LangFinnishModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels/LangFrenchModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels/LangDanishModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels/LangGermanModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels/LangGreekModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels/LangHungarianModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels/LangHebrewModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels/LangIrishModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels/LangItalianModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels/LangLithuanianModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels/LangLatvianModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels/LangMalteseModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels/LangPolishModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels/LangPortugueseModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels/LangRomanianModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels/LangRussianModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels/LangSlovakModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels/LangSloveneModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels/LangSwedishModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels/LangSpanishModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels/LangThaiModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels/LangTurkishModel.cpp'),
    os.path.join(uchardet_dir, 'LangModels/LangVietnameseModel.cpp'),
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
# cfg_vars = sysconfig.get_config_vars()
# for key, value in cfg_vars.items():
#     if type(value) == str:
#         cfg_vars[key] = value.replace("-Wstrict-prototypes", "")
#         # O3を指定したところで速度が向上するかは疑問である
#         # cfg_vars[key] = value.replace("-O2", "-O3")

cchardet_module = Extension(
    'cchardet._cchardet',
    sources=sources,
    include_dirs=[uchardet_dir],
    language='c++',
)

setup(
    cmdclass={'build_ext': build_ext},
    package_dir={'': 'src'},
    packages=['cchardet', ],
    scripts=['bin/cchardetect'],
    ext_modules=[
        cchardet_module
    ],
)

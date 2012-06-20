from distutils.core import setup, Extension
from Cython.Distutils import build_ext # use cython's buld_ext

setup(
    name = 'cchardet',
    url = r"https://github.com/PyYoshi/cChardet",
    description = 'Universal encoding detector',
    version = '0.1',
    cmdclass = {'build_ext': build_ext},
    ext_modules = [
        Extension("cchardet",
            sources = ["cchardet.pyx"],
            libraries=['charsetdetect'],
            language="c",
        ),

    ]
)
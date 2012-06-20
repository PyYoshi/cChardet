from distutils.core import setup, Extension
from Cython.Distutils import build_ext # use cython's buld_ext

charsetdetect_include_dir = r"."
charsetdetect_lib_dir = r"libcharsetdetect.dll"

setup(
    name = 'cchardet',
    description = 'Universal encoding detector',
    version = '0.1',
    cmdclass = {'build_ext': build_ext},
    ext_modules = [
        Extension("cchardet",
            sources = ["cchardet.pyx"],
            include_dirs=[charsetdetect_include_dir,],
            extra_objects=[charsetdetect_lib_dir,],
            language="c",
        ),

    ]
)
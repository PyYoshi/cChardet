#!/usr/bin/env python
# coding: utf-8

# python setup.py sdist --formats=gztar

from os.path import join
from glob import glob

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext

from distutils.ccompiler import CCompiler
from distutils.unixccompiler import UnixCCompiler
from distutils.msvccompiler import MSVCCompiler

DEBUG = False

compiler_opts = {
    CCompiler: {},
    MSVCCompiler: {
        'extra_compile_args': ['/EHsc'],
    },
}

if DEBUG:
    compiler_opts = {
        CCompiler: {'define_macros': [('DEBUG_chardet', '1')]},
        MSVCCompiler: {
            'extra_compile_args': ['/EHsc', '/Z7'],
            'extra_link_args': ['/DEBUG'],
        },
        UnixCCompiler: {
            'extra_compile_args': ['-g'],
            'extra_link_args': ['-g'],
        }
    }


class BuildExtSubclass(build_ext):
    def build_extensions(self):
        c = self.compiler

        # use the inheritance relationship and not names. That is
        # CCompiler will match all compilers, UnixCCompiler will match
        # mingw32 and cygwin as well and so on.
        opts = [v for k, v in compiler_opts.items() if isinstance(c, k)]
        for e in self.extensions:
            for o in opts:
                # the keys match the public attributes and are initialized
                # to empty lists.
                for attrib, value in o.items():
                    getattr(e, attrib).extend(value)

        build_ext.build_extensions(self)

cchardet_dir = join('src', 'cchardet')
charsetdetect_dir = join('src', 'ext', 'libcharsetdetect')
nspr_emu_dir = join(charsetdetect_dir, 'nspr-emu')
uchardet_dir = join(
    charsetdetect_dir, 'mozilla/extensions/universalchardet/src/base')

pyx_sources = glob(join(cchardet_dir, '*.pyx'))
sources = pyx_sources + [join(charsetdetect_dir, 'charsetdetect.cpp')] + glob(
    join(uchardet_dir, '*.cpp'))

cchardet_module = Extension(
    'cchardet._cchardet',
    sources=sources,
    include_dirs=[
        uchardet_dir,
        nspr_emu_dir,
        charsetdetect_dir
    ],
    depends=(glob(join(charsetdetect_dir, '*.h')) +
             glob(join(uchardet_dir, '*.h')) +
             glob(join(nspr_emu_dir, '*.h'))),
    language='c++',
)

setup(
    name='cchardet',
    author='PyYoshi',
    author_email='myoshi321go_at_gmail_dot_com',
    url='https://github.com/PyYoshi/cChardet',
    description='Universal encoding detector, faster than chardet.',
    long_description="""\
cChardet is high speed universal character encoding detector. It is a thin
Cython wrapper to charsetdetect. This library is faster than chardet.
""",
    use_scm_version={
        'version_scheme': 'guess-next-dev',
        'local_scheme': 'dirty-tag',
        'write_to': 'src/cchardet/_version.py'
    },

    setup_requires=[
        'setuptools>=18.0',
        'cython',
        'setuptools-scm>1.5.4'
    ],
    tests_require=[
        'pytest',
        'pytest-benchmark',
        'chardet'
    ],
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
    package_dir={"": 'src'},
    packages=['cchardet'],
    ext_modules=[
        cchardet_module
    ],
    cmdclass={'build_ext': BuildExtSubclass},
)

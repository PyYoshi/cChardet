#!/usr/bin/env python
# coding: utf-8

# TODO: WinはMSVC9で行うようにする

import ez_setup
ez_setup.use_setuptools()
import os,sys,platform,shutil
import subprocess
from setuptools import setup, Extension
import distutils.spawn as ds
from Cython.Distutils import build_ext

root = os.getcwd()
ext_dir = os.path.join(root,'ext_')
src_dir = os.path.join(root,'src')
build_dir = os.path.join(root,'build')
cchardet_dir = os.path.join(src_dir,'cchardet')
cchardet_source = os.path.join(cchardet_dir,"cchardet.pyx")
charsetdetect_dir = os.path.join(ext_dir, 'libcharsetdetect')
charsetdetect_build_dir = os.path.join(charsetdetect_dir,'build')

platform_os = platform.system()
cmake_cmd = "cmake"
if platform_os == "Windows":
    cmake_args = " -DBUILD_SHARED_LIBS=NO -DCMAKE_BUILD_TYPE:STRING=Release -G \"NMake Makefiles\""
else:
    cmake_args = " -DBUILD_SHARED_LIBS=YES -DCMAKE_BUILD_TYPE:STRING=Release".split()

def build_charsetdetect():
    if ds.find_executable(cmake_cmd) is None:
        print("Error: unable to configure libcharsetdetect!")
        print()
        print("CMake build tool (http://www.cmake.org/) to configure.")
        print("However, CMake is not found in your system.")
        print("Please install CMake before running the setup file.")
        sys.exit(-1)

    print("Configuring libcharsetdetect via CMake...")
    os.chdir(charsetdetect_dir)
    if platform_os == "Windows":
        import distutils.msvc9compiler as dm
        msvc_version = dm.get_build_version()
        vcvarsall_cmd = dm.find_vcvarsall(msvc_version)
        if os.path.exists(vcvarsall_cmd) is None:
            print("Error: Could not execute vcvarsall.bat!")
            print("Require Microsoft Visual Studio 2008.")
            sys.exit(-1)
        configure_file = "configure.bat"
        print("Create: %s" % configure_file)
        fp = file(configure_file,"w")
        fp_code_lines = [
            'call "%s"' % vcvarsall_cmd,
            '\n',
            'cmake %s'% cmake_args,
            '\n',
        ]
        fp.writelines(fp_code_lines)
        fp.close()
        print("Excec: %s"% configure_file)
        configure_file = os.path.join(charsetdetect_dir,configure_file)
        popen = subprocess.Popen(configure_file,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        print("===========================================")
        print(popen.stdout.read())
        print(popen.stderr.read())
        print("===========================================")
    else:
        try:
            ds.spawn(cmd=[cmake_cmd]+cmake_args,)
        except ds.DistutilsExecError:
            print("Error: error occurred while running CMake to configure libcharsetdetect!")
            print("You may want to manually configure libcharsetdetect by running cmake's tools:")
            print('cd %s' % charsetdetect_dir)
            print("cmake-gui or cmake")
            sys.exit(-1)

    print("Building libcharsetdetect ...")

    try:
        if platform_os == "Windows":
            execute_make_file = "exec_make.bat"
            print("Create: %s" % execute_make_file)
            fp = file(execute_make_file,"w")
            fp_code_lines = [
                'call "%s"' % vcvarsall_cmd,
                '\n',
                'nmake',
                '\n',
            ]
            fp.writelines(fp_code_lines)
            fp.close()
            execute_make_file = os.path.join(charsetdetect_dir,execute_make_file)
            popen = subprocess.Popen(execute_make_file,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            print("===========================================")
            print(popen.stdout.read())
            print(popen.stderr.read())
            print("===========================================")
        else:
            ds.spawn(cmd=["make"])
            if not os.path.exists(build_dir):
                os.makedirs(build_dir)
    except ds.DistutilsExecError as e:
        print("Error: Could not build libchardet!")
        print(e)
        sys.exit(-1)
    os.chdir(root)

build_charsetdetect()

cchardet_module = Extension("_cchardet",
    sources = [cchardet_source],
    libraries = ['charsetdetect'],
    include_dirs = [charsetdetect_dir],
    library_dirs = [charsetdetect_build_dir],
    language = "c++",
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
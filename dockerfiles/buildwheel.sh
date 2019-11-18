#!/bin/bash
set -e -x

ARCH=`uname -p`
echo "arch=$ARCH"

for V in cp38-cp38m cp37-cp37m cp36-cp36m cp35-cp35m cp27-cp27m cp27-cp27mu; do
    PYBIN=/opt/python/$V/bin
    rm -rf build src/cchardet/__pycache__ src/cchardet/*.cpp src/cchardet/*.pyc src/cchardet/*.so src/cchardet.egg-info src/tests/__pycache__ src/tests/*.pyc
    $PYBIN/pip install -r requirements-dev.txt
    $PYBIN/python setup.py bdist_wheel -p manylinux1_${ARCH}
done

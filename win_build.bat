rem setup packages
py -3.4-32 -m pip install -U pip cython wheel twine
py -3.4-x64 -m pip install -U pip cython wheel twine
py -2.7-32 -m pip install -U pip cython wheel twine
py -2.7-x64 -m pip install -U pip cython wheel twine

rem build package
py -3.4-32 setup.py bdist_wheel
py -3.4-x64 setup.py bdist_wheel
py -2.7-32 setup.py bdist_wheel
py -2.7-x64 setup.py bdist_wheel

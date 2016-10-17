test:
	python setup.py nosetests

clean:
	$(RM) -r build dist src/cchardet/__pycache__ src/cchardet/*.cpp src/cchardet/*.pyc src/cchardet/*.so src/cchardet.egg-info src/tests/__pycache__ src/tests/*.pyc

sdist: clean
	python setup.py sdist

pip:
	pip install -U pip cython tox nose chardet

twine:
	twine upload dist/*.whl
	twine upload dist/*.tar.gz

install: clean
	python setup.py install

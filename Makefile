test:
	python setup.py nosetests

clean:
	$(RM) -r build dist src/cchardet/__pycache__ src/cchardet/*.cpp src/cchardet/*.pyc src/cchardet/*.so src/cchardet.egg-info src/tests/__pycache__ src/tests/*.pyc

sdist:
	python setup.py sdist

pip:
	pip install -U pip cython tox nose chardet

twine:
	twine upload dist/*.whl dist/*.tar.gz

install: clean
	python setup.py install

build-manylinux1-wheel:
	docker pull quay.io/pypa/manylinux1_i686
	docker pull quay.io/pypa/manylinux1_x86_64
	docker run --rm -ti -v `pwd`:/project -w /project quay.io/pypa/manylinux1_i686   bash dockerfiles/buildwheel.sh
	docker run --rm -ti -v `pwd`:/project -w /project quay.io/pypa/manylinux1_x86_64 bash dockerfiles/buildwheel.sh

build: clean pip test sdist build-manylinux1-wheel

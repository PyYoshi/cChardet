test:
	python -m pytest

clean:
	$(RM) -r build dist src/cchardet/__pycache__ src/cchardet/*.cpp src/cchardet/*.pyc src/cchardet/*.so src/cchardet.egg-info src/tests/__pycache__ src/tests/*.pyc

sdist:
	python setup.py sdist --formats=gztar

pip:
	pip install -r requirements-dev.txt

twine:
	twine upload dist/cchardet-*.whl dist/cchardet-*.tar.gz

install: clean
	python setup.py install

build-wheels-on-manylinux2014:
	docker pull quay.io/pypa/manylinux2014_i686
	docker pull quay.io/pypa/manylinux2014_x86_64
	docker run --rm -ti -v `pwd`:/project -w /project quay.io/pypa/manylinux2014_i686   bash dockerfiles/buildwheel.sh
	docker run --rm -ti -v `pwd`:/project -w /project quay.io/pypa/manylinux2014_x86_64 bash dockerfiles/buildwheel.sh

build: clean pip test sdist build-wheels-on-manylinux2014

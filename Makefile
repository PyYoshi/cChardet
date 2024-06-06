.PHONY: clean
clean:
	$(RM) -r \
		.pytest_cache \
		.ruff_cache \
		build \
		dist \
		src/cchardet/__pycache__ \
		src/cchardet/*.cpp \
		src/cchardet/*.pyc \
		src/cchardet/*.so \
		src/cchardet.egg-info \
		tests/__pycache__ \
		tests/*.pyc \
		wheelhouse

.PHONY: cython
cython:
	cython --cplus src/cchardet/_cchardet.pyx

.PHONY: test
test: clean cython
	python setup.py build_ext -i -f
	pytest

.PHONY: lint
lint:
	ruff check

.PHONY: format
lint:
	ruff format

.PHONY: bench
bench: clean cython
	python setup.py build_ext -i -f
	python tests/bench.py

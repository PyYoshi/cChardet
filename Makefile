.PHONY: clean sync cython build test lint format check sdist
clean:
	$(RM) -r \
		.pytest_cache \
		.ruff_cache \
		build \
		dist \
		src/cchardet/cli/__pycache__ \
		src/cchardet/__pycache__ \
		src/cchardet/*.cpp \
		src/cchardet/*.pyc \
		src/cchardet/*.so \
		src/cchardet.egg-info \
		tests/__pycache__ \
		tests/*.pyc \
		wheelhouse

cython:
	uv run cython --cplus src/cchardet/_cchardet.pyx

sync:
	uv sync --locked

test: clean cython
	uv run python setup.py build_ext -i -f
	uv run pytest tests

lint:
	uv run ruff check

format:
	uv run ruff format

check: lint test

bench: clean cython
	uv run python setup.py build_ext -i -f
	uv run python tests/bench.py

build: clean
	uv build

sdist: build

# Release process

Releases are built from a `v*` tag and published with PyPI Trusted Publishing.
Before the first automated release, configure a PyPI trusted publisher for
this repository and the `build.yaml` workflow, then configure the GitHub
`pypi` environment with required reviewers. No long-lived PyPI token is used.

## Prepare the release

1. Change `version` and `__version__` in `src/cchardet/__init__.py` to the final
   version.
2. Replace `(Unreleased)` in `CHANGES.md` with the release date.
3. Run `make check` in the locked uv environment.
4. Run `uv build` and `uv run twine check dist/*`.
5. Verify the wheel smoke test through cibuildwheel on the release pull
   request.

After the release commit is merged, create and push a signed `vX.Y.Z` tag. The
workflow builds the sdist and platform wheels independently, verifies that the
tag matches the package version, and waits at the protected `pypi` environment
before publishing. Trusted Publishing uploads attestations by default.

Finally, install the published version into a clean uv environment and run a
basic `detect()`, `detect_all()`, incremental detection, and CLI smoke test.

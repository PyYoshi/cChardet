# SPDX-License-Identifier: MIT
"""Inspect build configuration without compiling or importing the extension."""

import runpy
import sys
import sysconfig
import types
from pathlib import Path

import pytest


@pytest.mark.parametrize("platform,default", [("linux", "-std=c++11"), ("win32", "/std:c++14")])
@pytest.mark.parametrize("standard", [None, "20"])
def test_standard(monkeypatch, platform, default, standard):
    captured = {}
    fake = types.ModuleType("setuptools")
    fake.Extension = lambda name, **kwargs: kwargs
    fake.setup = lambda **kwargs: captured.update(kwargs)
    monkeypatch.setitem(sys.modules, "setuptools", fake)
    monkeypatch.setattr(sys, "platform", platform)
    monkeypatch.setattr(sysconfig, "get_config_var", lambda name: 0)
    if standard is None:
        monkeypatch.delenv("CCHARDET_CXX_STANDARD", raising=False)
    else:
        monkeypatch.setenv("CCHARDET_CXX_STANDARD", standard)
    runpy.run_path(str(Path(__file__).resolve().parents[1] / "setup.py"))
    extension = captured["ext_modules"][0]
    flag = default if standard is None else ("/std:c++20" if platform == "win32" else "-std=c++20")
    assert extension["extra_compile_args"] == (
        [flag, "/Zc:__cplusplus"] if platform == "win32" else [flag]
    )
    assert any(source.endswith("uchardet.cpp") for source in extension["sources"])
    assert any(source.endswith(".pyx") for source in extension["sources"])


@pytest.mark.parametrize("standard", ["", "11", "14", "17", "23", "20 -march=native"])
def test_invalid_standard(monkeypatch, standard):
    monkeypatch.setenv("CCHARDET_CXX_STANDARD", standard)
    fake = types.ModuleType("setuptools")
    fake.Extension = lambda *args, **kwargs: None
    fake.setup = lambda **kwargs: pytest.fail("invalid standard reached setup")
    monkeypatch.setitem(sys.modules, "setuptools", fake)
    with pytest.raises(ValueError, match="must be unset or '20'"):
        runpy.run_path(str(Path(__file__).resolve().parents[1] / "setup.py"))

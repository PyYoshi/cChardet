<!-- SPDX-License-Identifier: MIT -->
# v3 sdist build の要件と独立再build確認

2026-09-21時点の `pyproject.toml` / `setup.py` / `MANIFEST.in` に基づく。
今後のC++20既定化や最低compiler versionの決定とは区別する。

## 現在の要件

| 対象 | 要件・責務 |
| --- | --- |
| Python | 3.11以上。対象ABIに合うPython本体・開発header・link環境 |
| build backend | `setuptools.build_meta`、`setuptools>=77` |
| Cython | `>=3.2.9,<3.4`。sdistのpyxからwrapperを生成する |
| 非Windows compiler | 現在の既定は `-std=c++11` を扱えるC++ compiler |
| Windows compiler | 現在の既定は `/std:c++14 /Zc:__cplusplus` を扱えるMSVC環境 |
| C++20試験 | `CCHARDET_CXX_STANDARD=20` の明示指定。wrapper/native両方へ適用 |
| 開発環境管理 | uv `>=0.9.26`、`uv sync --locked` |

上記規格の対応だけで任意の古いcompiler versionが保証されるわけではない。
CPython・Cythonが要求するcompiler/SDK条件も満たす必要があり、最低実装versionを
この表から逆算して宣言しない。

Python extensionはsetuptoolsが同梱uchardet sourceを直接compileする。
この経路ではsystem uchardet、CMake、Ninjaは不要。standalone native開発の
CMake 3.21以上 / preset環境とは別である。Git checkoutでのbuildはsubmodule初期化が
必要だが、完成したsdistには必要なnative cpp/header/tabが同梱される。

isolated buildの依存解決と開発用uv.lockは同一ではない。再現性が必要なbuildでは
実際のbuild依存versionを記録し、必要に応じてuvのbuild constraintsを使用する。
`--offline` は必要な依存がcache済みの場合だけ利用でき、未取得依存を解決する機能ではない。

## 2026-09-21の独立再build

対象cChardet head `a3b93a4`、native `8e183f6b370bf3d26f764c708cda6fe45d651491`。
既存checkoutからsdistを作り、その **tar.gzを入力として** C++20 wheelをbuildした。
tar.gzからのbuildはGit submoduleやcheckoutの既存objectを参照しない。

```sh
uv build --sdist --offline --out-dir /disk/sdist-check
CCHARDET_CXX_STANDARD=20 uv build /disk/sdist-check/cchardet-2.3.0.tar.gz \
  --wheel --offline --out-dir /disk/sdist-check/wheels
uv venv --offline --python /path/to/python3.14 /disk/sdist-env
uv pip install --offline --python /disk/sdist-env/bin/python \
  /disk/sdist-check/wheels/cchardet-2.3.0-cp314-cp314-linux_x86_64.whl
/disk/sdist-env/bin/python tools/wheel_smoke.py
```

出力先は新しいdirectoryを使う。例のversion / ABI / platformは今回の観測値であり、
次releaseの名前を固定する指定ではない。

- CPython 3.14.2 / GCC 16.2.1 / Linux x86_64 で成功。
- wrapperとnative sourceのcompile行末 `-std=c++20` を確認。
- 独立uv環境へwheelをinstallし、既存の短いwheel smokeが成功。
- sdist SHA-256: `cf5c41de71baf7d09e4194fa919da53c670f1bad0b433f54cb3b9c54dc5aa447`
- wheel SHA-256: `429aa1f0d269290bba3bd8e130396bc537e68d788f7852d124e6767eb31b8366`

これはsource同梱とbuild経路の確認であり、wheelのbit-for-bit再現性試験ではない。
ローカル `linux_x86_64` wheelをmanylinux認証済みと扱わない。
最低OS、他compiler、free-threaded ABIのsdist再buildを今回追加検証したわけではない。
通常CIの `Verify distributions` も維持し、今回の補助確認で置き換えない。

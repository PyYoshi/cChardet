<!-- SPDX-License-Identifier: MIT -->
# ARM64旧runtimeのQEMUによる限定検証

2026-09-21。既存C++20 wheelをARM64のglibc 2.24 / CPython 3.11.1で実行した。
x86_64ホスト上のQEMU user-modeによる検証であり、ARM実機・性能・全ABIの確認ではない。
現在のdevを再buildした結果でもない。C++規格や最低対応条件は変更しない。

## 固定した資材

- wheel供給元: [C++20 run 35513146332](https://github.com/PyYoshi/cChardet/actions/runs/35513146332)、artifact `wheels-Linux`
- build head: `87a69e3df6b1014f2b19b050103b14bbcd7a6c72`
- checkout merge: `71508b9a5b741793b75ea9ec998f638541d5b9f2`
- wheel: `cchardet-2.3.0-cp311-cp311-manylinux_2_24_aarch64.manylinux_2_28_aarch64.whl`
- wheel SHA-256: `8f5b8f35f58da7d7f641997d99839316146026e9284e29c11c38064a28eef3f9`
- 元の `tools/wheel_smoke.py` SHA-256: `5a378038f50036d407794aef9072967192d820968dc3d6c2f7410ae97e5a972f`
- image: `quay.io/pypa/manylinux_2_24_aarch64@sha256:3911e0f2b4d8859716571c05c103c40e1e07986b9668af5bdcae77a63f8f8e2d`
- QEMU: `qemu-aarch64 version 10.2.2 (qemu-10.2.2-1.fc44)`
- static emulator SHA-256: `e4cbe197554147c4944a9a2593cd4e46bc00f630cb58196dc9170659ef1f253d`
- 下記runner SHA-256: `038ce71459c3554f568ef9e7de1ebcfa424c9d1d4a0117d894574041c46ec1ef`

imageのarchitectureはarm64。圧縮layer合計344,076,972 bytes、
Docker表示の展開size 1,444,606,013 bytes。取得・保存予算内で追加した。
旧imageは開発の標準環境として推奨するものではなく、互換性確認だけに使う。

## 実測

終了code 0で、既存smokeのASCII、buffer入力、仏語候補/language、incremental、
CLI JSON、型情報同梱assertが成功した。Pythonと共有libraryの観測値:

```text
Python 3.11.1 (main, Dec 20 2022, 07:06:36) [GCC 6.3.0 20170516]
glibc 2.24
/runtime/site/cchardet/__init__.py
/lib/aarch64-linux-gnu/libc-2.24.so
/usr/lib/aarch64-linux-gnu/libstdc++.so.6.0.22
```

wheelをnetwork無効・no-index・no-depsでinstallした。新しいglibc/libstdc++は持ち込まず、
QEMU自体はx86_64 static binaryとしてmountした。検証終了後の一時containerは自動削除済み。
hostのbinfmt設定、既存smoke、cChardetのコードは変更していない。

最初の試行はinstall成功後にModuleNotFoundErrorで停止した。
同一プロセス内でpipを実行したため、起動時に存在しなかったsiteディレクトリのimport cacheを
更新する必要があった。runnerへ `importlib.invalidate_caches()` を追加すると成功した。
この初回失敗をwheelのABI非互換とは数えない。

## 再現runner

次の内容を `/disk/arm64-smoke-runner.py` として保存する。
開発依存の管理はuvを維持する。ここでのpipは旧imageのPythonによる
ローカルwheel install検証だけに使用する。

binfmtを登録せずにCLI subprocessも動かすため、runnerは元smokeの
`subprocess.check_output` に渡るPython起動へ明示的にQEMUを付ける。
assert、CLI引数、結果の解析は元smokeのまま。通常のsubprocess起動そのものを
ARM実機で検証した結果とは区別する。

```python
# SPDX-License-Identifier: MIT
"""Run the unchanged wheel smoke with explicit QEMU child dispatch."""
import json
import importlib
import os
from pathlib import Path
import runpy
import subprocess
import sys

wheel = sys.argv[1]
sys.argv = ["pip", "install", "--no-index", "--no-deps", "--no-cache-dir",
            "--disable-pip-version-check", "--target", "/runtime/site", wheel]
try:
    runpy.run_module("pip", run_name="__main__")
except SystemExit as exc:
    if exc.code not in (None, 0):
        raise
sys.path.insert(0, "/runtime/site")
importlib.invalidate_caches()

# The host has no ARM binfmt handler. Prefix only the smoke's Python child;
# do not alter the imported module, assertions, CLI arguments, or output.
check_output = subprocess.check_output
launches = []
def qemu_check_output(command, *args, **kwargs):
    assert isinstance(command, list) and command[0] == sys.executable, command
    launches.append(command)
    return check_output(["/emulator", *command], *args, **kwargs)
subprocess.check_output = qemu_check_output
runpy.run_path("/checks/wheel_smoke.py", run_name="__main__")
assert len(launches) == 1
import cchardet
print(json.dumps({
    "python": sys.version,
    "executable": sys.executable,
    "glibc": os.confstr("CS_GNU_LIBC_VERSION"),
    "package": cchardet.__file__,
    "child_launches": launches,
    "mapped_libraries": sorted({line.split()[-1] for line in
                                Path("/proc/self/maps").read_text().splitlines()
                                if "libc-" in line or "libstdc++" in line}),
    "smoke": "passed",
}, sort_keys=True))
```

## コンテナ実行

以下のhost pathは手元の保存先に置き換え、先に上記hashを照合する。
repository全体やDocker socket、認証情報はコンテナへ渡さない。

```sh
docker pull --platform linux/arm64 quay.io/pypa/manylinux_2_24_aarch64@sha256:3911e0f2b4d8859716571c05c103c40e1e07986b9668af5bdcae77a63f8f8e2d
timeout --signal=TERM --kill-after=10s 120s docker run --rm \
  --name cchardet-arm64-cp311-smoke --platform linux/arm64 \
  --network none --read-only --cap-drop ALL --security-opt no-new-privileges \
  --user 1000:1000 --tmpfs /tmp:rw,nosuid,nodev,size=16m \
  --tmpfs /runtime:rw,exec,nosuid,nodev,size=128m,mode=1777 \
  --mount type=bind,src=/usr/bin/qemu-aarch64-static,dst=/emulator,readonly \
  --mount type=bind,src=/disk/cxx20-wheels,dst=/wheels,readonly \
  --mount type=bind,src=/path/to/tools/wheel_smoke.py,dst=/checks/wheel_smoke.py,readonly \
  --mount type=bind,src=/disk/arm64-smoke-runner.py,dst=/checks/runner.py,readonly \
  --env PYTHONPATH=/runtime/site --env PYTHONDONTWRITEBYTECODE=1 \
  --entrypoint /emulator \
  quay.io/pypa/manylinux_2_24_aarch64@sha256:3911e0f2b4d8859716571c05c103c40e1e07986b9668af5bdcae77a63f8f8e2d \
  /opt/python/cp311-cp311/bin/python /checks/runner.py \
  /wheels/cchardet-2.3.0-cp311-cp311-manylinux_2_24_aarch64.manylinux_2_28_aarch64.whl
```

timeoutはDocker clientの上限。タイムアウト時にはcontainerが残っていないか
`docker ps -a --filter name=cchardet-arm64-cp311-smoke` で確認し、
残っている場合だけ、その検証用containerを停止・削除する。
今回の成功実行では残留containerはなかった。

## 残る検証

- ARM64のCPython 3.12 / 3.13 / 3.14 / 3.14tでの旧runtime実行
- ARM実機、旧kernel、実CPU機能、並列性・性能
- 最低macOS / Windows / CRT
- 将来C++20標準library機能を追加した実wheel

この1 ABIの成功だけで#116やC++20既定化を完了扱いにはしない。

<!-- SPDX-License-Identifier: MIT -->
# 最低runtimeの限定的な実行確認

2026-09-21。C++20指定で作成済みのwheelを、build時より古いglibcで実行した。
対象は **CPython 3.11〜3.14 / 3.14t、Linux x86_64 の5 wheel**。
対応platformや既定C++規格を変更する判断ではない。

## 固定した入力

- [C++20 wheel run 35513146332](https://github.com/PyYoshi/cChardet/actions/runs/35513146332)
- build head: `87a69e3df6b1014f2b19b050103b14bbcd7a6c72`
- checkout merge commit: `71508b9a5b741793b75ea9ec998f638541d5b9f2`
- artifact: `wheels-Linux`、compressed artifact size 5,971,981 bytes
- wheel: `cchardet-2.3.0-cp311-cp311-manylinux_2_24_x86_64.manylinux_2_28_x86_64.whl`
- wheel SHA-256: `52f710453b57df64c935a026110d35bd33fb98c67976170693e3d7c327cd9b8b`
- smoke: `tools/wheel_smoke.py`
- smoke SHA-256: `5a378038f50036d407794aef9072967192d820968dc3d6c2f7410ae97e5a972f`
- image: `quay.io/pypa/manylinux_2_24_x86_64@sha256:a332ca25073bf71c6be54fe3c18e477418eedc194685f7263624ef4dfac91f9e`

imageは[PyPA公式のmanylinux_2_24](https://github.com/pypa/manylinux#manylinux_2_24-debian-9-based---eol)。
このimageのサポートは終了しており、開発用の標準環境として推奨するものではない。
取得layerは圧縮約372 MB、Docker表示の展開sizeは1,552,022,224 bytes。
wheel約6 MBと合わせて既存の取得・保存予算内。新しいCI buildや外部課金は行っていない。

## 実測結果

container内で `getconf GNU_LIBC_VERSION` とPython自身の情報を確認した。

```text
glibc 2.24
Python 3.11.1
3.11.1 ('glibc', '2.24') /runtime/site/cchardet/__init__.py 2.3.0
```

wheelをoffline installし、既存smokeが終了code 0で成功した。
ASCII、bytes/bytearray/memoryview、短い仏語cp1252の候補・language、incremental API、
CLI JSON、型情報同梱の既存assertを実行した。大入力やfuzzは実行していない。

最初の試行は `/tmp` へのinstall後に `failed to map segment from shared object` で失敗した。
`/proc/mounts` で `/tmp` が `noexec` と確認できたため、ホストのmount設定は変更せず、
一時containerの `/runtime` だけをexec可能にして再試行した。成功後はcontainerを削除した。
初回失敗をglibc/ABI非互換として数えない。

## 再現手順

以下のhost pathは自分の保存先へ置き換える。取得はネットワーク有効なhost側で行い、
実行containerへはDocker socket、認証情報、repository全体を渡さない。
wheelとsmokeだけをread-only mountする。新しい空のdownload directoryを使う。

```sh
gh run download 35513146332 --repo PyYoshi/cChardet \
  --name wheels-Linux --dir /disk/cxx20-wheels
docker pull quay.io/pypa/manylinux_2_24_x86_64@sha256:a332ca25073bf71c6be54fe3c18e477418eedc194685f7263624ef4dfac91f9e
docker run --rm --network none --read-only --cap-drop ALL \
  --security-opt no-new-privileges --user 1000:1000 \
  --tmpfs /tmp:rw,nosuid,nodev,size=16m \
  --tmpfs /runtime:rw,exec,nosuid,nodev,size=128m,mode=1777 \
  --mount type=bind,src=/disk/cxx20-wheels,dst=/wheels,readonly \
  --mount type=bind,src=/path/to/tools/wheel_smoke.py,dst=/checks/wheel_smoke.py,readonly \
  --env PYTHONPATH=/runtime/site --env PYTHONDONTWRITEBYTECODE=1 \
  quay.io/pypa/manylinux_2_24_x86_64@sha256:a332ca25073bf71c6be54fe3c18e477418eedc194685f7263624ef4dfac91f9e \
  /bin/sh -c '/opt/python/cp311-cp311/bin/python -m pip install \
    --no-index --no-deps --no-cache-dir --disable-pip-version-check --target /runtime/site \
    /wheels/cchardet-2.3.0-cp311-cp311-manylinux_2_24_x86_64.manylinux_2_28_x86_64.whl && \
    /opt/python/cp311-cp311/bin/python /checks/wheel_smoke.py'
```

hostの開発環境はuvを維持する。ここでのpipは、既存の旧imageにあるPythonを使った
wheel install検証だけであり、新しい開発環境の依存管理には使わない。
成功判定の前にwheel / smokeのhashを照合する。GitHub artifactの保持期限を超えた場合、
別のwheelを同じ実測結果として扱わず、新しいartifactの検証として記録する。

## 3.12〜3.14 / free-threadedの追加確認

同日の追加試験では、同じrunの残り4 ABIも終了code 0でsmokeに成功した。
3.14tでは既存smoke内のGIL無効assertも通過した。

| ABI | 実行Python | wheel SHA-256 |
| --- | --- | --- |
| cp312-cp312 | 3.12.14 | `a180f354cc5fc1585536cb5135dfa7a8a82f0a06500a98fef2f8d9f9a43b2b6a` |
| cp313-cp313 | 3.13.15 | `5cc18c07c74e9d8628ca087dfd9c0e8172cc088a39aca3b776402bdf0b34898c` |
| cp314-cp314 | 3.14.7 | `d56ba8f08ae493ac18d3d44ac1eead21efa7f7fc6338568a1e083b7faabb5c54` |
| cp314-cp314t | 3.14.7 free-threading | `a708d3053a2c123a99f6d78a2d71dc2c0e2abb62dddb3c0bd65af4179688d81a` |

旧imageにはこれらのPythonがないため、別の公式imageからinterpreterだけを取り出した。
供給元は次の固定digestであり、実行環境そのものには使っていない。

```text
quay.io/pypa/manylinux2014_x86_64@sha256:21c37461985655aaa25ed3a923b28e6c9d4dd9e10edc0281eb50385184bddd31
```

供給元の圧縮layer合計は398,277,015 bytes、取り出した4ディレクトリは約283 MiB。
取得・保存予算内で、追加のCI buildは行っていない。
`/opt/_internal/cpython-3.12.14`、`cpython-3.13.15`、`cpython-3.14.7`、
`cpython-3.14.7-nogil` を停止中の一時containerから `docker cp` で保存し、
親ディレクトリを旧imageの `/interpreters` にread-only mountした。
取り出し用containerは削除済み。元imageや保存したinterpreterは保持している。

先の再現コマンドにこのmountを追加し、Pythonを
`/interpreters/cpython-<version>/bin/python3`、wheelのABIを表の値へ変更する。
各ABIは独立したcontainerと空の `/runtime/site` で検証する。
新しいglibcやlibstdc++、OpenSSLを旧imageへコピーしていない。
各interpreterの `platform.libc_ver()` は `('glibc', '2.24')` を返し、
wheel import後の `/proc/self/maps` では全4 ABIで以下の旧image内ライブラリを確認した。

```text
/lib/x86_64-linux-gnu/libc-2.24.so
/usr/lib/x86_64-linux-gnu/libstdc++.so.6.0.22
```

pipはSSL依存が不足するため `Disabling truststore since ssl support is missing` と警告した。
今回は `--network none` / `--no-index` / `--no-deps` によるローカルwheelだけの
installであり、TLS検証を無効化してネットワーク取得したわけではない。
このinterpreter移植環境を汎用Python環境やSSL対応の検証として扱わない。
また、対象は上記の固定buildであり、現在のdev全体を再buildした結果ではない。

## まだ確認していない範囲

- ARM64のglibc 2.24実行
- 最低macOS / Windows / CRTでの実行
- C++20の追加標準ライブラリ機能をwheelへ入れた場合のruntime依存
- 古いkernel、異なるCPU、任意のLinux distributionの網羅
- detector全APIや並列性の完全な正当性

containerはホストkernelを共有する。旧distribution全体の実機試験とは区別する。
今回の成功をもって #116 やC++20既定化gateをすべて完了とはしない。

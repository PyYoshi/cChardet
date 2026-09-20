<!-- SPDX-License-Identifier: MIT -->
# 最低runtimeの限定的な実行確認

2026-09-21。C++20指定で作成済みのwheelを、build時より古いglibcで実行した。
対象は **CPython 3.11 / Linux x86_64 の1 wheelだけ**。
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

## まだ確認していない範囲

- CPython 3.12〜3.14/3.14tとARM64のglibc 2.24実行
- 最低macOS / Windows / CRTでの実行
- C++20の追加標準ライブラリ機能をwheelへ入れた場合のruntime依存
- 古いkernel、異なるCPU、任意のLinux distributionの網羅
- detector全APIや並列性の完全な正当性

containerはホストkernelを共有する。旧distribution全体の実機試験とは区別する。
今回の成功をもって #116 やC++20既定化gateをすべて完了とはしない。

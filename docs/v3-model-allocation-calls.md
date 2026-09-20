<!-- SPDX-License-Identifier: MIT -->
# 単一モデル reuse 中の allocation 呼び出し

2026-09-21。[uchardet #36](https://github.com/PyYoshi/uchardet/pull/36) の
実験用toolで、[native計時](v3-native-model-timing.md)と同じモデル・入力の
allocation API call-siteを別途観測した。engineや公開API、既定modelは変更していない。

## 観測範囲

64-bit Linux、GCC 16.2.1、C++11/O2、非LTOの静的libraryを使用した。
linkerの `--wrap` で、静的リンク時に解決される以下の呼び出しを数える。

- malloc / calloc / realloc / free
- throwing・unalignedのscalar/array new / delete

起動時に全8経路を意図的に呼び、期待回数に一致することを確認する。
自己検証の成功後、入力/scratch/proberを確保し、128回warm-upしてから
1回のreset/filter/feed/confidenceを観測する。通常版も別buildし、最終snapshotと
reset後の観測が計測版と一致することを確認した。時間計測との併用は拒否する。

入力I/O、buffer確保、prober構築、出力は区間外。
shared library内部、aligned/nothrow/sized/custom allocator、mmapは対象外。
counterはsingle-thread診断専用である。

## 結果

Paris Stories validationのfull cp1252 16文書、合計40,777 bytesを使用。
trainingの変更や再調整、独立holdoutの参照は行っていない。

| モデル | 文書数 | 各文書の対象8 counter | 通常版との観測差分 |
| --- | ---: | --- | ---: |
| legacy French | 16 | すべて0 | 0 |
| identity生成model | 16 | すべて0 | 0 |
| filtered生成model | 16 | すべて0 | 0 |

これは選択した入力のwarm reuseに限った**API呼び出し回数**であり、
物理allocation数、live/peak memory、確保byte数や全detectorの計測ではない。
特に初回構築・scratch確保を除外しているため、「メモリを使用しない」とは解釈しない。
全detectorのallocation/memory gateを通過したとは扱わない。

## 検証と再現

GCCでモデル関連86 tests成功。Clang 22.1.8でも自己検証と通常版との一致を確認した。
native PR #36は全11 CI成功後、devの`df0ef3957247499428a3637a372e0cd5c9268ca7`
へ統合済み。参照更新後のcChardetローカル検証は305 passed、27 skipped、
76 subtests passed（native library/filter tool指定）。skipは検証済みとは扱わない。
人工・小入力は空、ASCII、accent付き文字、2,048 bytesの入力を含む。
これは追加fuzzやP01の保留作業を再開したものではない。

native source commit: `c58c7c910b41ebc294d6f6e7569ef025618c78ae`。
library SHA-256: `cbfafc66f7aeb38952991b0fe3a621b6abf47aedf12bbc8eda3541908f28649a`。
corpus/modelの由来は[既存モデル比較](v3-legacy-model-comparison.md)と同じ。

```sh
uv run --no-project python models/experimental/model_allocations.py \
  /disk/filter-comparison-identity-fr-v1.json /disk/filtered-training-fr-v1.json \
  /disk/paris-stories-generated-1/manifest.json /disk/native-build/src/libuchardet.a \
  /disk/allocation-report.json
```

report content hash:
`400603891813af879c69d9e9a42b35d12609b6152eb5e435d2fc2752e73acacc`。
file SHA-256: `24fc3035a06f608caddca6d0d05a7b961fff94ad2972f6f3f85665d7d714c39a`。
別の出力先へ再build・再実行したreportとの全byte一致も確認した。
生reportはGit管理外に保持する。生成modelの配布条件や識別品質は、この計測では解決しない。

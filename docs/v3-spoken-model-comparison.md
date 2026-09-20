<!-- SPDX-License-Identifier: MIT -->
# 学習corpusを変えた固定generatorの比較

2026-09-21。[会話training corpus](v3-spoken-training-corpus.md)を使用し、
既存のidentity/filtered profileを変更せずにFrench cp1252モデルを別artifactとして生成した。
旧Rust bookモデル、既存legacy table、評価入力、閾値は変更していない。
この比較は単一proberの反応であり、全detectorのencoding accuracyではない。

## 条件

- 旧学習元: Rust book introduction 1章。新学習元: Paris Stories 32録音。
- 新モデルはParis-only。Rustとの混合学習ではない。
- データ量・domain・文書数が同時に変わるため、個別要因の因果効果は分離できない。
- 同じidentity / native whole-document filter、character順序、95/99 mass区分を使用。
- `NOT_ENGINE_CALIBRATED` / `UNDETERMINED`を維持。modelはGit管理外に保存。
- native static library SHA-256:
  `cbfafc66f7aeb38952991b0fe3a621b6abf47aedf12bbc8eda3541908f28649a`。
- wrapper: GCC 16.2.1、C++11/O2、Python 3.14.2。
  実行toolのnative revisionは`613245051da2e208489e5056c967af6b01c8f528`。

原文とnative filterを再観測する`validate --manifest`も成功した。
旧モデルも現行toolで再実行し、両corpus・全3モデルの文書別観測が以前の公開reportと一致した。
追加の独立holdout予測、閾値探索、validationの再分割は行っていない。

## cp1252 positive入力での観測

category 0の累積回数と全sequence数を記録する。学習の未観測pairだけでなく、
頻出matrix外の文字を含むsequenceも影響するため、「誤判定数」とは呼ばない。

| 評価corpus | 学習元 / profile | category 0 / 全sequence | 内部confidence範囲 |
| --- | --- | ---: | ---: |
| Paris validation 16文書 | Rust / identity | 288 / 3,837 | −0.006417〜0.678264 |
| 同上 | Paris / identity | 52 / 3,837 | 0.479648〜0.837211 |
| 同上 | Rust / filtered | 503 / 3,837 | −0.236911〜0.532397 |
| 同上 | Paris / filtered | 82 / 3,837 | 0.358901〜0.837921 |
| 同上 | legacy | 0 / 3,837 | 0.785962〜0.851188 |
| Rust validation 1章 | Rust / identity | 82 / 3,220 | 0.704291 |
| 同上 | Paris / identity | 30 / 3,220 | 0.759757 |
| 同上 | Rust / filtered | 222 / 3,220 | 0.535302 |
| 同上 | Paris / filtered | 55 / 3,220 | 0.742848 |
| 同上 | legacy | 0 / 3,220 | 0.849141 |

全positive文書は入力末尾まで処理しstateはdetectingだった。
今回の生成profile内ではcategory 0が減り内部スコアも高い範囲になったが、
confidenceは正解確率ではない。legacyとはcategoryの学習由来も異なる。
候補順位の改善、false-positive低下、legacyを上回る精度を示す表ではない。

## 同一文章のUTF-8 control

Paris validationでは、旧・新・legacyの全モデルで16/16 pairがcp1252側のスコアを高くした。
この指標は旧モデルも同じため、分離の件数が改善したとは言わない。
新identityのUTF-8範囲は−0.410316〜0.072449、filteredは−0.423882〜0.067451。
UTF-8側の一部スコアも高くなるため、positive側の上昇だけを成功条件にしない。

Rust validationのUTF-8 bytesはstrict cp1252 decode不可で、全モデルが途中でrejectする。
この構造的な棄却をParisの全入力処理と同列の統計的分離とは扱わない。

## 再現

```sh
uv run --no-project python models/experimental/sequence_training.py train \
  /disk/paris-training/manifest.json fr /disk/paris-identity.json
uv run --no-project python models/experimental/filtered_training.py train \
  /disk/paris-training/manifest.json fr /disk/build/benchmark/uchardet-filter-profile \
  /disk/paris-filtered.json
uv run --no-project python models/experimental/paired_controls.py \
  /disk/paris-identity.json /disk/paris-filtered.json \
  /disk/paris-validation/manifest.json validation /disk/build/src/libuchardet.a \
  /disk/paired-report.json
```

Rust validationは[前回のpaired評価](v3-paired-encoding-controls.md)と同じmanifestを使用する。
両corpusで別出力先への再build・再観測を実行し、report全byteの一致を確認した。

| artifact | content hash | file SHA-256 |
| --- | --- | --- |
| identity training | `73cc98234e5532d7e8b05c4bd7f8bf802727325dadf41babb865adb143bc2b84` | `a4bfee8e80f760321320b79a65e7f3e2da040251ccb9ac42bbe57f4aa032131f` |
| filtered training | `8f80555a7a7f1fbd4ad368aaf95158428af7ad3fd750b4ed1f85e4e84b2997fd` | `a5ee5758d1011424a31f5cd85dba5fe183946eadf450d4f611eabaec2ac1af78` |
| Paris paired report | `eae530e4d473554750a6f6c871c5b1d88ced7a5145d2ed65d2df8d887d02976d` | `bcaf8a56037906f0b185f63f14a9cfef64323d53e7a749c767a9847a950140a5` |
| Rust paired report | `754576e8e0f393a688e134bc371598d2722d533368845bee63ee06d61ec66e0d` | `9d27de03421369e16843380809db9b1886f0363ce990b256dd8617159db5ed60` |

全detectorの識別精度、confidence校正、この新モデルの性能/memory、独立domain上の評価、
生成modelの配布条件は未完了。既定modelは置換せず、P01も再開しない。

後続の[限定処理コスト](v3-spoken-model-cost.md)では単一proberの計時とallocation call-siteを
観測した。trial末尾側に変動があり、全体の性能/memory gate完了とは扱わない。

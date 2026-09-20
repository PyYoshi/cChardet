<!-- SPDX-License-Identifier: MIT -->
# 既存 French モデルと生成モデルの native 比較

2026-09-21。[uchardet #33](https://github.com/PyYoshi/uchardet/pull/33) の
[比較tool](../src/ext/uchardet/models/experimental/NATIVE_COMPARISON.ja.md)で、
`Windows_1252FrenchModel`、identity、filteredを同条件で観測した。
既存tableをコピーせず、library内のsymbolを直接参照する。

## 条件

- 同じstatic library、GCC 16.2.1、C++11/O2のharness、検証済み入力bytes
- 文書全体を一回filterし、独立した一つのproberへ一回feed
- [固定training artifact](v3-filtered-training.md)を変更しない
- [validation corpus](v3-filtered-evaluation.md)も変更しない（Paris Stories16録音、Rust book別章1件）
- 独立holdout・新規取得・再学習・threshold調整は行わない

既存モデルのtraining corpusとの重複は追跡できないので `legacy_training_overlap=UNKNOWN`。
生成モデル側のsplit監査を、既存モデル側の独立性の証明には流用しない。

## 結果

下表はproberの内部confidence。公開APIの確率やencoding正解率ではない。
全モデル・全17文書でstateはdetectingだった。

| corpus | legacy | identity | filtered |
| --- | ---: | ---: | ---: |
| Paris Stories、16文書の最小〜最大 | 0.785962〜0.851188 | −0.006417〜0.678264 | −0.236911〜0.532397 |
| Rust book、1文書 | 0.849141 | 0.704291 | 0.535302 |

Paris Storiesで負値はidentity1件・filtered2件・legacy0件。非有限値・1超は全モデル0件。
native counterの合計は次のとおり。

| corpus / model | negative category / 全sequence | 頻出matrix外letter |
| --- | ---: | ---: |
| Paris / legacy | 0 / 3,837 | 0 |
| Paris / identity | 288 / 3,837 | 26 |
| Paris / filtered | 503 / 3,837 | 51 |
| Rust book / legacy | 0 / 3,220 | 0 |
| Rust book / identity | 82 / 3,220 | 8 |
| Rust book / filtered | 222 / 3,220 | 27 |

既存モデルのnegative categoryは、新規profileの「training未観測matrix pair」と
同義とは限らない。counterにはmatrix外letterによるnegative加算も含まれる。
学習方法・量子化・文字order・ratioが異なるため、単一の要因へ差を帰属させない。

## 判断

全件detectingだったことは生成モデル特有の失敗ではなく、既存モデルでも同じだった。
一方、生成モデルが既存モデルに対して良い識別性能を持つという証拠はまだない。
今回の観測を理由にratioを変更してconfidenceだけを引き上げることはしない。

正例のFrench/cp1252だけではfalse positiveや他encodingとの識別能力を評価できない。
候補競合・negative control・未使用data・性能の評価前にモデルを採用しない。
生成モデルの採用案は保留。既存モデル・公開API・default動作は維持する。

## 再現

native commit `50df203`、Python 3.14.2。library SHA-256:
`cbfafc66f7aeb38952991b0fe3a621b6abf47aedf12bbc8eda3541908f28649a`。
モデル・corpus hashは前記の固定artifactと同じ。

```sh
uv run --no-project python models/experimental/native_comparison.py \
  /disk/filter-comparison-identity-fr-v1.json /disk/filtered-training-fr-v1.json \
  /disk/paris-stories-generated-1/manifest.json validation \
  /disk/native-build/src/libuchardet.a /disk/paris-native-model-comparison-v1.json
```

Rust bookにはvalidation専用manifestを指定する。両方ともfresh buildから2回実行し、
report全byteが一致した。記録はGit管理外に保持する。

| report | content hash | file SHA-256 |
| --- | --- | --- |
| Paris | `5a3224d9d71651fa473b0500bae4467475012209703bed6b7abdd251dee96c45` | `f2dd054d0b8fac2680e1417504831ee7d5e79811620b346d1648787814ab52bc` |
| Rust book | `35089a3f57cd3ab643e616b897c0300b51460994ad3e04a3f5bf48aa6df62223` | `df44728d832d8c8f73a8ea21b9de4d5ff77a56dcad0990ef64f4afbd45aaebc0` |

各reportはsource別のconfidence bit/counter/stateと、モデル別header/library/compiler/binaryの
由来を含む。legacy tableの学習元を新たに解明したものではない。
P01の安全性調査・fuzz・大入力停止調査は再開しない。

[native CI](https://github.com/PyYoshi/uchardet/actions/runs/35538406458) 全11チェック成功。
モデル関連70テストはnative toolsありで全成功、なしでは62成功/8skip。
実比較harnessはLinux diagnosticsで実行した。追加4テストはローカルClangでも成功。
cChardetローカル統合は289 passed / 27 skipped / 76 subtests passed。

後続の[同一文章のencoding対照](v3-paired-encoding-controls.md)でUTF-8 variantへの反応も
観測した。構造的にdecode不能な対照と、decode可能だが別の文字列になる対照を分けている。

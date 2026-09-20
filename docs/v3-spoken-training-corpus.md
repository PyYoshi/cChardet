<!-- SPDX-License-Identifier: MIT -->
# 会話ジャンルの学習用corpus追加

2026-09-21。Rust bookの1章だけに依存する学習条件を広げるため、
[uchardet #37](https://github.com/PyYoshi/uchardet/pull/37)でParis Storiesの
upstream trainを別profileとして取り込んだ。既存validationをtrainingへ再分割していない。
詳細な取得・隔離・再現手順は[日本語仕様](../src/ext/uchardet/corpus/sources/PARIS_TRAINING.ja.md)。

## 固定元と取得量

revisionはvalidationと同じ `dec76f7a1731318b033c578d534410b0a3d4ea5c`。
README/LICENSEのCC BY-SA 4.0表示と本文を含む旨を確認し、出典・contributorsを保持した。
upstream train、README、LICENSEの3file、計2,214,251 bytesを追加取得した。
test・音声・外部参照先は取得していない。本文・生成物はGit管理外の `archives/v3-corpus/` に置く。
toolのMITとcorpusのCC BY-SA 4.0は別で、生成modelの配布条件は未決定のまま。

## 取込前の検出と隔離

元データ1,387文に対して、二つの問題を実際のstrict取込で検出した。

| 検出内容 | 対象 | 措置 |
| --- | ---: | --- |
| 録音identity欠落 | 27文 | sentence IDをrecipeに列挙し隔離。identityを推測しない |
| 既存validationと同じ録音 | 1録音38文 | 録音全体をtrainingから隔離。validationは維持 |

raw cacheは保持し、隔離理由・ID・hashをingestion reportへ残す。
未知の欠落・重複まで自動skipすることはなく、残るsource hash/origin/sentence IDの
cross-split重複は出力前に拒否する。文章のcp1252変換可否や検出スコアで選別していない。

## 生成・再現結果

- 採用入力: 32録音、1,322文、抽出UTF-8 87,681 bytes。
- full UTF-8/cp1252の64 variants全件strict往復成功。変換不能skipは0。
- 別出力先への取込・生成は、manifest・本文を含め全fileのbyteが一致した。
- training32 + validation16の48 source、1,128 pairを既存char5 profileで照合し、近似候補0。
- corpus基盤49 tests、source取込39 tests成功。
- native全11 CI成功後、`613245051da2e208489e5056c967af6b01c8f528`をdevへ統合。
- 参照更新後のローカル統合検証は314 passed、27 skipped、79 subtests passed。
  native library/filter toolを指定した結果であり、skipを検証済みとは扱わない。

近似候補0でも話者や意味内容の独立性、翻訳や部分転載の不存在は保証しない。
同じ会話domain内のvalidationであり、独立holdoutの代用ではない。
今回の成果は学習用入力の追加であり、model品質の改善を示す結果ではない。
generatorの仕様・閾値は変更せず、model再生成・検出精度評価もこの取込では行っていない。

## 識別hash

| 対象 | content hash / SHA-256 |
| --- | --- |
| train raw file | `558c125ecb84f4e16ef8d8871368e24b8c6054446a06da9a5211fc67abb65a1d` |
| training manifest | `fdd8e32a85cd6c4604929f62d5402f50bfc69b59b81cc3d08b85fe9494998466` |
| 既存validation manifest | `6340aff3b3d424fced87b782d75036c64152b4840eec98a05dc9a5b4f90216aa` |
| overlap report | `33f50a11f9dfd879273c781da9c5663611dfbaa07183de62f068349fa5304b22` |

次の比較では既存のRust-onlyモデルを保存し、固定generatorで新しい学習corpusから作った
モデルを別artifactとして扱う。validationの結果を見て閾値を繰り返し調整することや、
独立holdoutを開くことは、この追加をもって許可・実施したとは扱わない。

<!-- SPDX-License-Identifier: MIT -->
# 同一 filter 入力でのモデル比較結果

2026-09-21。[uchardet #31](https://github.com/PyYoshi/uchardet/pull/31) の比較toolを使用。
[training結果](v3-filtered-training.md)の identity / native-filter モデルを固定し、
同じ native-filter 出力統計に対して比較した。再学習やパラメータ変更はしていない。
手順・制約は[日本語仕様](../src/ext/uchardet/models/experimental/FILTERED_EVALUATION.ja.md)。

## 結論

今回の2 corpusでは、filtered trainingの方が未観測文字・pairが増えた。
native filterと学習入力を合わせても、少量の学習文書で減った証拠を補うことはできない。
少なくとも「filter適合だけで品質改善した」という根拠にはならない。

これは**固定tableのcoverage**であり、encoding正解率でもconfidenceでもない。
filteredモデルの採用は推奨せず、学習データの多様性とprober統計の照合を残す。
validationで見つけた文やpairをtrainingへ移して帳尻を合わせない。

## Corpus別結果

各行の分子/分母はmicro集計。未観測pairの分母は、そのモデルのmatrix内pair。
matrix外pairも別に示すので、小さなmatrixが有利に見える問題を隠さない。

| corpus / model | 未観測letter / 全letter | matrix外 / 全letter pair | 未観測pair / matrix内pair |
| --- | ---: | ---: | ---: |
| Rust book / identity | 8 / 3,790 | 6 / 3,220 | 76 / 3,214 |
| Rust book / filtered | 27 / 3,790 | 25 / 3,220 | 197 / 3,195 |
| Paris Stories / identity | 26 / 4,837 | 33 / 3,837 | 255 / 3,804 |
| Paris Stories / filtered | 51 / 4,837 | 62 / 3,837 | 441 / 3,775 |

Rust bookはtrainingと同じ書籍の別章1件（validation、raw 27,265 bytes / filtered 4,456 bytes）。
独立した著者・ドメインの評価ではない。元manifestのvalidation source metadataだけから
`encodings=["cp1252"]`, `byte_limits=[None]`, `formats=["text"]` で専用corpusを生成した。
independent sourceの本文は読んでいない。

Paris Storiesは既存validation 16録音、raw合計40,777 bytes / filtered 5,876 bytes。
全16文書のmacro未観測pair率はidentity **6.716%**、filtered **11.685%**。
全ての文書で分母が定義可能だった。raw文書サイズは全件1 KiB以上4 KiB未満。
元テキストの権利・話者/domain制約は[会話corpusの記録](v3-spoken-corpus.md)を参照する。

Tatoeba Frenchの既存manifestはoriginが文ごとのIDではなく共通の
`tatoeba:cc0-pilot`。現在の同一origin拒否gateにより比較前に停止した。
個々の文が重複しているとの判定ではない。source provenanceを都合よく書き換えず、
この結果には含めない。group単位評価とsource単位評価を分離する設計は別途必要。

## 再現条件とhash

- evaluator commit: `51b08fd`、Python 3.14.2
- native binary・training artifact: [前段の固定hash](v3-filtered-training.md)
- native filter: whole-document、最大65536 bytes、10秒timeout、実行binaryを前後照合
- Rust validation corpus content hash: `d2216d4be95ad16858caf544e0d432dd756e8238c3804ceed524283d7605d762`
- Paris corpus content hash: `6340aff3b3d424fced87b782d75036c64152b4840eec98a05dc9a5b4f90216aa`
- Rust report content hash: `332f2566b400a3959ca48468cb7273356f07664b130efb1150350e3cbb2799cd`
- Paris report content hash: `e40f57359d5ae983cc5d6169f3bf747b7587258068e0894e8d4bca1ae1311539`

それぞれ2回実行して全byteが一致した。reportファイルSHA-256:

- Rust: `75f0a15b1de0f6bf0a97e968527501143a03c32f575296129758d0dd714d8d7f`
- Paris: `4cab08bfc0ec5030bc609d380996b085d9a2e254651ccec9865201a3a4ae1bf9`

report本体はsource別統計・macroの厳密分数・rawサイズ層別集計・依存hashを持ち、
Git管理外の `archives/v3-corpus/` に保持する。頻度統計は匿名化ではない。
新規取得は0 bytes、モデルの配布条件は `UNDETERMINED` のまま。

[native CI](https://github.com/PyYoshi/uchardet/actions/runs/35537150641) は全11チェック成功。
モデル関連60テストはnative toolありで全成功、なしでは58成功/2skip。
実native接続はLinux diagnosticsで確認した。cChardetローカル統合は
279 passed / 27 skipped / 76 subtests passed。

## 未完了

proberのsequence counterとconfidence校正、候補競合を含むencoding/language精度、
新旧モデルの性能比較は未完了。通常のdetectorへ新規modelを登録していない。
P01は再開しない。この比較だけで #123 / #125 / #126 を完了扱いにしない。

後続の[native prober照合](v3-native-sequence-probe.md)では、Paris Storiesの全32組で
整数counterの一致を確認した。confidence校正・全detectorの正解率は引き続き未確認。

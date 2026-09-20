<!-- SPDX-License-Identifier: MIT -->
# v3 採用gateと未確定の移行範囲

2026-09-20時点。これは3.0の機能確約やrelease checklistの完了報告ではない。
開発基盤の統合と、利用者へ提供する既定動作への採用を区別する。

## 基盤と標準採用の境界

| 対象 | 確認済み | 採用前に残るもの | 現在の扱い |
| --- | --- | --- | --- |
| C++20 | native matrix、Python 30 wheelのbuild/installed smoke | 最低runtime、新たに導入する標準library機能のavailability | build opt-in。既定規格は維持 |
| 内部trace | group直下のstate/active、language detectorのstate/counter、同一feedの小fixture出力一致 | reject/ranking理由、一般的な無効時cost検証 | 開発用・既定OFF。公開APIではない |
| corpus生成 | manifest検証、split監査、変換不能の明示、実pilot再生成一致 | domain/言語の多様性、translation/近重複確認、独立評価 | 生成基盤として採用。精度向上とは数えない |
| 新規model形式 | 明示契約、人工tableのC++構造体適合、provenance、未較正training profileの再現性 | engine filter適合、未使用data上の品質、配布条件 | 実験用。既存modelを置換しない |
| 保存観測分析 | corpus hash照合、exact/compatible/decode-equivalent分離 | 実Web頻度、独立corpus、原因診断 | 評価tool。candidate順位を変えない |

細部の根拠は[基盤結果](v3-foundation-results.md)、[C++20配布記録](v3-cxx20-distribution.md)、
[改善順位](v3-improvement-priorities.md)に分けて保持する。

## 今回の2件の試作枠

### 1. 先頭BOMのchunk buffering

local `v3/bom-prototype`に保存した非デフォルト試作。統合・公開APIへの追加はしていない。
一部のchunk差分を改善しても、全candidate、confidence、done時点、短い入力の扱いまで
同等になるとは限らない。BOMなしUTF-16の問題を解決する試作でもない。

[P01](v3-decision-log.md)の検証保留に依存するため、追加検証・性能比較・採用判断は保留。
現時点の推奨は「採用せず保存」であり、失敗とも成功とも確定しない。

### 2. 新規のモデル生成pipeline

raw byte-bigram試作、SequenceModel形式契約、training仕様の精緻化を同じ試作枠として扱う。
旧generatorの修復や既存tableの書き写しを前提としない。

生成の決定性、構造体適合、統計上のloss、encoding精度は別々の指標である。
一つの成功を他の成功へ読み替えない。既存engineとのfilter適合とconfidence較正を確認するまで、
形式が正しいtableでも既定modelへ登録しない。生成物の配布条件は未確定のまま保持する。
接続前に照合すべき入力・統計・feed境界は[SBCS training契約の調査](v3-sbcs-training-contract.md)
に整理した。sourceを読んだ根拠と実行検証を区別する。

2026-09-21追記: native filter training、同一入力coverage、実prober counter接続、
[既存Frenchモデルとの比較](v3-legacy-model-comparison.md)まで実装・観測した。
今回のvalidationでは生成モデルのnegativeカテゴリが多く、採用を支持する識別品質の証拠はない。
整数counterの一致だけでconfidence校正やencoding正解率を達成したとは扱わない。
候補競合、negative control、未使用data、性能、生成modelの権利確認が残るため採用は保留する。

後続の[同一文章のencoding対照](v3-paired-encoding-controls.md)と
[単一proberのnative計時](v3-native-model-timing.md)を追加した。
限定的な反応差と処理コストは測定済みだが、全detectorの識別精度、confidence校正、
リクエスト単位のtail latency・memory/allocationは未確認で、標準採用の保留は維持する。

[reuse中のallocation呼び出し](v3-model-allocation-calls.md)も個別に観測した。
対象call-siteの0回と、全detectorのallocation/memory gateは区別する。
初回確保・peak/live memory・共有library内部等は未測定のままである。

[会話trainingを使う固定generator比較](v3-spoken-model-comparison.md)では、
2つのvalidation corpusでcategory 0が減少し、positive側の内部スコアが高い範囲になった。
ただしpaired分離件数は旧モデルと同じで、encoding accuracy改善・標準採用の根拠にはしない。

[候補競合を含めた評価](v3-full-engine-model-comparison.md)まで進めた結果、Paris validation
のcp1252 16入力でdecode-equivalentがlegacy 16件に対しidentity 5件、filtered 7件だった。
したがって、この固定モデルの標準採用は推奨しない。単に接続が未完了なのではなく、
限定的ながら実際の識別品質に反証が得られた状態である。
他言語・別domain・大入力・incremental全体については、この結果から推測しない。
generator基盤と非デフォルト観測targetは維持し、内部選抜の分析を次の課題にする。

[専用tuningを用いたratio感度実験](v3-ratio-sensitivity.md)では、24録音で再学習した
2 profileの因子0.90が事前基準を満たした。ただしこれは8録音のtuning内で選んだ候補であり、
標準採用の保留は維持する。旧32録音版と再学習・ratio変更版の結果を混同しない。

[因子を固定したincremental評価](v3-ratio-chunks.md)ではchunkによる精度・候補差が残った。
1-byteの悪化はlegacyにもあるが、7-byteでは生成modelがlegacyより低いdecode-equivalent
件数となった。whole-inputのtuning成功をincremental採用gateの成功へ読み替えない。

## 互換性とmigration

v3では必要な破壊的変更を許容する方針だが、現段階で具体的な公開API変更を決めたわけではない。
現在の変更は両repositoryの`dev`内の基盤整備であり、v2系・`master`・releaseには反映しない。

API、既定`max_bytes`、候補順位、confidence、最低OS/Python、既定modelを変える場合は、
変更ごとに旧新比較・影響を受ける入力・移行手順・代替策を用意する。
「majorが変わるから説明不要」とはしない。変更が未確定な今は架空の移行手順を書かない。

## 最終報告へ残す判断

- D01: runtime切り捨てが必要になった場合の最低対応条件。現在は切り捨てを提案しない。
- D02/D03: candidate動作やmodelの標準採用。現時点では品質証拠が不足しており採用を提案しない。
- D04: 生成modelの配布条件。toolのMITや入力文の許諾だけから自動的に決めない。
- P01: 保留した検証の再開環境・担当。既存sanitizer CI成功で代用しない。
- D06: `master`反映とrelease。今回の自走範囲外のまま。

これらの判断待ちを理由に、独立したcorpus・generator・分析toolの作業まで止めない。
#125/#126はこの文書の追加だけではcloseしない。

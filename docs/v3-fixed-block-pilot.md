<!-- SPDX-License-Identifier: MIT -->
# 第3試作: 固定block native adapter

2026-09-22。対象は非デフォルトの検証基盤であり、Python APIや標準modelの変更ではない。
[native PR #46](https://github.com/PyYoshi/uchardet/pull/46)を全11 CI成功後devへ統合した。
固定点: `058aec784a0891103584a79c7c52b217340db67d`。

## 目的と契約

外部feedのchunk境界によらず、同じ入力prefixを同じ固定block列でnative coreへ渡す。
block長・evidence上限は明示指定、初期pilotは最大4096 bytes・processあたり10秒。
空feedではflushしない。finishで端数を一度flushし、resetでpending/core状態を破棄する。
adapter保持bufferはblock長分。native内部のmemory上限を保証するものではない。
coreのdone観測位置と、呼出し側がdoneを受け取るfeed境界は区別する。

既定targetではbuildせず、installもしない。one-shot/streamingの公開契約には未導入。
旧whole-inputとの候補・confidence一致を約束せず、差分を評価対象とする。

## 検証結果

- 通常小入力1000比較で、直接C APIへ同じ固定blockを渡した候補・confidence bit列・done・処理位置と一致。
- metadata/CLI等の追加7 unittest成功。native benchmark suiteは31成功・5 skip。
- 固定tuning 16入力×4内部block×5外部chunkの320観測で、同じ内部block長なら候補・最終done・core処理位置が一致。
- 同じbuildのlegacy whole-inputは保存済み観測と全件一致。report再実行で全byte一致。
- native最終head `676dde447a3b3a6c777901ca8244e714fc770a72` の11 CI成功
  （run `35622532551`）。新pilot実行はLinux diagnosticsであり、全OS実行とは扱わない。
- cChardet統合のローカルpytest: 355 passed / 15 skipped / 88 subtests。
  fixed-block/trace/filter/static-libraryの既存検証用binaryを環境指定して実行した。
  前固定点からnative `src/`に差分なし。Python既定処理へadapterは導入していない。

| 内部block | cp1252 exact / 8 | cp1252 decode-equivalent / 8 | UTF-8 exact / 8 | 旧wholeと候補全体が異なる入力 / 16 |
| --- | --- | --- | --- | --- |
| 1 | 0 | 0 | 8 | 16 |
| 7 | 2 | 6 | 8 | 16 |
| 64 | 4 | 8 | 8 | 16 |
| 1024 | 4 | 8 | 8 | 4 |

旧wholeはcp1252 exact 4/8・decode-equivalent 8/8。境界一貫性と品質向上は別である。
この小さなtuning結果だけでblock長を選ばない。compatible/superset指標は未評価。
標準modelだけを使用し、生成modelを混ぜていない。独立holdoutは未開封。

## 再現とprovenance

実行手順は[native日本語文書](../src/ext/uchardet/benchmark/fixed-block.ja.md)。
private report: `archives/v3-corpus/fixed-block-tuning-v3.json`。
content hash: `d198e153f5167a561d5809f011717def074fb3ab3991d84fa0f438bad816c63d`。
固定元report hash: `5d28f112f1ed472e1a438df9790f9e2f50c9aa0e216943059e2bb51621d0c8c1`。
入力・binary・driver hashと全観測をreportへ保持する。raw corpus/modelをGitへ追加しない。

## 残作業・採用境界

- 追加platformでのpilot実行、初回確保・request p95・memory/allocation計測。
- 別言語/domainの評価。既存Paris validationと限定warm reuse性能は下記の追加評価済み。
  独立holdoutは採用判断まで温存する。
- block長・evidence上限・done・EOF・resetの公開契約とPython APIへの採用判断。
- 選定後のwheel/API・性能・精度の回帰、移行手順。

#125/#126はこの基盤統合だけでcloseしない。P01の大入力・追加安全性検証は保留のまま。

## 追加評価: validationとnative性能

[native PR #47](https://github.com/PyYoshi/uchardet/pull/47)で比較driverを拡張した。
全11 CI成功（run `35625470786`）後、`2863aeaf420d766c05dfa8c44604c33f20fe9d91`へ統合。
native benchmark suiteは38成功・5 skip。cChardet統合時のローカルpytestは
362 passed / 15 skipped / 94 subtests（各検証用binaryを環境指定）。
既定engine/model/APIは変更せず、内部block候補も1/7/64/1024のまま固定した。

既存Paris validationの32入力（cp1252/UTF-8各16）×4 block×5外部chunk、
640観測で同じ内部block長なら候補/done/core処理位置が一致。再実行reportも全byte一致。
既に分析したvalidationであり、未参照独立評価と称しない。

| 内部block | cp1252 exact / 16 | cp1252 decode-equivalent / 16 | UTF-8 exact / 16 |
| --- | --- | --- | --- |
| 1 | 0 | 0 | 16 |
| 7 | 3 | 4 | 16 |
| 64 | 11 | 16 | 16 |
| 1024 | 11 | 16 | 16 |

旧wholeはcp1252 exact 11/16、decode-equivalent 16/16。64/1024はtop-1件数を維持するが、
候補全体はそれぞれ32/32・8/32入力で旧wholeと異なる。
report content hash: `07945ca56191edfab5afad23c492e708849d2e64b941b5c1338d5e2c89f63c19`。

### native処理コスト

固定tuning 16入力で、旧whole・直接固定block・adapterの3方式を同じnative binaryで比較。
CPU2固定、各入力100反復×7試行、17 warmup、順番を循環、独立2 run。
I/O・Python・初期detector/buffer確保は区間外、reset/feed/finalize/最小限の結果取得は区間内。
GCC16.2.1 Release、powersave。affinityは周波数固定やCPU占有を保証しない。

64-byteは旧whole比の5%超悪化が再現した。外部wholeの文書別medianでは
run1で14/16入力（+4.76〜9.30%）、run2で15/16入力（+4.84〜8.55%）が該当。
1024は同条件で両runとも5%超なし（run1 +0.28〜1.24%、run2 +0.19〜1.15%）。
外部1-byteではadapterのloop/copyコストも含み、集計上の1024はwhole比約3%の増分。

時間は文書別trial平均の合計から取るmedianで、corpus passやrequest p95ではない。
全試行・入力hash・binary/driver hashを保存した
[native性能記録](../src/ext/uchardet/benchmark/fixed-block-timing.ja.md)を参照。

判断: 1/7は品質、64は性能に採用上の問題が残る。1024は追加評価候補だが、
限定corpusでのtop-1件数・warm reuse性能だけでは標準採用しない。
候補/confidenceの差、初回allocation・memory、公開契約の確認を続ける。

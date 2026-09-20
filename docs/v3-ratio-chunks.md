<!-- SPDX-License-Identifier: MIT -->
# 固定ratioモデルのincremental評価

[ratio感度実験](v3-ratio-sensitivity.md)の因子0.90を固定し、tuning 8録音の
full cp1252/UTF-8全16入力をwhole / 1 / 7 / 64 / 1024-byteで比較した。
追加の係数探索、入力選別、validation再予測、独立holdout開封は行っていない。

## 結果

cp1252 strict decode-equivalent件数（各8入力）:

| chunk | legacy | identity 1 | identity 0.90 | filtered 1 | filtered 0.90 |
| --- | ---: | ---: | ---: | ---: | ---: |
| whole | 8 | 4 | 8 | 5 | 8 |
| 1 | 0 | 0 | 0 | 0 | 0 |
| 7 | 6 | 4 | 4 | 4 | 4 |
| 64 | 8 | 4 | 7 | 5 | 8 |
| 1024 | 8 | 4 | 8 | 5 | 8 |

UTF-8 exactは全条件8/8。confidenceは全候補で有限かつ[0,1]内だった。
wholeに対する候補完全一致の不一致は、1/7/64-byteで各modelとも16/16、
1024-byteで各modelとも4/16。encoding/language順序の不一致とは別に集計している。
final doneとfirst done offsetのwholeとの差は今回0件。

1-byteの悪化はlegacyにもあり、今回のratio変更だけに起因しない。
7-byteでは生成modelがlegacyより悪い。wholeの8/8をもってincremental gateを満たしたとは
扱わず、標準採用は保留する。因子を追加探索してこの結果に合わせ込まない。

## Filterまでの切り分け

既存の[filter診断](v3-filter-profile.md)と[自然文での観測](v3-filter-validation.md)で
分かっていたchunk依存を、今回のtuning先頭cp1252文書でも確認した。
入力1,708 bytes、SHA-256は
`c8920476cada520722870177598a16a4d0f64351c0a0fb25a443c4c470787902`。

| filter呼び出し | 出力bytes | 出力の隣接byte pair数 |
| --- | ---: | ---: |
| whole | 275 | 274 |
| 1-byteごと | 51 | 50 |

既存`uchardet-filter-profile`で同一入力を観測した。これはmodelのfrequent pair数ではなく、
filter出力の全隣接byte pair数である。
`FilterWithoutEnglishLettersToBuffer`の高位bit遭遇flagと区間先頭は呼び出し内のlocal変数で、
groupはchunkごとにfilterを呼ぶ。一方、single-byte proberは前のorderを保持する。
したがって分割により入力証拠と隣接関係が変わり、confidence倍率だけで同じ証拠には戻せない。
ただし他proberも競合するため、最終判定の差をこの1要因ですべて説明したとはしない。

## 再現と制約

[uchardet PR #42](https://github.com/PyYoshi/uchardet/pull/42)の
`models/experimental/ratio_chunks.py IDENTITY FILTERED MANIFEST SWEEP BUILDS OUTPUT`を使用。
24録音学習artifact、固定training/tuning manifest、ratio sweepと検証済みbuildを指定する。
各入力4 KiB以下・各process10秒上限で、全400観測を2回実行しreport全byte一致を確認した。
関連102 unittestが成功。標準model・engine・公開APIは変更していない。

private report: `archives/v3-corpus/paris24-ratio-chunks-v1.json`。
content hash: `5d28f112f1ed472e1a438df9790f9e2f50c9aa0e216943059e2bb51621d0c8c1`。
同modelのwhole差、同chunkのlegacy差、同profileの因子1差を分離して保存する。
feed回数は生観測に保持するが一致指標に含めない。first done offsetはfeed後の観測位置。
大入力・追加fuzz・P01対象の停止調査は再開していない。

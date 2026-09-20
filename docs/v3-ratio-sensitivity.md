<!-- SPDX-License-Identifier: MIT -->
# 生成Frenchモデルのratio感度実験

## 結論と適用範囲

24録音から生成したidentity / filtered modelの両方で、ratio因子0.90が次段階の候補となった。
ただし8録音のtuning上で選んだ結果であり、未使用dataの精度・確率校正・標準採用を
証明するものではない。既存model、公開API、engine共通の係数は変更していない。

## 事前固定と結果

[uchardet PR #41](https://github.com/PyYoshi/uchardet/pull/41)の`fa32d55`で、予測前に
4因子と採否基準を固定した。詳細はnativeの`models/experimental/RATIO_VARIANT.ja.md`。
親モデルと[tuning baseline](v3-tuning-corpus.md)をhashで固定し、同じ16入力を全条件で使用。
生成modelのratioのみ変更し、byte order / category table / 他modelは維持した。

cp1252の母数は各8入力。全条件でUTF-8 exact/decode-equivalentは8/8、
language一致は両encodingで各8/8。範囲外confidenceは全16入力の全候補から数える。

| model | 因子 | cp1252 exact | decode-equivalent | 範囲外confidence | 判定 |
| --- | ---: | ---: | ---: | ---: | --- |
| identity | 1.00 | 1 | 4 | 0 | 対照 |
| identity | 0.95 | 4 | 7 | 0 | 適格 |
| identity | 0.90 | 8 | 8 | 0 | 次段階候補 |
| identity | 0.80 | 8 | 8 | 1 | 不採択 |
| filtered | 1.00 | 2 | 5 | 0 | 対照 |
| filtered | 0.95 | 5 | 7 | 0 | 適格 |
| filtered | 0.90 | 8 | 8 | 0 | 次段階候補 |
| filtered | 0.80 | 8 | 8 | 2 | 不採択 |

採否条件はcp1252のdecode-equivalent改善、UTF-8とlanguageの非悪化、全confidenceが
有限かつ[0,1]内であること。適格候補はdecode-equivalent、exact、因子が1に近い順で選んだ。
0.80の値はclampしておらず、精度だけを見て採用することも避けた。
この選択はprofile間の優劣を決めるものではない。

## 再現性

標準targetは保存したlegacy baseline、因子1は各profileのbaselineと候補・confidence bits・
done観測が完全一致した。8条件すべてを2回観測し、report全体がbyte一致した。
nativeの関連100テストは実験targetの試験を含め成功している。

private report: `archives/v3-corpus/paris24-ratio-sweep-v1.json`。
content hash: `8ebbe3a8e939488bf89aa1fa2c3d6169a494c99e2cf23faf9dc37419f93cd6d6`。
全候補、採否、親model、変換tool、build source/binaryのprovenanceをreportへ保持する。
再現コマンドはnativeの`ratio_sweep.py IDENTITY FILTERED MANIFEST BASELINE BUILDS OUTPUT`。
引数には24録音版model、新training/tuning manifest、固定baselineを使う。

## 残る検証

同じtuningで候補gridを増やしたり、0.90の周辺を微調整したりしない。
次段階では因子を固定したまま、未使用data、incremental、性能、confidenceの妥当性、
他言語・encodingへの影響を検証する。今回はvalidationの新たな予測と独立holdoutの
開封は行っていない。生成modelの配布条件も未確定で、P01の保留を維持する。

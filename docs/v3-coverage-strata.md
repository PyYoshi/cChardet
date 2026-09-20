<!-- SPDX-License-Identifier: MIT -->
# 固定model coverageの文書平均・入力サイズ別評価

2026-09-21。[会話corpus評価](v3-spoken-corpus.md)のmicro集計に、
文書ごとの等重み平均とbyte長区間を追加した。
native実行・再学習・閾値調整は行わず、未較正の固定tableを使う。

## 指標の意味

microは全出現数の分子・分母を足した比率で、長文の寄与が大きい。
macroは分母が正の各文書の比率を等重みで平均する。
分母0の文書は0点にせず除外し、指標ごとの有効・未定義文書数を記録する。
保存値は厳密な分数。以下の百分率は読みやすさのため小数6桁に丸めた。

| 指標 | micro (%) | 文書macro (%) |
| --- | ---: | ---: |
| 頻出letter coverage | 99.812777 | 99.811233 |
| 未知letter率 | 0.187223 | 0.188767 |
| matrix pair coverage | 99.752397 | 99.756002 |
| matrix内の未観測pair率 | 2.396426 | 2.387837 |

全指標で有効16文書・未定義0文書。旧reportの全document観測とaggregate countsは一致した。
この表はencoding accuracy、native confidence、独立母集団での品質比較ではない。
microとmacroが近くても、corpusの代表性や統計的独立性は証明できない。

## サイズ分布によって分かった不足

全16文書が[1024,4096) bytesに入り、他区間は0文書だった。
したがってこのcorpusだけでは、数十byteの短文や数十〜数百KiB文書への
適合を判断できない。空区間もreportに残し、未評価の範囲を隠さない。
同じ文書を切断したvariantを追加したわけではなく、全文の長さによる分類である。

French Tatoeba pilotでは複数文が同じoriginを持ち、既存の
`duplicate selected evaluation source hash/origin`検証で拒否された。
成功結果として数えず、重複防止を緩めたり文を結合したりしなかった。
集計対象の文書単位と、漏洩防止用のsource groupを分ける場合は別契約として検証する。

## 再現情報

- training artifact: `856a8ba06a4a6d8450ddb3f4afeafdf99223a2c715350ce6e381a8e271c80515`
- model contract: `007efecaae466c6f23066dc8088f6a63167de3f4c39e5624481bf38c575466f3`
- evaluation manifest: `6340aff3b3d424fced87b782d75036c64152b4840eec98a05dc9a5b4f90216aa`
- v2 report content hash: `4b2b75e83a72723edd2c344ede3dc536ae074609e96c0ff9f9c69308a6bdcaf0`
- evaluator依存source hash: `c222fa5971082021a731eb2dcb6a1e0a4ac011f3f86093c1f5845d853471898f`

`sequence-coverage-evaluation-v2`の仕様は
[native側の日本語文書](../src/ext/uchardet/models/experimental/SEQUENCE_EVALUATION.md)を参照。
旧reportを上書きせず、Git管理外の別fileへ保存した。
追加testsはmacro/microの違い、空分母、全サイズ境界、counts保存を検証し、
model関連46 testsが成功した。P01・独立holdout封印・生成modelの権利保留は維持する。

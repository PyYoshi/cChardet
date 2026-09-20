<!-- SPDX-License-Identifier: MIT -->
# 同じ文章の cp1252 / UTF-8 対照評価

2026-09-21。[uchardet #34](https://github.com/PyYoshi/uchardet/pull/34) の
[対照評価tool](../src/ext/uchardet/models/experimental/PAIRED_CONTROLS.ja.md)を使用。
前回の[既存モデル比較](v3-legacy-model-comparison.md)はcp1252の正例だけだったため、
同じUnicode本文をUTF-8にencodeしたvariantも単一proberへ渡した。
全detectorのUTF-8候補との競合、false-positive rate、正解率を測ったものではない。

## 固定条件

- legacy / identity / filteredの3モデル、同じnative library、whole-document filter
- 既存training artifactは不変。新規取得・学習・ratio/threshold調整なし
- 同じsourceのfull / complete / textのcp1252とUTF-8を対にし、strict decodeした本文一致を確認
- bytes同一の対は識別可能な負例に数えない
- UTF-8 bytesのcp1252でのstrict decode可否と、proberの途中終了を別々に記録
- 独立holdoutは未使用。legacy training overlapはUNKNOWN

## Paris Stories: 16対

全16対はbytesが異なる。UTF-8 bytesもstrict cp1252でdecode可能だが、元の文とは異なる
文字列になる。3モデルとも全対でcp1252版の内部confidenceがUTF-8版より高かった。
同値・逆転・非有限値・途中終了は0件。両encodingとも全16件がdetectingだった。

| model | cp1252内部confidence 最小〜最大 | UTF-8 bytesへの内部confidence 最小〜最大 |
| --- | ---: | ---: |
| legacy | 0.785962〜0.851188 | −0.249817〜0.086460 |
| identity | −0.006417〜0.678264 | −0.406838〜0.022351 |
| filtered | −0.236911〜0.532397 | −0.529099〜−0.159606 |

これは**同じ文書の2種類のbytesに対する単一proberの反応順序**であり、正解率100%ではない。
とくに生成モデルは、別文書同士で見ると正例・対照のscore範囲が重なる。
この表から汎用の閾値や実運用のfalse-positive rateは決められない。

## Rust book: 1対

validation専用manifestの同じsourceから、frameworkでcp1252/UTF-8両方の全文variantを生成した。
sourceのsplitはvalidationのまま。生成configは`encodings=["cp1252", "utf-8"]`、
`byte_limits=[None]`、`formats=["text"]`。元source本文を変更していない。

| model | cp1252 score / state | UTF-8 bytesへのscore / state |
| --- | --- | --- |
| legacy | 0.849141 / detecting | 0.029399 / rejected |
| identity | 0.704291 / detecting | −0.067459 / rejected |
| filtered | 0.535302 / detecting | −0.150758 / rejected |

UTF-8 bytesはcp1252としてstrict decodeできず、3モデルともfilter後5,138 bytesのうち
263 bytesで処理を止めていた。cp1252正例は4,456 bytesを全て消費した。
同じscore順序でも、Parisの全文を消費した対照と同じ統計的識別の証拠には数えない。
途中終了の有無とcodecのdecode可否だけで、任意入力の停止理由を自動診断するtoolではない。

## 再現と限界

native commit `d817c1d`、Python 3.14.2、GCC 16.2.1、C++11/O2。
libraryは[前回と同じ固定SHA](v3-legacy-model-comparison.md)。Paris manifestも同じ。
Rust paired corpus content hash: `44e44e689c22fbbeb83ab8b087434f054f6733b80dc20e2f71a11bc3dd37fa7b`。

```sh
uv run --no-project python models/experimental/paired_controls.py \
  /disk/filter-comparison-identity-fr-v1.json /disk/filtered-training-fr-v1.json \
  /disk/paris-stories-generated-1/manifest.json validation \
  /disk/native-build/src/libuchardet.a /disk/paris-paired-controls.json
```

両corpusともfresh buildから2回実行してreport全byteが一致した。

| report | content hash | file SHA-256 |
| --- | --- | --- |
| Paris | `c45d72ba703be344541f76ae36c1d37fd60dbf4f083867f42fa5e2165c9557e5` | `73d26a1b993b8fc2a1825d35daee12cf6f9e25bc1fdcb558b9958634a61bf011` |
| Rust book | `55ae25f1f8c161b601e6410a98df1d928189752f3ad34f6c7358348f08e32626` | `f31da3c07d09195ea4e7e74fdeda253f247ea3166a2e863cc9335fe0fd491c07` |

生のreport・モデルはGit管理外に保持する。結果はFrenchの2 corpusと2 encodingに限定され、
他言語・他codec・HTML・incremental処理・全detectorの候補順位・性能には一般化しない。
モデル採用とconfidence校正は保留し、P01の保留調査も再開していない。

[native CI](https://github.com/PyYoshi/uchardet/actions/runs/35539089353) 全11チェック成功。
モデル関連78テストはnative toolsありで全成功、なしでは69成功/9skip。
実harnessはLinux diagnosticsで実行した。追加8テストはローカルClangでも成功。
cChardetローカル統合は297 passed / 27 skipped / 76 subtests passed。

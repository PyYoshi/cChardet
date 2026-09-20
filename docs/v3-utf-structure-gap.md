<!-- SPDX-License-Identifier: MIT -->
# BOMなしUTF-16候補不在のsource確認

2026-09-21。既存の日本語UTF-16 LE/BE fixtureの保存観測とsourceを照合した。
新しいnative実行、入力探索、BOM試作の変更は行っていない。

## 観測と由来

観測revisionは `7993e0afe3b6c64f0ea3b43c7d4987118f6c5c12`。
今回のsource確認先は `a56fd9584d11e7a1f5cbcc75df9b5c3ec4837ab4`。
両revisionの `src/nsUniversalDetector.cpp` は同じGit blob
`06c2d9a2306afdb136d99e9020863c576d22c492`。
MBCS/SBCS groupとescape proberのcppにも、このrevision間の差分はない。

| fixture | bytes | 先頭4 bytes | 保存された先頭候補 |
| --- | ---: | --- | --- |
| ja/utf-16le.txt | 1416 | 55 00 54 00 | UTF-8 / hu / confidence bits 3ef86af4 |
| ja/utf-16be.txt | 1416 | 00 55 00 54 | UTF-8 / pl / confidence bits 3efd78c9 |

fixtureのSHA-256はLEが
`74e4dc7cb2cc04df9d1cdb3ee4ac33222f8e87a2a1d4605a60b6bdb6eb60a824`、BEが
`73df6f4ac1e8be28b71ba4fb37f689cbaa7e08f74cd8034120089122b1a3df01`。
現在の本文hashを保存観測と照合し、Pythonの指定codecによるstrict decodeも成功した。
ラベルはlegacy fixture path由来であり、独立した正解確認を追加したわけではない。
両者とも保存観測内に正解候補がなく、top-kを広げても得られない。

## sourceから分かる範囲

- [先頭判定](https://github.com/PyYoshi/uchardet/blob/a56fd9584d11e7a1f5cbcc75df9b5c3ec4837ab4/src/nsUniversalDetector.cpp#L118)
  では最初のfeedのBOMからUTF-16/UTF-32 shortcutを設定する。
- [MBCSの生成](https://github.com/PyYoshi/uchardet/blob/a56fd9584d11e7a1f5cbcc75df9b5c3ec4837ab4/src/nsMBCSGroupProber.cpp#L61)
  ではUTF-8、SJIS、EUC-JP、GB18030、EUC-KR、Big5、EUC-TW、Johabの8 proberを作る。
  BOMなしUTF-16/UTF-32用の構造proberは登録されていない。
- この固定sourceのUTF-16/UTF-32 encoding labelは先頭BOM shortcutにあり、
  後続のSBCS・escape経路がBOMなしUTF-16を候補として補う設計ではない。

したがって、この2件を単純なconfidence/ranking調整の対象とするのは不適切である。
**不足しているのはBOMなし入力からUTF-16候補を作る経路**であって、
「UTF-16全体が未対応」「日本語modelが未対応」とは言わない。
統計modelの追加と構造判定の追加も別の変更として扱う。

これはsourceに基づく手動診断。一般的な失敗分類toolは候補不在だけから同じ原因を
自動断定せず、既存の `cause_status: UNRESOLVED` を維持する。
他revision・別library・別入力にこの結論を一般化しない。

## 改善前に必要な評価

先頭BOMのchunk bufferingだけでは、BOM自体がないこの2件は解決しない。
構造判定を追加する場合は、通常ASCII/UTF-8、embedded NUL、短い入力、code unit境界、
surrogate、chunking、処理量制限との識別・互換性を別途評価する必要がある。
これらは将来の受け入れ条件であり、今回試験したと主張しない。

現在の2件の試作枠を無断で増やしたり、P01を再開したりしない。
新しい実装・採用は #125/#126 とD02/D03の判断範囲へ残す。

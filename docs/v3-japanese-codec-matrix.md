<!-- SPDX-License-Identifier: MIT -->
# 日本語validation本文のcodec・HTML・サイズ生成確認

2026-09-21。既存Rust book日本語pilotのvalidation章だけを使い、
corpus frameworkの多codec・stateful codec・HTML宣言・境界処理を確認した。
native検出、model学習、独立holdoutの読込・予測は行っていない。
新しいsource取得や今回の生成を成功させるための段落削除も行っていない。

## 同じ原典でも抽出profileは異なる

原典は固定revision `5092e5395bf32a65b277c3b1cc1a81ba288c7d46`の
[guessing game章](https://github.com/rust-lang-ja/book-ja/blob/5092e5395bf32a65b277c3b1cc1a81ba288c7d46/src/ch02-00-guessing-game-tutorial.md)。
MITを選択する権利根拠・保存noticeは[取得仕様](../src/ext/uchardet/corpus/sources/README.md)に従う。
下の2種類は以前のingest出力であり、今回追加で本文を加工したものではない。

| 抽出profile | 段落 | 除外済み段落 | UTF-8 bytes | 文字数 |
| --- | ---: | ---: | ---: | ---: |
| UTF-8 | 98 | 0 | 36,977 | 14,768 |
| CP932向け | 97 | 1 | 35,991 | 14,343 |

UTF-8版source SHA-256:
`491a616765f3dadca2d0aab938854ecee676fed09484af932c0dd7ae742c8337`。
CP932向けsource SHA-256:
`db1f9e439bd4ecd8e58bc81cacec77be0e6862cda21cc7bb2b9a7f858bf64780`。
同じoriginを維持し、どちらもvalidation。独立した2原典として数えない。

## 生成matrix

- codec: UTF-8、CP932、Shift_JIS、EUC-JP、ISO-2022-JP、UTF-16LE、UTF-16BE。
- 形式: text、html-clean、html-declared、html-mismatched。
- byte上限: unlimited、16、64、256、1024、4096。
- 境界: complete、truncated。

各profileで7×4×6×2=336組を試行した。
`failure_policy=record-and-continue`を使い、strict変換不能を明示的に記録する。
UTF-16LE/BEは明示endian codecでありBOMを追加しない。
completeは文字途中を切らず、stateful codecのfinalizationも上限内に収める。
truncatedはbyte上限で切るためstrict decode成功を保証せず、ground truthも区別する。

| profile | 成功 | skip | skipの内訳 |
| --- | ---: | ---: | --- |
| UTF-8 | 144 | 192 | CP932 / Shift_JIS / EUC-JP / ISO-2022-JPで各48組unencodable |
| CP932向け | 336 | 0 | なし |

短い上限のvariantも、frameworkの既定契約どおり全文のstrict変換可能性を先に確認する。
したがってprefixだけなら変換できた可能性があっても、全文が変換不能ならskipになる。
skipをdetectorの誤判定や未対応codec件数に読み替えない。

別directoryへ再生成し、manifest・本文・sampleを含む全fileがbyte一致した。
manifest content hash:

- UTF-8 profile: `147fbfbba61b8f662996d752964addb7d6ad1249ce31c0d10c13fe93d1ae80d3`
- CP932向けprofile: `824d7a882afc18cfabb14fd2fd5825edec3d1f7b8abff6be9f6b7be3ed42ed0d`

## 再現方法

生成器はuchardet `04f3bc4a927d116da12a8e161273239a804e21c5`の
`corpus/framework.py`（SHA-256:
`7095170260470955aa82319a8d3ce2e86cd142f1740d58a9cae684a96b7f73ed`）。
実行はuv / CPython 3.14.2。保存量は2回分合計約9.6 MiBで既存予算内。

既存取得recipeをingestした `ja-utf-8.json` / `ja-cp932.json`から、
metadataのsplitがvalidationであるsourceだけを選ぶ。各1件であることと上記hashを確認する。
source metadata・origin・本文は変更せず、上記4軸の設定でframework.generateを呼ぶ。
source rootは元ingest directory、出力先は未作成の別directoryとする。
2回分を生成し、manifestだけでなく全fileの相対path・bytesも比較する。
両manifestをmetadata-onlyのaudit-splitsへ渡すとsource_records=2、split_leakage=falseとなる。

この結果は1章の生成基盤確認に限る。HTMLは合成であり、Web収集本文ではない。
98段落版と97段落版には選択の偏りがあり、codec間の公平なaccuracy比較には混在させない。
生成variant数480を独立文書数と数えず、native精度・性能は未測定のまま保持する。

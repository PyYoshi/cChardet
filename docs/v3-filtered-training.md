<!-- SPDX-License-Identifier: MIT -->
# native filter を使用する別 training profile

2026-09-21。[uchardet #30](https://github.com/PyYoshi/uchardet/pull/30) の
`cp1252-native-filter-sequence-training-v1`。identity profile を上書きしない。
既存 filter を呼ぶ tool と新規 generator を接続し、filter 実装を Python へ移植しない。
仕様・実行例は[日本語ガイド](../src/ext/uchardet/models/experimental/FILTERED_TRAINING.ja.md)。

## 条件と再現結果

French Rust book の training source 1件だけを使用した。
元 manifest `2fcf2b73e697c0d07719dd5bc219fbd6947b51b9df27c767860c224dfb93bb68`
から `split == "training"` の source metadata を選び、framework の
`generate(config, original_manifest.parent, output)` で corpus を別出力へ生成した。
config は選択 source、`encodings=["cp1252"]`、`byte_limits=[None]`、`formats=["text"]`。
元 manifest の validation/independent source 本文は読んでいない。split の変更もない。

- source: `rust-book-fr-ch00-00-introduction-cp1252`
- source revision: `42bfcc8ccea02a1272e5fda936dd593b88361b80`
- source SHA-256: `d3c8f8c8a8cd2a921a9c73d8f04b707fee55a844e6bd6ec08574445dc7392af8`
- training-only corpus content hash: `e18bb288d48c7327bfc7699b8028b891885b6f4efae53355beae366eb3da7902`
- native tool: GCC 16.2.1 Release、native base `17f0cf4508e9c60f96c5ce9c02de69e4b1d118a6`
- binary SHA-256: `b69fedd1aca1c89d32e8e5b6387f3375920d828468afcd2c91917951ffd2c42a`
- generator commit: `dda46a5`、Python 3.14.2

同じ training-only manifest から両 profile を生成した。

| 学習統計 | identity | native-filter whole-document |
| --- | ---: | ---: |
| bytes | 11,946 | 1,944 |
| 観測された頻出文字数 | 54 | 34 |
| adjacent letter pair mass | 7,455 | 1,510 |
| positive category pair mass | 7,143 | 1,455 |

これは入力・生成統計の比較であり、精度の比較ではない。両方とも未校正。
文書全体の一回 filter に固定し、chunk分割の結果は混ぜない。

filtered profile を2回生成し、artifact全byteが一致した。
さらに `validate --manifest ... --binary ...` による再観測・再生成照合も成功した。

[native CI](https://github.com/PyYoshi/uchardet/actions/runs/35536634061) は全11チェック成功。
実native filter接続テストはLinux diagnosticsで実行し、macOS/Windowsでは純Python検証を
実行した。ローカルのcChardet統合テストは272 passed / 27 skipped / 70 subtests passed。

- filtered artifact content hash: `2ebcb763099f049c94afcbb65803c256fab373a02bcedd8af579d5d2fcb364a9`
- filtered artifact file SHA-256（両生成共通）: `90690917093ce3412e3b745b55e324f8de6afc1f5003bac99c98de425c4542bf`
- identity comparison artifact content hash: `561d76078a612829e92db031b39e9f3b6c4c0fbbb69774243e3b0553882b654e`

本文・統計・生成modelは `archives/v3-corpus/` にのみ保存し、Gitには追加しない。
公開しているのは集計と識別hashであり、生成modelの配布license決定ではない。

## 残る接続gate

filter後の隣接byte統計からテーブルを導出できるようになったが、実際のproberの
sequence counter、confidence、early terminationを再現したわけではない。
filter出力のbyte列/hashもtoolは返しておらず、同じ頻度からbyte順序一致は証明できない。
`NOT_ENGINE_CALIBRATED` / `UNDETERMINED` を維持する。
P01の保留作業は再開せず、標準model・公開API・既存engineを変更しない。

次は tuning/validation の同じfilter条件での観測と、prober側の分母・特殊orderの
扱いの照合を分けて進める。入力統計の改善だけで #123 や採用gate を完了扱いにしない。

<!-- SPDX-License-Identifier: MIT -->
# SBCS filter前後の入力統計

[uchardet #29](https://github.com/PyYoshi/uchardet/pull/29)の開発用診断を
native `17f0cf4508e9c60f96c5ce9c02de69e4b1d118a6`として統合する。
既存filterを呼び、元入力と各feedのfilter出力を連結した列のbyte/pair頻度を比較する。
filterの移植・変更、engine/model/public APIへの変更ではない。

## なぜ必要か

[training接続前調査](v3-sbcs-training-contract.md)で整理した入力差を観測するためのtool。
Python-only profileは元byteをそのまま数えるが、SBCS groupはfilter後のbyteを使う。
同じ文書でもchunk境界でfilterの出力が変わるため、profileのcountsとengineの
sequence counterが一致すると仮定してはいけない。

人工cp1252入力`plain café text`の小規模テストでは以下を確認した。

| 観測 | bytes | 隣接byte pair数 |
| --- | ---: | ---: |
| 元入力 | 15 | 14 |
| 全文filter後 | 5 | 4 |
| 1-byte chunkを個別filterして連結 | 1 | 0 |

一括出力は`café `、1-byte chunkでは`é`相当になる。これは既存filterの動作の
確認であり、望ましい動作の決定、chunk差分の修正、精度の評価ではない。
文書を跨ぐpairは作らず、同一文書内の空でないfeed出力の境界は跨いで数える。

## 再現と範囲

native側の[日本語仕様](../src/ext/uchardet/benchmark/filter-profile.ja.md)に
build/run/test commandとJSON契約を記載した。`BUILD_INTROSPECTION=ON`のstatic開発build限定、
既定OFF、install対象外。入力は最大65,536 bytesで、本文・pathは出力しない。
ただし頻度統計から入力を推測できる場合があり、匿名化済みとは扱わない。

GCC 16 ReleaseとClang 22（C++11、warning有効、同じGCC製engine libraryへlink）の
ローカルtool testsは各4件成功。native PR CI
[35535615643](https://github.com/PyYoshi/uchardet/actions/runs/35535615643)は全11件成功。
新toolの実行CIはLinux diagnosticsであり、他OSの通常matrixはこのopt-in toolをbuildしない。

## engineが変更されていないことの確認

engine/model sourceの差分はない。GCC Releaseの保存baselineと新buildで
archive内の全61 objectの内容・順序がbyte一致した。

- 旧archive: `6b9b78d7d7d206081ab278ec319b02a28fc2d557348f3edad253bbf8372effbb`
- 新archive: `cbfafc66f7aeb38952991b0fe3a621b6abf47aedf12bbc8eda3541908f28649a`

archive全体のhashは異なるが、63個のar headerの12-byte timestamp fieldだけを
メモリ上で空白へ置換すると全体が一致した。その比較用SHA-256は
`be33ee279884e98f5d639a176bbb895ec45248a0d28031ff3be85cdcef29c5a1`。
元artifactは書き換えていない。これは特定buildの比較であり、全toolchain・性能・
新しい候補出力の実測証明ではない。

## 未完了のgate

このtoolはproberのactive状態、文字order、matrix分類、early completionを実行しない。
実detectorが全入力を同じchildへ渡すとは限らず、生byte pairはmodelのsequence分母でもない。
filter互換training、confidence較正、独立dataでの識別品質は未完了のまま。
既定profileの`identity-unfiltered-v1` / `NOT_ENGINE_CALIBRATED`を維持する。
P01対象の追加fuzz・大入力停止原因調査・BOM試作評価は再開していない。

後続の[会話validation観測](v3-filter-validation.md)では、既存16文書に対する
filter前後とchunk別の統計差を記録した。trainingや精度評価とは分けて扱う。

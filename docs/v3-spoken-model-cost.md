<!-- SPDX-License-Identifier: MIT -->
# 会話trainingモデルの限定的な処理コスト

2026-09-21。[固定generator比較](v3-spoken-model-comparison.md)で作ったParis-only
identity/filteredモデルを、同じnative libraryのlegacy Frenchモデルと比較した。
候補を競合させる全detectorではなく、単一proberのwarm reuseを対象とする。

## 条件

[前回の計時](v3-native-model-timing.md)と同じParis validation full cp1252 16文書、
raw合計40,777 bytes、CPU2、20,000反復×7試行×3 run。
reset/filter/feed/confidence/checksumをnative区間内で測り、I/O・確保・build・Pythonを除く。
128 warm-upを置き、モデルの実行順を文書・試行ごとに循環する。
全試行の最終観測/checksumは非計測時と一致した。

hostはAMD Ryzen 7 8845HS、Linux `7.2.4-202.nobara.fc44.x86_64`、
GCC 16.2.1、wrapper C++11/O2。governorは全runの前後ともpowersave。
こちらから同時に別のbuild/testは走らせていないが、CPU占有・周波数・background負荷・
SMT相方は制御していない。過去runとの絶対値差をモデルによる変化と断定しない。
各run内のlegacyを比較基準とする。

## 時間

値は独立した文書別warm trial時間の合計を反復数で割ったmedian（µs）。
16文書を交互に処理したcorpus passの実測値ではない。

| run | legacy | identity | filtered |
| --- | ---: | ---: | ---: |
| 1 | 50.704 | 51.140 | 51.601 |
| 2 | 51.387 | 51.213 | 51.454 |
| 3 | 51.550 | 51.209 | 51.868 |

全3 run・全16文書で文書別medianのlegacy比5%超悪化はなかった。
ただし試行平均p95の10%超悪化はrun3に2件あり、そのまま残す。
7試行のnearest-rank p95は最大試行であり、個々のリクエストのp95ではない。

| source ID末尾までのhash | モデル | p95悪化 | 該当最大試行時間 / legacy最大 |
| --- | --- | ---: | ---: |
| `485411558ce4ace208c63bad29a00f16ad06b158701da4f53ee86da243a6acfc` | identity | +10.57% | 60.951 / 55.127 ms |
| `a3fae83e5d322ae488bcebe382eda7c30cd857380766bd9b9716ed6b7d491221` | filtered | +30.71% | 79.265 / 60.642 ms |

source IDは上記hashに`paris-fr-`を付けたもの。各試行は20,000反復。
run1/2では10%超悪化は出ていない。最初のsourceは旧学習モデルの前回計時でも
identity側の変動を記録しており、今回のtraining変更固有とは断定できない。
CPU時間・context switch・周波数を区間内で観測していないため、OS scheduling等を
原因として確定することもできない。追加観測が必要な差分として保持する。

## Allocation call-site

時間計測とは別に[allocation tool](v3-model-allocation-calls.md)で48観測を実行した。
128 warm-up後1回のreuseで対象8種のcounterは全て0、通常版とのsnapshot/reset差分も0。
静的リンクで捕捉できる呼び出しだけの結果であり、shared-library内部・初回確保・
peak/live memory・全detectorのallocationは未測定。

## 再現・識別hash

前回の計時/計測commandのtraining artifactを次の2fileへ置き換える。

- `paris-identity-training-v1.json`: content hash `73cc98234e5532d7e8b05c4bd7f8bf802727325dadf41babb865adb143bc2b84`
- `paris-filtered-training-v1.json`: content hash `8f80555a7a7f1fbd4ad368aaf95158428af7ad3fd750b4ed1f85e4e84b2997fd`

tool revision: native `613245051da2e208489e5056c967af6b01c8f528`。
library SHA-256: `cbfafc66f7aeb38952991b0fe3a621b6abf47aedf12bbc8eda3541908f28649a`。
生reportはGit管理外に保持する。

| report | content hash | file SHA-256 |
| --- | --- | --- |
| timing run1 | `a2c381cf742e95010b00e84794612d7880e834a69f3677bbee6a7bab4a8c2088` | `e7ec777a476b23fe5ccece0edf394b69f96e89aeb22f88e4654c46fb0dd10607` |
| timing run2 | `0fece33f210cebf28dcc67652e885b6312819c4a254238eb85ea565ee897c168` | `d51f7ed454e24bc05bfe41edd13dccaf4e0620e395f902014a379b5ba1ba8998` |
| timing run3 | `fa5805af71a35272c3da2be620b5956f8c61260afb14840ed74587ed3213d7c9` | `ac8fc99a7257435e7b106b11ed58d72da8031a2c4995cb483f15d99f55939687` |
| allocation | `789c43254dca41252b2f2c45b615b99dd99a6c32a2b28c04c7fc6327707c23ad` | `98007ea0f7a690495fb2007a769de8961c8a3821a5c42eb0acb50e99e001e523` |

限定medianだけで性能gate全体を通過したとは扱わない。trial末尾側の変動原因、
request tail latency、全detectorのmemory/throughput、識別精度と配布条件は残る。
この結果を理由に既定modelを置換せず、P01の保留も維持する。

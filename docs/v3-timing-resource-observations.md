<!-- SPDX-License-Identifier: MIT -->
# 試行時間の変動とCPU/resource観測

2026-09-21。[前回の未解決な試行変動](v3-spoken-model-cost.md)を切り分けるため、
[uchardet #38](https://github.com/PyYoshi/uchardet/pull/38)でnative計測toolを拡張した。
engine・model・公開APIは変えていない。過去の計測値を補完・上書きするものでもない。

## 計測範囲

Linuxの単一thread診断processで、wall区間の直前・直後に`getrusage(RUSAGE_SELF)`を呼ぶ。
user/system CPU時間、voluntary/involuntary context switch、minor/major page faultの
差分を各試行へ保存する。CPU時間はmicrosecond精度をns表記へ換算した値である。
resourceの区間はclock読取り等も含むため、wall区間とは厳密には異なる。
APIの範囲は[Linux man-pages](https://man7.org/linux/man-pages/man2/getrusage.2.html)に従う。

reportは`native-model-timing-v2`。`elapsed_ns`と`trial_resources`は同じ試行順・件数で保存し、
非計測時のsnapshot/checksumとの一致も維持する。Linuxの取得失敗やcounter不正は失敗として扱う。
non-Linuxの低レベルprobeは未観測をnullとする。0回・0時間と偽らない。

## 固定条件と結果

Paris-onlyのidentity/filteredモデル、legacy French、Paris validation 16文書を使用した。
CPU2、20,000反復×7試行×3 run、128 warm-up、モデル順序の循環は前回と同じ。
計測中はこちらから他のbuild/testを走らせていない。hostのCPU占有・周波数は固定していない。
全1,008試行で最終観測/checksumが一致し、resource列と時間列の件数・順序を確認した。

値は文書別warm trial合計のmedian（µs）。交互corpus passやリクエスト単位の値ではない。

| run | legacy | identity | filtered |
| --- | ---: | ---: | ---: |
| 1 | 49.537 | 49.412 | 49.904 |
| 2 | 49.586 | 49.365 | 49.804 |
| 3 | 49.542 | 49.406 | 49.840 |

文書別medianのlegacy比5%超悪化はなかった。試行平均p95の10%超悪化は次の2件。
7試行のnearest-rank p95は最大試行に相当する。原因の説明にならないため、試行を除外しない。

| run / model | source hash（`paris-fr-`を前置） | p95悪化 | 該当試行wall / CPU合計 | involuntary switch / minor fault |
| --- | --- | ---: | ---: | ---: |
| 1 / filtered | `e1234e35957df30782bc719015971a32835cf7c55c018da45be678e190768a85` | +19.19% | 101.026 / 100.714 ms | 1 / 2 |
| 2 / identity | `fdaa76afb56bbf118d36b729d1e91489ab3f87f41e90f8b02d46624d4431d76d` | +20.40% | 100.856 / 100.465 ms | 2 / 1 |

両試行のvoluntary switch・major faultは0。前者の他6試行のCPU合計は約84.1〜84.2 ms、
後者は約79.5〜79.6 msで、遅い試行ではCPU時間も増加していた。
この観測は単純なwall-onlyの待ち時間では説明しにくいが、modelが原因との証明でもない。
周波数・cache miss・SMT競合等を観測していないため、原因は未確定のまま。
context switch数だけから停止時間を計算することはできない。

## 再現・検証

[前回と同じcommand](v3-spoken-model-cost.md)をnative `014f8f69b1a92e9efe5f0147a630bec2fd6b7546`
のtoolで実行した。model/input/libraryは不変で、GCC 16.2.1、wrapper C++11/O2、Python 3.14.2。
関連87 testsとClangによるsequence probe 10 testsが成功した。
native PR #38は全11 CI成功後、devの`10ee109390bddf0255acf16a67d1fe8c004cae6a`
へ統合済み。cChardet参照更新後のローカル検証は315 passed、27 skipped、
79 subtests passed（native library/filter tool指定）。skipは検証済みとは扱わない。

| report | content hash | file SHA-256 |
| --- | --- | --- |
| run1 | `4816f46a111a7fe9c6bcedf2994ea5f2c8a14a48143c71f6ff8b511b0349061f` | `79da7e0821654e257e10c55cf736dac0a9bd174fe1304d4824b5c1b54a2d744e` |
| run2 | `284196be5a0b47ad06b773ba38b00d173f8cf59574c5eeece7e636d5feec7862` | `1d4be356200378027961807c07f9bd6a0855358f79c64f32087531f641e1d179` |
| run3 | `65960f5efb4c2223648cf70ec9d8ea1e58e9e8838d12f4b28b632ff57b44ee83` | `30fc90135d7bf7d25278f5f6760695b698f26ee33c4d1b7beb4b34f4e2fe8912` |

生reportはGit管理外に保持する。これを性能gate全体の完了とは扱わず、
全detectorの性能・request tail latency・memory・品質と配布条件の確認は残る。P01も維持する。

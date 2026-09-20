<!-- SPDX-License-Identifier: MIT -->
# trace build optionの無効時影響：限定測定

2026-09-21。native `063ad3e9a62c90db482550e278a8682b98d0198a`で
`BUILD_INTROSPECTION=ON`からOFFへ切り替え、同じbuild directory、GCC16.2.1、
Release/static設定で再buildした。小fixtureだけを使用し、P01の大入力検証は再開していない。

## 生成物の一致

切り替え前後で静的library全体とnative benchmark実行ファイルがbyte一致した。

| 生成物 | 両設定のSHA-256 |
| --- | --- |
| libuchardet.a | `6b9b78d7d7d206081ab278ec319b02a28fc2d557348f3edad253bbf8372effbb` |
| uchardet-benchmark | `4c8a52308a73091006cc442dff926daba00354b4cdd095728e8d1621419390b8` |

optionは別の診断実行ファイルを追加するだけで、engineへ実行時flagやcallbackを注入しない。
OFFへの切り替え時にengineの再compileも発生しなかった。
これは同一build内のON/OFF比較であり、過去の別revisionのarchive比較とは区別する。
古いtrace実行ファイルはbuild directoryに残り得るが、OFFのbuild targetには含まれない。

## native C APIでの測定

空・11-byte ASCII・135-byte日本語UTF-8の既存3fixtureを一巡する時間。
input hashは[候補照合の固定入力](v3-report-attribution.md)と同じ。
I/OとPython処理を計測外とする既存`uchardet-benchmark`を使い、CPU affinityは0へ固定した。
各process内3回warm-up後、1001回を測定。ON→OFF／OFF→ONを交互に10組実行した。
fresh/reuse × whole/7-byteの4条件、各設定・条件に10,010 samples。
checksumは全processで153612だった。checksumを全候補の完全一致検証の代用にはしない。

| mode | chunk | ON median (ms) | OFF median (ms) | ON p95 (ms) | OFF p95 (ms) |
| --- | ---: | ---: | ---: | ---: | ---: |
| fresh | whole | 0.0465665 | 0.0453945 | 0.085760 | 0.074549 |
| fresh | 7 | 0.050424 | 0.050604 | 0.054231 | 0.054541 |
| reuse | whole | 0.039844 | 0.039894 | 0.041567 | 0.041267 |
| reuse | 7 | 0.050975 | 0.051105 | 0.055103 | 0.055132 |

medianは各processの中央値の平均ではなく全sampleを合算した中央値。
p95は昇順sampleのnearest-rankで計算した。native出力の小数精度を超える精度は主張しない。

**両実行ファイルが同一なので、表の差を機能の高速化・低速化と解釈しない。**
とくに最初のfresh/wholeではprocess medianがON 0.072906→0.039122 ms、
OFF 0.074178→0.039223 msへ低下した。3回の短いwarm-upだけでは実行環境の
時間変動を取り除けなかった。CPU周波数が原因と実測確定したわけでもない。
この条件のp95差を機能由来のregression判定に使用しない。
後半3条件のmedian差は約0.13〜0.36%だが、一般的な性能保証や誤差上限ではない。

再現する場合はON buildのbenchmarkとlibraryを保存し、同じdirectoryで
`cmake -DBUILD_INTROSPECTION=OFF`と再buildを実行してhashを先に比較する。
各実行は `taskset -c <CPU> uchardet-benchmark fresh 1001 0 <空> <ASCII> <日本語>`。
modeとchunkを上表に合わせ、10組で実行順を交互にする。入力読込をnative計測内へ移さない。

## 結論と未完了範囲

当該buildのengine／benchmarkにはON/OFFで実行コードの差がない。
診断toolを実際に起動した際のJSON生成・allocationコストは別であり、ここでは測っていない。
他compiler、配布wheel、大入力、一般的な並列性能を検証したとは扱わない。
#120の観測基盤を支える限定的証拠として記録し、reject/ranking原因の網羅まで完了とはしない。

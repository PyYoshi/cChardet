<!-- SPDX-License-Identifier: MIT -->
# 生成モデルと native prober のカウンタ照合

2026-09-21。[uchardet #32](https://github.com/PyYoshi/uchardet/pull/32) の
非デフォルトharnessで、生成モデルを初めて実際の single-byte prober に渡した。
既存engineやmodel登録は変更していない。[操作仕様](../src/ext/uchardet/models/experimental/SEQUENCE_PROBE.ja.md)。

## 観測条件

[前回の同一filter比較](v3-filtered-evaluation.md)と同じ2つの固定training artifactと
Paris Stories validation 16録音を使用した。corpus/modelは再生成・再学習していない。
manifestの全sourceがvalidationであることをmetadataで確認してから、frameworkで本文を検証し、
full / complete / text / cp1252だけを選択した。独立holdoutは使用しない。

1. 各モデルのcontractをvalidator/emitterへ渡してprivate headerを生成する。
2. 既存static libraryと新規harnessをリンクする。モデルごとに別binaryを作る。
3. 一文書ごとに新しいprocess/proberを起動し、全文を一回filterして一回feedする。
4. 保存したnative counterを、同じ文書のfilter統計から計算した期待値と照合する。
5. 各観測を2回実行して一致を確認する。全体もfresh buildから再実行して同一reportになった。

全32組（16文書 × 2モデル）で次の整数値が一致した。

- `total_characters = filtered bytes`
- `frequent_characters = frequent_letters`
- `out_characters = known_rare_letters + unknown_letters`
- `control_characters = byte_to_order が254のsymbol質量`
- `total_sequences = adjacent_letter_pairs`
- `categories[0] = matrix category 0 の質量 + outside_matrix_pairs`
- `categories[1..3] = 各matrix categoryの質量`

これは今回の生成profileと有効なcp1252文書での照合結果。
任意の契約、illegal byteで途中終了する入力、reversed prober、incremental入力一般についての
同値証明ではない。confidence式をPythonで再実装して一致させた結果でもない。

## 内部confidenceと状態

| model | 文書数 | detecting / found / rejected | 内部confidence最小〜最大 |
| --- | ---: | --- | --- |
| identity | 16 | 16 / 0 / 0 | −0.006417〜0.678264 |
| filtered | 16 | 16 / 0 / 0 | −0.236911〜0.532397 |

confidenceはbinary32 bitで保存し、表だけを丸めて表示した。
この内部値は確率ではなく、公開APIの最終候補confidenceでもない。
全件detectingであることは「判定不能と確定した」「誤判定した」のどちらも意味しない。
全detectorの候補競合を行っていないため、encoding accuracyには換算しない。

人工modelではnegative confidenceと1超の値、1024 sequenceを**超えた**場合のshortcut、
低頻度letterのnegative加算、空filter、resetをGCC/Clangで検証した。
今回の未校正modelを標準登録する根拠にはならない。

## 再現情報

- harness commit: `f69e46c`、Python 3.14.2
- compiler: GCC 16.2.1、`-std=c++11 -O2 -Wall -Wextra -Wpedantic`
- static library: 既存native `17f0cf4` からのGCC Release build、後続でengine source変更なし
- static library SHA-256: `cbfafc66f7aeb38952991b0fe3a621b6abf47aedf12bbc8eda3541908f28649a`
- corpus content hash: `6340aff3b3d424fced87b782d75036c64152b4840eec98a05dc9a5b4f90216aa`
- report content hash: `458269d70d0ba13cf7f0832e242285e027cfe4f42d563e8b3b224bb6e1dfd095`
- report file SHA-256: `d419fba1689c415870925facbe83b1715f3a66e8be6a27ba2c56932caa1e69c3`
- local実験script SHA-256: `71273472c72e5259a263074985b74c256591ed8cccf08ede0826e43398a12e64`

CLIで一文書を再実行する場合、training artifactの`contract`を別JSONへ抽出し、
上記native仕様のcommandに、その文書のmanifest sample pathを指定する。
複数文書のカウンタ照合は`sequence_probe.build()` / `observe()`と
`filtered_training.observe()` / `check_observation()`、
`filtered_evaluation.counts()`を使い、上の対応式で比較できる。
raw input、native model、compiler等のhashをreportから追跡できる。

reportは `archives/v3-corpus/paris-sequence-probe-v1.json` にのみ保持する。
header/binaryは一時directoryの終了時に破棄し、repositoryやwheelへ同梱しない。
生成モデルの配布licenseは未確定のまま。

[native CI](https://github.com/PyYoshi/uchardet/actions/runs/35537798560) 全11チェック成功。
実harnessはLinux diagnosticsで実行した。ローカルではGCC/Clangの各6テスト成功、
モデル関連66テスト成功、cChardet統合285 passed / 27 skipped / 76 subtests passed。
macOS/Windows CIではこのnative harnessの実行までは確認していない。

## 次のgate

入力・整数counter接続の限定的な確認から、confidence校正や実際の候補競合・識別品質へ
進む必要がある。内部confidenceの上下を品質の優劣に置き換えない。
P01の安全性調査・fuzz・大きなUTF-8入力の停止調査は再開していない。

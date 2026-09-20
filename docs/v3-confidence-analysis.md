<!-- SPDX-License-Identifier: MIT -->
# 保存済み観測による confidence 診断

2026-09-21。`benchmarks.confidence_analysis` は新しい detector 実行を行わず、
保存済み legacy 観測と実際の corpus byte / SHA / label / 順序を照合して分析する。
既存の exact / compatible / decode-equivalent 判定を再利用する。

```sh
uv run --locked python -m benchmarks.confidence_analysis \
  --observations /disk/saved-legacy-observations.json \
  --uchardet-corpus src/ext/uchardet/test \
  --output /disk/legacy-confidence.json
```

各候補の有限な binary32 confidence bits を検証する。表示用の丸められた数値ではなく
bits から復元した値を使い、候補順序は保存されたまま維持する。
先頭候補のscoreを全体・encoding family・言語・入力サイズ別に集計する。

- bucket は下端以上・上端未満。0未満・1以上も独立bucketに残す。
- scoreを `[0,1]` へ丸めず、範囲外の件数を明示する。
- 候補なしはunscored。閾値を満たす件数の分母には元の全件を使う。
- decode-equivalentは判定可能件数を別に保持する。判定不能を誤判定として数えない。
- 閾値は固定の `0, .25, .5, .75, .9, .95, .99, 1`。結果から最適化しない。
- outputが同じなら再書込みせず、異なる既存reportの上書きは拒否する。

## 既存158 fixtureの結果

native `7993e0afe3b6c64f0ea3b43c7d4987118f6c5c12` の保存観測を使用。
今回のnative devを新規測定した結果ではない。全158件に先頭候補があり、
scoreは約0.485〜1.0、範囲外0件だった。

| 閾値以上 | 残る件数 / 元件数 | exact / 残る件数 | decode-equivalent / 判定可能件数 |
| --- | ---: | ---: | ---: |
| 0 | 158 / 158 | 153 / 158 | 147 / 149 |
| 0.5 | 156 / 158 | 153 / 156 | 147 / 147 |
| 0.75 | 144 / 158 | 141 / 144 | 136 / 136 |
| 0.9 | 42 / 158 | 42 / 42 | 42 / 42 |
| 0.95 | 38 / 158 | 38 / 38 | 38 / 38 |
| 0.99 | 10 / 158 | 10 / 10 | 10 / 10 |
| 1.0 | 2 / 158 | 2 / 2 | 2 / 2 |

score約0.485/0.495の2例は既知のBOMなし日本語UTF-16 LE/BEで、正解候補不在。
codec名が非exactの残る3例はscore約0.799〜0.858だが、いずれもdecode-equivalent。
その3例まで一律に「高confidence誤判定」と呼ばない。

0.9以上が全件exactでも、116件を除外している。これを全体精度100%や
推奨閾値0.9と読み替えない。このcorpusのscoreと正解率の関係を観測しただけであり、
実Webや独立corpusでの校正を立証しない。confidenceは正解確率と仮定しない。

[集計JSON](benchmarks/v3-confidence-2026-09-21.json)にreport hashと分母を保存した。
完全reportには入力reportのhash、native revision、評価library version、分析tool依存hash、
sampleごとのbitsと根拠を含む。既定API・confidence値・閾値は変更していない。

<!-- SPDX-License-Identifier: MIT -->
# encoding family集計のv2

2026-09-21。`benchmarks.encoding_families` を `codec-family-v2` とした。
detectorの対応・精度改善ではなく、集計漏れの修正である。過去のv1結果は上書きしない。

## 明示分類の追加

| encoding | reporting family | v1のunknown件数 |
| --- | --- | ---: |
| IBM852 / MAC-CENTRALEUROPE | latin-central-european | 11 |
| ISO-8859-4 / ISO-8859-10 / IBM865 | latin-northern | 7 |
| ISO-8859-16 | latin-southeastern | 4 |
| ISO-8859-3 | latin-southern | 3 |
| IBM855 | cyrillic | 2 |
| IBM862 | hebrew | 2 |
| CP737 | greek | 1 |
| GEORGIAN-ACADEMY / GEORGIAN-PS | georgian | 2 |
| VISCII | vietnamese | 1 |
| EUC-TW | chinese-traditional | 1 |

根拠は[Python codec一覧](https://docs.python.org/3.14/library/codecs.html)、
[GNU libiconv](https://www.gnu.org/software/libiconv/)、
[EUC-TWのGNU CLISP説明](https://www.gnu.org/s/clisp/impnotes/encoding.html)。
地域別bucket名は本分析の方針であり、正式規格の分類や対応言語の排他性ではない。
同familyだからdecode互換・superset・同じ誤判定原因とは扱わない。

Python未登録のnative名は、family照合だけでcaseとhyphen/underscoreを吸収する。
明示した5名称だけを認め、prefix推測やdecoder登録は行わない。
`canonical_encoding` とexact/compatible/decode-equivalent判定は変更していない。
GEORGIAN-PSはfamilyが分かっても、Pythonでdecode検証できたことにはならない。

## 保存観測による確認

native `7993e0afe3b6c64f0ea3b43c7d4987118f6c5c12` の保存観測を158 fixtureの
本文hash・label・順序と照合して再分析した。native再実行や独立holdout予測はない。

```sh
uv run --locked python -m benchmarks.failure_analysis \
  --observations /disk/saved-legacy-observations.json \
  --uchardet-corpus src/ext/uchardet/test
```

- 入力観測SHA-256: `04bf1e26feb43270233d25dd106670e164f17ed81df918f66d5abe8d7a2b59b0`
- v1再分析report SHA-256: `ba0ab69a623290ab9bbf0700749b8076b2e046b50cb0a2fb653a9b0202a7b095`
- v2 stdout report SHA-256: `11ffd1fa1dc172bc1a5bc31e14487891a1e18a359de11b536aa42c1f07526983`
- expected family未分類: 34件 → 0件。
- sampleの4分類field（encoding_family / expected_family / predicted_family / family_relation）
  以外はv1再分析と全件一致。候補順・confidence・各精度判定は不変。
- cause未確定11件、Python decoder不足9件は維持。

これはlegacy corpus内の分類coverageであり、外部精度や実Web頻度の証明ではない。
未登録encodingは引き続きunknownとし、新規encodingの採用順位は未確定。

## pytest探索範囲

既定rootを `tests` と `src/ext/uchardet` に明示した。
nativeのcorpus/model/benchmark testsは残し、Git管理外の `archives` に保存した
検証用Pythonの標準ライブラリtestを誤収集しない。
初回の引数なしpytestはこの誤収集で収集段階に失敗し、成功件数には含めない。
回帰testで両rootの収集とarchives除外を確認した。

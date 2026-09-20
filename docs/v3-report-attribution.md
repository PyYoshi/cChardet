<!-- SPDX-License-Identifier: MIT -->
# raw Reportと最終候補の対応照合

`benchmarks.report_attribution` は保存済みtrace JSONLと、1入力分の
`uchardet-conformance` JSONを照合するPython-only tool。native実行やrankingの再実装はしない。

```sh
uv run --locked python -m benchmarks.report_attribution \
  --trace /disk/trace.jsonl --final /disk/final.json
```

完全なinitial〜after_end snapshot、入力長、feed回数、開始・終了done、候補数と
有限binary32 confidence bitsを確認する。最終候補の順序をそのままrankとして保持する。
各候補についてencoding名・language（nullを含む）・confidence bitsが完全一致する
raw Reportのevent indexを列挙し、同labelだがscoreが違うeventも別に示す。
indexはJSONL全eventの0始まりであり、raw Reportだけの番号ではない。

- codec aliasやdecode互換性ではなく、観測値の完全一致を扱う。
- 同値のraw eventが複数あれば全indexを残し、採用元を一つに決めつけない。
- `unmatched_raw_event_indices` は最終候補のどの値とも完全一致しなかったevent。
  「棄却された理由」や「unusedだったevent」の証明ではない。
- 異なるscoreを見ても、weight適用や較正が原因だったと推測しない。
- input本文・新しいconfidence計算・deduplication/tie-breakingの再実装は含まない。

出力にはtrace/final artifactと分析toolのSHA-256を含める。
**このhashはファイルの同一性を追跡するもので、同じ入力・build・chunkから
生成されたことを認証するものではない。** 長さとfeed回数の一致だけでも証明できない。
収集時のinput hash、native revision、tool hash、同じfeed scheduleを別途固定する必要がある。
ranking_reasonは一致した場合も `UNRESOLVED` のままにする。

## 限定した実行確認（2026-09-21）

19件の単体testに加え、既存の空・ASCII・135-byte日本語fixtureを
whole / 1-byte / 7-byteでfeedする9通りを実際のtrace/conformanceで照合した。
同じtemporary inputを両toolへ渡し、全最終候補について同値raw Reportが存在した。
これはencoding accuracyや順位原因の証明ではない。

```sh
UCHARDET_TRACE=/path/to/uchardet-trace \
UCHARDET_CONFORMANCE=/path/to/uchardet-conformance \
  uv run --locked pytest tests/test_report_attribution.py -q
```

この実行は28 tests成功。環境変数なしではnative比較9件がskipとなる。
native toolはlanguage観測追加commit `a9b7405701d96c04dfca4432817190078c86208e` の
GCC16.2.1 / Release / static buildを使用した。merge先は `a56fd9584d11e7a1f5cbcc75df9b5c3ec4837ab4`。

使用toolのSHA-256:

- trace: `90a3b320fd189674a5d8883d12a92ca986344432a8c655191954299f5138a2ea`
- conformance: `2944d943c50af9a76222617e9591bb6294526b5e18d6390b978501187d67501e`

固定した入力（UTF-8。検証toolが作るtemporary fileで両実行に共用）:

| 内容 | bytes | SHA-256 |
| --- | ---: | --- |
| 空 | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `plain text` + LF | 11 | `c30a92f9ef889c07c781a7cf99f5b71415d4d1289e84473d1b9e6f01feffc62d` |
| `日本語の文章です。` を5回 | 135 | `85a90cf384c10ea7cb1bd217352fad10c14393daaf7aaccd9227b2344aef2c2f` |

新規fuzz、不正入力探索、大入力、独立holdout評価、既定model/API変更は行っていない。

## prober内部観測追加後の再確認

native `063ad3e9a62c90db482550e278a8682b98d0198a`
（merge `e3c8526ab0effa6960dff173be991a18e732782d`）でも同じ28 testsが成功した。
追加のsnapshot fieldがあっても、保存済みraw値と最終候補の照合結果は変わらない。
同じGCC16.2.1 / Release / static buildのtool SHA-256:

- trace: `018734eb85809cbeb8ff9946d4ea25196d48d8bfd94f2836f0ef75463e0bb9ce`
- conformance: `2944d943c50af9a76222617e9591bb6294526b5e18d6390b978501187d67501e`

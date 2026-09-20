<!-- SPDX-License-Identifier: MIT -->
# V3: manifestに基づくcorpus分析

`benchmarks.manifest_analysis`は生成corpusの内訳と評価対象の選択を記録する。
既定は棚卸しのみで、detectorは起動しない。リポジトリrootで実行する。

```sh
uv run python -m benchmarks.manifest_analysis \
  --manifest /path/to/corpus/manifest.json --max-input-bytes 1024
```

複数corpusは`--manifest`を繰り返す。schema・hash・実byteと再生成結果を検証し、
manifestをまたぐorigin/hashのsplit漏洩と重複manifestを拒否する。
この検証はholdoutを含むファイルを読み、再encodingするが、予測や精度評価はしない。
本文を読まないsplit監査だけが必要なら、uchardetの`corpus/framework.py audit-splits`を使う。

既定splitは`validation`、boundaryは`complete`のみ。
件数はcorpus・split・言語・encoding・サイズ・形式別に出し、
対象外のsampleも除外理由付きで残す。予測結果を使って対象を選ぶ機能はない。
生成前にskipしたvariantはmanifestの`generation_report.counts`を別途掲載する。
旧manifestで記録がなければ`null`であり、skipゼロを意味しない。

## 評価の明示的な有効化

native conformance toolを使用する評価には`--native-tool`、
`--native-revision`、`--max-input-bytes`の3指定が必要。
`--split independent`の評価はさらに`--allow-independent-evaluation`が必要。
実行直前にも入力hashを確認し、実行失敗や不正な出力は評価全体をエラーにする。
失敗を誤判定やskipに変換して集計しない。

encodingのexact / compatible / decode-equivalent、language、両者の一致、
top-1/3/5を分ける。decode-equivalentは評価可能件数を別途出す。
判定基準は既存の`failure_analysis`を共有し、利用したchardetのversionを記録する。
candidate不在からmodel不在を断定することはできない。

入力上限は評価対象を選ぶ条件であり、長いsampleをその場で切断しない。
上限内であることはnative実装の安全性を証明しない。
[P01](v3-decision-log.md)の大入力native評価は保留のままとし、
今回のpilot集計は棚卸しのみ。独立holdoutの予測結果は取得しない。

### 2026-09-20のpilot棚卸し

Rust book翻訳由来の既存6manifest（仏・日・露、UTF-8と各legacy codec）を検証した。
全96sampleのうち、validationかつ1 KiB以下のcomplete variantは12件。
split対象外が72件、validationのサイズ対象外が12件。native評価は0件。
independent holdout 24件はすべて評価対象外であり、精度値は取得・公開していない。
この旧manifestには生成attemptの記録がないため、生成前skip件数は不明として扱う。

## 集計の限界

- 生成元のstrict再encodingはbyteの由来を説明するが、一意に推定できるcodecとは限らない。
- 同一書籍の翻訳・章分割は、独立著者や独立domainのcorpusではない。
- 選んだ小入力の成績を、対象外のサイズやsplitへ一般化しない。
- reportはcorpus本文を含まないが、manifest由来のpath・origin・hashを含む。公開前に確認する。
- metadataやsampleの改変を検出するための検証であり、未信頼corpusを実行するsandboxではない。

# コーパス重複監査と固定モデルの validation 診断

2026-09-20、Python-only の offline 診断を追加した。
native 検出・独立 holdout 予測・モデル再学習・既定モデル変更は行っていない。
実装は [uchardet #20](https://github.com/PyYoshi/uchardet/pull/20)。
native dev `2dffb2c330b9418e778938471e693b78223f2147` に統合済みで全11 CIが成功した。
cChardet 統合時のローカル検証は176 passed / 10 skipped、ruff / mypy 成功。

## source 本文の重複監査

[仕様](../src/ext/uchardet/corpus/OVERLAP.md)の正規化一致と文字 5-gram Jaccard
類似度で、metadata の SHA / origin 検査を補完する。診断用正規化は元本文に反映しない。
既定閾値 4/5 を変更せず、保存済み Tatoeba CC0 pilot の仏語・露語各200文を比較した。

| 項目 | 結果 |
| --- | ---: |
| source 数 | 400 |
| source UTF-8 bytes | 30,409 |
| 比較ペア数 | 79,800 |
| 非空の正規化一致 | 0 |
| 近似重複候補 | 15組 |
| split をまたぐ候補 | 0 |

全データが同じ validation split / origin グループであるため、最後の0件は
split 独立性を立証する結果ではない。完全一致がなくても似た文が残ることを確認した。
候補は削除せず、原文の確認と将来の集計重み付けの検討対象とする。
翻訳関係や意味的言い換えを検出するものではなく、代表性も保証しない。

## 固定モデルの coverage

[仕様](../src/ext/uchardet/models/experimental/SEQUENCE_EVALUATION.md)に従い、
既存のフランス語 training artifact を変更せず、Rust book の別章を診断した。
training は introduction、validation は guessing game の1章。それぞれ別 origin / SHA。
同じ書籍の別章なので、独立した著者・ドメインの評価とは扱わない。

| 項目 | 分子 / 分母 |
| --- | ---: |
| 診断対象 | 1文書・27,265 bytes |
| 頻出 table 内 letter | 21,260 / 21,273 |
| training 未出現 letter | 13 / 21,273 |
| matrix 内の隣接 letter pair | 16,782 / 16,793 |
| matrix 外 pair | 11 / 16,793 |
| matrix 内の training 未観測 pair | 232 / 16,782 |

category 0/1/2/3 の質量は `[232, 0, 771, 15779]`。
分母は文書内の直接隣接であり、native filter を通した系列ではない。
**coverage は encoding accuracy や confidence の品質を示さない。**
`NOT_ENGINE_CALIBRATED` を維持し、この結果に合わせた閾値変更は行わない。
独立 holdout は既存 manifest の整合性検証で読まれるが、table 照合対象にはしていない。

## 再現性と公開範囲

[集計 JSON](benchmarks/v3-corpus-quality-2026-09-20.json)に入力・出力の content hash と
整数集計を保存する。完全 report、取得 archive、本文、生成 model は ignored の
`archives/v3-corpus/` に保存し、Git には同梱しない。
tool hash と Unicode/runtime 情報は完全 report に含む。同一入力の再実行で同一結果を確認する。

実行例（path は各自の保存先に置き換える）:

```sh
uv run --no-project python corpus/overlap.py \
  /disk/tatoeba-fra/manifest.json /disk/tatoeba-rus/manifest.json --output /disk/overlap.json
uv run --no-project python models/experimental/sequence_evaluation.py \
  /disk/sequence-training-fr-v1.json validation /disk/coverage.json /disk/fr-cp1252/manifest.json
```

次の課題は近似重複を考慮した source 選定、別著者・別ドメインの corpus 拡張、
native filter と training の適合、モデル品質・権利の検討である。
今回の診断だけで #123 / #124 を完了扱いにしない。P01 の保留も変更しない。

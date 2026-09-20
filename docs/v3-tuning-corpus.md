<!-- SPDX-License-Identifier: MIT -->
# French model較正に向けたtraining / tuning分離

[候補競合評価](v3-full-engine-model-comparison.md)で固定モデルの精度後退を確認したため、
validationを調整用へ転用せず、今後の較正に使うsplitを別revisionとして作成した。
元の32録音training、16録音validation、既存modelは上書きしていない。

## 分割と検証

[uchardet PR #40](https://github.com/PyYoshi/uchardet/pull/40)で
`corpus/sources/paris-training-tuning.json`を追加した。
既知の隔離後、録音identity SHA-256の昇順の先頭8録音をtuning、残り24録音をtrainingとする。
文章、検出結果、入力長、encoding変換の成否を分割選択に使わない。
録音内の文や派生encodingを別splitへ移さない。

- UTF-8/cp1252の全64 variantsをstrict変換できた。
- 別出力先へ2回取込・生成し、全fileでbyte一致した。
- validationを含む48 source / 1,128 pairの近似重複候補は0。
- tuningのfull入力は1,625〜3,331 bytesで、現行実験入口の4 KiB上限内。
- corpus 49件、source 42件のローカルtestとnative CI 11件が成功した。

近似重複候補0は意味内容・話者の独立性の証明ではない。以前trainingに利用した資料であり、
新たな未読の独立holdoutを確保したとは扱わない。独立holdoutは未開封を維持する。

manifest content hash: `1da3f89ee4325d1216e79aefc078def8fb4d8fec3730f3893deef4af0648bd19`。
overlap report content hash: `b0691327f16ef9447e5b778ba62088adf70877e55175aa0e18fdfda5f1a87434`。

## 24録音からの再生成

旧32録音modelはtuning録音を学習済みなので流用しない。
同じgenerator仕様でidentity / filteredを新たに生成し、両artifactがtraining 24録音のみを
含み、tuning録音IDを含まないことを確認した。manifestからの再計算validateも成功した。
係数・category境界・rankingはまだ変更していない。

| model | content hash | file SHA-256 |
| --- | --- | --- |
| identity | `7804fcf6a8d2e036c059585e311f405b8f3c7a8b668f6a5fba0dc6dc63827fdf` | `45adf0a7a5a65bc46641b684a59809b640128e6709d0ecbbc5924d19b5d897cc` |
| filtered | `01a1bd8fc984b9fa76e948a98c0ed11b82dc09032eada4a7e3bb41f71cd65124` | `64dfaf7c1f3e34a3549c9c3b0a8a46968e8468a450617e4315229d31d2a70ec2` |

生成物は`archives/v3-corpus/paris24-{identity,filtered}-training-v1.json`へ私的保存する。
再現はnativeの`PARIS_TRAINING.ja.md`の新recipe手順でmanifestを生成し、
`sequence_training.py train MANIFEST fr OUTPUT`と
`filtered_training.py train MANIFEST fr FILTER_BINARY OUTPUT`を使う。
それぞれ`validate ARTIFACT --manifest MANIFEST`で再計算検証する。
filteredのvalidateには`--binary FILTER_BINARY`も必要。

## 次の評価

まず係数未変更の2モデルでtuning baselineを観測する。指標は先頭候補のexact codec、
strict decode-equivalent、language、正解codecの候補内存在を分離し、16入力全体を報告する。
失敗入力だけの選別や入力の切り詰めはしない。全候補・confidence bits・done観測も残す。
較正候補を試す場合は、その候補集合と採否基準を事前に固定する。
baseline観測だけで標準採用・性能gate完了とはしない。生成modelの配布条件も未確定。

## 係数未変更のtuning baseline

上記2モデルを実験用targetへ接続し、tuning 8録音のUTF-8/cp1252全16入力を
one-shot/freshで評価した。French cp1252の1 slotのみを差し替え、他のmodel・ranking・
係数は変更していない。両buildの標準target出力一致とbuild provenanceを照合した。
各process上限10秒、入力4 KiB以下。入力の選別・切り詰めは行っていない。

| 入力 | model | exact codec | decode-equivalent | language一致 |
| --- | --- | ---: | ---: | ---: |
| cp1252 | legacy | 4/8 | 8/8 | 8/8 |
| cp1252 | identity | 1/8 | 4/8 | 8/8 |
| cp1252 | filtered | 2/8 | 5/8 | 8/8 |
| UTF-8 | legacy | 8/8 | 8/8 | 8/8 |
| UTF-8 | identity | 8/8 | 8/8 | 8/8 |
| UTF-8 | filtered | 8/8 | 8/8 | 8/8 |

cp1252入力でdecodeは成功するが正解文字列と異なる件数はidentity 4件、filtered 3件。
今回、正解codecの候補内存在件数はexact codec件数と同じだった。
decode-equivalentは当該入力上の一致であり、encoding全体の互換性・superset判定ではない。
legacyの学習corpusとの重複は不明なので、公平な未学習比較の保証とは区別する。

2回の比較でreport全体がbyte一致した。
private report: `archives/v3-corpus/paris24-tuning-engine-v1.json`。
content hash: `d34ffb575ce241519978ff704c9da96c821f67f3cae39dff54cbbde23f6ea9a6`。
file SHA-256: `70bf3cbb333edff74ea707a4149bab24752bcb3c368da5859e8b8c4cc26916f7`。

再現は`engine_probe.py --training ARTIFACT NEW_BUILD_DIRECTORY`で2つのbuildを作り、
`engine_comparison.py IDENTITY FILTERED MANIFEST IDENTITY_BUILD FILTERED_BUILD OUTPUT --split tuning`
を実行する。引数ARTIFACTは本書の24録音版、MANIFESTはtraining/tuning分割版を使う。
32録音版modelをこのtuning manifestへ渡すと、既存の学習重複検査で拒否される。

この結果を較正前の固定baselineとし、validationを見ながら係数を選ばない。
ここでは新たなvalidation予測や独立holdout予測は実行していない。

<!-- SPDX-License-Identifier: MIT -->
# 標準機能・コーパス偏り・生成物再実行の追加検証

2026-09-21。既定 engine / model / API / C++ 規格は変更しない。
P01 の native 安全性調査や独立 holdout 予測も再開していない。

## C++20 の機能単位の検証

[uchardet #21](https://github.com/PyYoshi/uchardet/pull/21) で独立 probe を追加した。
`cxx20` preset だけが有効化し、detector へリンク・install しない。
span、concepts、ranges sort/filter、bit_cast、signed/unsigned 比較、erase_if を
compile/run し、feature-test macro と標準ライブラリ識別情報を JSON 出力する。
Release で消える assert には依存しない。

ローカル GCC 16.2.1 / Clang 22.1.8（ともに libstdc++）で成功。
[native CI 35518598676](https://github.com/PyYoshi/uchardet/actions/runs/35518598676)
でも全11チェックが成功し、GCC / AppleClang / MSVC の cxx20 行で probe が通った。
通常 release preset では `BUILD_CXX20_PROBE=OFF` を確認した。

CI実測: GCC 13.3.0 / libstdc++ `20240904`、AppleClang 15.0.0 / libc++ `170006`、
MSVC 19.44.35228.0 / MSVC STL `143`。各macro値はrunの詳細出力に保持される。

これは標準規格フラグだけの成功より具体的な証拠だが、最低 OS / CRT、
manylinux container 内、各 Python wheel 内での新機能利用を実証したものではない。
#116 の最低 runtime gate は残す。[仕様](../src/ext/uchardet/tools/cxx20/README.md)。

## 近似重複グループ

前回の Tatoeba 400文の重複候補を、本文を変更せず連結成分として集計した。

| 成分サイズ | 成分数 | source 数 |
| --- | ---: | ---: |
| 1 | 374 | 374 |
| 2 | 10 | 20 |
| 3 | 2 | 6 |
| 合計 | 386 | 400 |

15候補辺が12の複数source成分を作り、26文がそこに含まれる。
連結成分内のすべての文同士が近似一致するわけではない。
386を統計的な有効標本数として扱わず、文の削除や既存benchmarkへの重み付けはしない。
`1 / 成分サイズ` は将来の比較用に示した例であり、採用済みの集計方針ではない。
全sourceがvalidationなので、cross-split成分0件も独立性の証明にはならない。
[仕様](../src/ext/uchardet/corpus/GROUPS.md)。

## 生成物の公開と中断後再実行

[uchardet #22](https://github.com/PyYoshi/uchardet/pull/22) では、実験modelの保存を
一時ファイルへの完成後、hard linkによる排他的公開へ変更した。
既存内容が同じならmtimeを維持し、異なれば上書きしない。
hard link非対応filesystemでは失敗し、危険な直接書込みfallbackはしない。
[保証範囲と制約](../src/ext/uchardet/corpus/ARTIFACTS.md)を明記した。

人工入力で途中例外、同一／異なる内容の同時公開、再実行、既存出力保護を検証。
強制killや電源断を実機で検証したとは扱わない。corpus全体のtransactionでもない。

保存済みFrench trainingを新しいファイル名で再生成し、元manifestから照合した。
同じ出力先での再実行も成功。旧生成物に対し次が一致した。

- 全文書counts、audit
- byte-to-order、pair category、頻出文字数、positive ratio bits
- language、encoding、生成parameters、keep-English指定、schema、権利状態

helperが依存hashへ加わったため、artifactと契約provenanceのhashは変わる。
旧生成物は保持し、validatorの依存照合は緩めない。古い結果を再現する場合は
作成時のcommitを使い、新しい実装では同じmanifestから別名で再生成する。
旧モデルとのnative精度・性能比較は行っていない。

[集計とhash](benchmarks/v3-reproducibility-2026-09-21.json)を公開する。
本文・archive・生成model自体はGit管理外に保持する。

## 残る境界

今回の進捗だけで #116 / #123 / #124 はcloseしない。
最低runtimeでの実行、新規modelのfilter適合と識別品質、別著者・別domainのcorpus評価、
生成model配布条件、3.0標準採用は引き続き別の判断・検証である。

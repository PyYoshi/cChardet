<!-- SPDX-License-Identifier: MIT -->
# v3 基盤整備の結果と残作業

2026-09-20時点。Phase 1〜3全体の完了報告ではない。

## 統合済みnative基盤

- [uchardet #10](https://github.com/PyYoshi/uchardet/pull/10): build preset、Debug/sanitizer分離、compiler CI。8構成成功。
- [uchardet #11](https://github.com/PyYoshi/uchardet/pull/11): 候補の正確な比較、任意の内部observer、観測artifact。9 CI成功。
- [uchardet #12](https://github.com/PyYoshi/uchardet/pull/12): corpus、model生成試作、固定source取得recipe。9 CI成功。
- [uchardet #13](https://github.com/PyYoshi/uchardet/pull/13): UTF-8 test I/OとC++11の移植性修正。corpusのWindows/macOS検証を追加し11 CI成功。

native統合点: `9ac0f79`。C++標準の既定値、公開API、標準model、runtime対応条件は変更していない。
C++20はnative compiler matrixでは通ったが、Cython/wheelの全配布条件を満たすという承認ではない。

## 既存corpusの失敗分類

```sh
uv run --locked python benchmarks/failure_analysis.py \
  --native-tool /path/to/uchardet-conformance \
  --native-revision 7993e0afe3b6c64f0ea3b43c7d4987118f6c5c12 \
  --uchardet-corpus src/ext/uchardet/test
```

toolはsampleのhash、候補とfloat bit、top-k、サイズ／言語／codec別母数を出力する。
evaluatorは既存比較と同じ`chardet.evaluation`。legacy corpusのlabelはfilename由来で、
独立した再検証済みground truthではない。

開始点の158件ではexact 153、compatible 154。
decode-equivalentはPython codecで評価できた149件中147件。
Python未対応codecの9件を誤判定と混同しない。language一致は151件。

| exactでないfixture | 観測による分類 |
| --- | --- |
| da/iso-8859-1、es/iso-8859-15、he/iso-8859-8 | compatibleまたはdecode-equivalent |
| ja/utf-16be、ja/utf-16le | 正解codecの候補不在 |

候補不在だけでは、未対応encoding・model不足・早期rejectのどれかは断定できない。
`RANKING_FAILURE`は「正解codecが下位にある」という観測で、confidenceの原因診断ではない。
今回の5件には下位exact候補がなかった。競合corpusを学習に使ったり、集約率だけで改善対象を決めたりしない。

## 自然文pilotとmodel生成

[nativeの取得recipe](../src/ext/uchardet/corpus/sources/README.md)は、
日仏露のRust book翻訳を固定revisionで使用する。許諾文・出典・hashを保持し、本文はGitへ同梱しない。
21 fileの取得対象は381,359 bytes。調査時の取得等を含めても20 MiB未満で、承認予算を超えていない。
6構成（3言語×UTF-8/legacy）・96 sampleを生成・検証した。
同じ本の翻訳なので、独立著者・Web全体を代表するcorpusではない。

French/cp1252のtraining本文11,946 bytesから新規byte-bigram modelを生成した。
同じ出力先への再実行も成功し、C++ headerを生成できた。

- model content hash: `925d882cf4534cefb0d2a0bc3b7effb34bc0f745024c651221c7d0a143b5ce62`
- model file SHA-256: `6ec2ae428ba882a5f85f577767c2b63392d16f3941dc78dd916d14e11510dc53`
- validation: 27,264 pairs、4.405195459375268 bits/pair（Laplace平滑化）

これは生成機構の診断であり、文字コード正解率でも既存modelに対する改善率でもない。
独立holdout枠の予測はまだ開いていない。生成modelの配布条件は未確定で、artifact自体は公開しない。
既存SequenceModelへのadapterと同じengineでの品質比較は未実装。

## 保留と継続可能な作業

[判断ログP01](v3-decision-log.md#p01-安全性検証の一部を保留2026-09-20)に従い、
追加安全性検証と未検証修正は保留した。既存sanitizer CIは維持している。

先頭4-byte bufferingの非デフォルトBOM試作はlocal branch `v3/bom-prototype`に保持する。
BOM分割の一部を改善する一方、通常入力の候補副作用、completion遅延、短いUTF-16の未解決点がある。
既存engineの大入力で停止が報告されているため、性能比較・標準採用は保留する。
未検証の修正や試作を統合済みnativeへ含めていない。

残作業:

- #116: C++20のCython/wheel・配布runtime互換性検証
- #118/#119: P01の安全性検証と修正。OOM注入・weight/reset契約も未完了
- #120: group内部のprober・reject/ranking理由。現状observerは最上位のみ
- #123: 既存engine用adapter、model品質比較、生成modelの権利判断
- #124: 独立corpus・real-world入力を含む失敗分析、family/coverage/校正の原因分類
- #125/#126: 3.0採用範囲、移行契約、試作の採否

上記を完了扱いにせず、保留部分を切り離して後続の独立作業を進める。

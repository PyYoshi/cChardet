<!-- SPDX-License-Identifier: MIT -->
# v3 改善対象の暫定順位と判断材料

2026-09-20時点。実装の優先順位と、現在ある証拠の強さを分ける。
この文書をencoding追加や標準model置換の承認とは扱わない。

## 既存158 fixtureから言えること

native `7993e0afe3b6c64f0ea3b43c7d4987118f6c5c12`の保存済み観測を
`codec-family-v1`で分類する。native再実行や独立holdout評価は不要。
[再集計の要約とhash](benchmarks/v3-family-analysis-2026-09-20.json)も保存した。

```sh
uv run --locked python -m benchmarks.failure_analysis \
  --observations /disk/saved-legacy-observations.json \
  --uchardet-corpus src/ext/uchardet/test
```

| 観測 | 母数と差分 | 現段階の扱い |
| --- | --- | --- |
| UTF-16 | 4件中exact 2件。日本語LE/BEの2件は正解候補不在 | 構造判定の改善候補。ただしmodel不足/早期棄却/入力不足の原因は未確定 |
| Western Latin | 25件中exact 23件。2件はdecode-equivalent | 異なるcodec名だけを理由に精度修正しない |
| Hebrew | 2件中exact 1件、compatible 2件 | superset/互換関係を維持して扱う |
| family未分類 | 34件、全件exact | detector未対応ではなく分析側mappingの未整備 |

残りのfixtureはexact一致。これは外部corpusや実Web上の精度を保証しない。
各familyの母数が少なく、実運用での出現頻度も測れていないので、
この数字だけではArabic・Vietnamese等の新規対応の順序は決められない。
原文本文とhashの照合を伴わない、保存済みreportだけの単純な再計数は根拠にしない。

`cause_status:UNRESOLVED`は計11件。そのうち2件が上記の候補不在で、
9件はcodec名こそexactだがPython側のcodecがなくdecodeを検証できない。
後者をdetectorの誤判定9件と数えたり、確認済み入力と扱ったりしない。

代表例も確認した。UTF-16 LE/BEの2件は各1,416 bytesで、先頭はそれぞれ
`55 00 54 00` / `00 55 00 54`。BOMを持たないため、BOMのfeed分割だけを改善しても
この2件の解決にはならない。保存観測の先頭候補は両方UTF-8であり、
これは今後のBOMなし構造判定を評価する例として残す。今回nativeで再実行はしていない。
Western Latinの差分はISO-8859-1とISO-8859-15間、HebrewはISO-8859-8に対する
Windows-1255で、3件とも判定languageはfixtureの言語と一致していた。

## 続行する順序

1. **失敗分析の再現性**: 保存観測とcorpusを照合し、family/workload別の母数、
   codec名の差、decode差、原因未確定を別々に出す。
2. **generatorとengineの接続契約**: character-order/4-category/ratioの形式を固定し、
   provenanceと人工fixtureでC++構造体への適合を検証する。品質とは別のgateとする。
3. **自然文の多様化**: 現在のRust book翻訳だけでは技術文書・同一書籍に偏る。
   別source/domainを権利確認後に追加し、文書単位の独立分割を守る。
4. **同一engineによるmodel比較**: filteringに対応したtraining/quantization仕様を明記し、
   OFF-default harnessで既存modelと比較する。未参照holdoutは基準を固定してから使用する。
5. **coverage/rankingの優先順位確定**: 独立・実運用corpusでの頻度と失敗の実害を確認してから、
   新規encodingやconfidence変更の採否を判断する。

## 今は進めないもの

- [P01](v3-decision-log.md)対象の追加安全性調査と、大入力を使うBOM試作の性能比較。
- 候補不在を理由にした「未対応encoding」「model不足」の自動断定。
- raw byte-bigramのlog loss改善を、encoding accuracy改善に読み替えること。
- C++20のwheelが通っただけでの最低runtime切り上げや新標準library機能の無条件採用。
- 権利条件未確定の生成modelの公開、既定model置換、master/releaseへの反映。

## 終盤で必要になる判断

既存のD01〜D06を維持する。現時点の通常基盤実装はこれらの回答を待つ必要はない。
生成modelの配布条件、標準採用による結果変更、対応platformの切り捨てが必要になった時点で、
測定結果・代替案・影響するIssueをまとめる。

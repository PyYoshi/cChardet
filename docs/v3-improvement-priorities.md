<!-- SPDX-License-Identifier: MIT -->
# v3 改善対象の開発順位と判断材料

2026-09-21更新。実装の優先順位と、現在ある証拠の強さを分ける。
この文書をencoding追加や標準model置換の承認とは扱わない。

## 分析から決定した開発順位

基盤の実装順ではなく、次に検証する利用者向け改善の順位を以下とする。
根拠は固定corpusの再現結果とsource確認であり、市場でのencoding出現頻度の順位ではない。
頻度・実装工数・改善率が未測定の項目に推測の数値を付けて加重scoreを作らない。
実装の容易さだけで順位を決めず、現在のmodel評価を妨げる共通原因を先に扱う。

| 順位 | 対象 | 確認済みの根拠と実害 | 変更範囲・判断 |
| --- | --- | --- | --- |
| 1 | incremental入力での証拠の一貫性、まずSBCS filterのchunk依存 | tuningのcp1252 8件でlegacyもwhole 8/8→1-byte 0/8。filter出力自体が分割で変わる | 既存modelにも影響。単なるconfidence倍率では回復しない。nativeでの状態保持・終了処理の設計を先行候補とする |
| 2 | Unicodeの構造的証拠：BOM境界とBOMなしUTF-16を別々に評価 | 初回feedだけのBOM判定と、BOMなし日本語LE/BE 2件の候補生成経路不足を確認 | bufferingと構造proberは別変更。BOM試作はP01で保留、BOMなし対応は新規試作・採用の判断が必要 |
| 3 | 新規SBCS modelの品質と内部選抜・confidence | validation cp1252 16件でlegacy16、生成5/7 decode-equivalent。代表例でnegative pairの減点と内部選抜を確認 | generator基盤は完成。現在のmodel置換は不採用。入力証拠を安定させてから別tuningで改善し、固定した未使用評価へ進む |
| 4 | 追加encoding/language、content hint | text/CSV/HTMLの利用者報告はあるが、現行再現や正解根拠に未確認部分がある | 言語ごとの追加順序を決める証拠は不足。権利・作成元・期待Unicodeを確認して優先度を再評価 |

順位1の根拠は[固定ratioのchunk比較](v3-ratio-chunks.md)にある。
同じ1,708-byte入力のfilter出力がwhole 275 bytesに対し1-byte feedでは51 bytesとなる。
これは単に候補名が異なるだけではなく、modelへ届く証拠の量・隣接関係が変わる問題である。
ただし最終判定は他proberとの競合もあり、全chunk差がこのfilterだけで直るとは約束しない。
新modelのratioを追加探索して、この差に合わせ込むことはしない。

順位2は[構造経路の確認](v3-utf-structure-gap.md)、順位3は
[選択cacheとscoreの照合](v3-full-engine-model-comparison.md)、順位4は
[利用者報告の確認条件](v3-real-world-reports.md)を根拠とする。
既存corpusのWestern Latin/Hebrewのdecode-equivalentな差は、新しいheuristicを追加する
優先理由にしない。codec未実装で評価不能な9件もdetectorの誤判定に数えない。

## #125/#126へ渡す先行候補と受入案

推奨する先行候補は「SBCS filterの入力分割依存を減らすnative incremental設計」。
以下は実装前の受入案であり、既存APIへの採用や試作枠の追加承認ではない。

- filter単体では同じ文書のwhole/1/7/64/1024-byte入力を比較し、最終flush後の証拠を照合する。
  途中文書resetで状態を破棄する。文書全体のbufferingで一致を作らない。
- pending区間・英字・区切り文字の扱いを明文化する。保持メモリの上限と、上限時に
  意味を変えるかどうかを実装前に決める。無制限のtoken保持を許容しない。
- detector全体では候補数/順序/encoding/language/confidenceとdone時点の差を分離する。
  全proberのchunk完全一致がfilter変更だけで実現したとは主張しない。
- 既存whole-inputの精度、UTF-8等の対照、短い入力、EOF/reset、max_bytesの境界を確認する。
  filter単体の一致だけを公開APIの回帰試験の代わりにしない。
- 固定した小〜中規模のnative benchmarkでlatency/throughput、allocation/memoryを測る。
  実行計画の性能基準を維持する。P01依存の試験が必要ならその部分を保留し、採用済みにしない。
- 既存2試作枠との関係とD02/D03を#125で決定してから実装する。検出結果が変わる場合は
  v3の移行説明と旧新比較を用意し、v2/masterには持ち込まない。

未参照holdoutは選抜のために開かず維持する。採用前の独立/real-world評価は残る。
ここで確定したのは、今ある証拠でどこから改善するかという開発順位であって、
新encodingの需要順位や製品全体のaccuracy優位性ではない。

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
| UTF-16 | 4件中exact 2件。日本語LE/BEの2件は正解候補不在 | 後続source確認でBOMなし構造判定経路の不足を確認。ranking調整とは分ける |
| Western Latin | 25件中exact 23件。2件はdecode-equivalent | 異なるcodec名だけを理由に精度修正しない |
| Hebrew | 2件中exact 1件、compatible 2件 | superset/互換関係を維持して扱う |
| family未分類 | v1で34件、全件exact | detector未対応ではなく分析側mappingの未整備 |

2026-09-21の[family mapping v2](v3-family-mapping.md)で未分類34件を明示分類した。
分類field以外のsample値は全件不変。以下のv1に基づく診断を精度改善とは読み替えない。

同日の[UTF-16 source確認](v3-utf-structure-gap.md)では、保存観測時と現状の判定経路が
同一で、BOMなしUTF-16候補を生成する構造proberがないことを確認した。
これは固定revisionの手動診断で、一般toolの候補不在を自動的に未対応と断定する変更ではない。

残りのfixtureはexact一致。これは外部corpusや実Web上の精度を保証しない。
各familyの母数が少なく、実運用での出現頻度も測れていないので、
この数字だけではArabic・Vietnamese等の新規対応の順序は決められない。
原文本文とhashの照合を伴わない、保存済みreportだけの単純な再計数は根拠にしない。

[既存利用者報告の整理](v3-real-world-reports.md)ではtext/CSV/HTMLの3件を確認した。
旧versionの報告や正解codec未確定のケースを現行accuracyへ加算せず、まずprovenance・
期待Unicode・現行再現を確認する。French tuningだけで改善順位全体を決定しない。

`cause_status:UNRESOLVED`は計11件。そのうち2件が上記の候補不在で、
9件はcodec名こそexactだがPython側のcodecがなくdecodeを検証できない。
後者をdetectorの誤判定9件と数えたり、確認済み入力と扱ったりしない。

代表例も確認した。UTF-16 LE/BEの2件は各1,416 bytesで、先頭はそれぞれ
`55 00 54 00` / `00 55 00 54`。BOMを持たないため、BOMのfeed分割だけを改善しても
この2件の解決にはならない。保存観測の先頭候補は両方UTF-8であり、
これは今後のBOMなし構造判定を評価する例として残す。今回nativeで再実行はしていない。
Western Latinの差分はISO-8859-1とISO-8859-15間、HebrewはISO-8859-8に対する
Windows-1255で、3件とも判定languageはfixtureの言語と一致していた。

## ここまでの基盤整備順（履歴）

[保存済みconfidence診断](v3-confidence-analysis.md)も追加した。閾値を上げた際の
残存件数とexact/compatible/decode-equivalentの分母を分離し、確率や推奨閾値とは扱わない。

1. **失敗分析の再現性**: 保存観測とcorpusを照合し、family/workload別の母数、
   codec名の差、decode差、原因未確定を別々に出す。
2. **generatorとengineの接続契約**: character-order/4-category/ratioの形式を固定し、
   provenanceと人工fixtureでC++構造体への適合を検証する。品質とは別のgateとする。
3. **自然文の多様化**: 当初のRust book翻訳だけでは技術文書・同一書籍に偏る。
   別source/domainを権利確認後に追加し、文書単位の独立分割を守る。
4. **同一engineによるmodel比較**: filteringに対応したtraining/quantization仕様を明記し、
   OFF-default harnessで既存modelと比較する。未参照holdoutは基準を固定してから使用する。
5. **coverage/rankingの優先順位確定**: 独立・実運用corpusでの頻度と失敗の実害を確認してから、
   新規encodingやconfidence変更の採否を判断する。

上記の生成基盤・native接続・品質評価は#123、代表的失敗の観測基盤は#120で受入済み。
未着手の基盤として繰り返さず、先頭の開発順位へ移る。

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

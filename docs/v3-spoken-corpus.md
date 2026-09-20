<!-- SPDX-License-Identifier: MIT -->
# 会話ジャンルによるcorpus多様化

2026-09-21。Rust bookの技術文書とTatoebaの例文に加え、Paris Storiesの会話書き起こしを
validation専用に取り込んだ。[実装PR](https://github.com/PyYoshi/uchardet/pull/23)、
[取得・抽出仕様](../src/ext/uchardet/corpus/sources/PARIS_STORIES.md)。

## 取得・権利・分割

公式repositoryの固定commit `dec76f7a1731318b033c578d534410b0a3d4ea5c` の
README / LICENSE / upstream devテキスト、計1,169,312 bytesのみを取得した。
元READMEは本文を含むCC BY-SA 4.0の会話corpusとして説明している。
許諾文・contributors・元URL・revision・hashを取り込み先へ保存し、toolのMITと分離する。
本文・音声・生成modelはGitへ公開していない。音声URLは取得せず、録音識別のhashにだけ使う。

比較候補French-GSDでは注釈と元本文の権利が異なるため、同じライセンス表示を根拠に
本文を取り込むことはしなかった。詳細な出典は取得仕様に記録した。

692文を録音ごとの16文書にまとめ、全てvalidationとした。
sentenceの元順序を保ち、1録音内でsplitを分けない。会話の話者・内容の独立性までは
確認しておらず、独立holdoutとは扱わない。trainingには使用していない。

抽出UTF-8は41,876 bytes。UTF-8/cp1252、全体/64/1024/4096 bytesの128 variantは
全てstrict往復で生成できた。cp1252向けの文字・文の削除や置換は行っていない。
別出力への再生成でmanifest・本文を含めて全byteが一致し、cache再検証の追加取得は0 bytes。

## 固定tableの別ジャンル診断

既存Rust book introduction由来の未較正training artifactを変更せず、
16文書のfull cp1252 textだけをPythonで照合した。入力は計40,777 bytes。
modelの再学習や閾値変更、native検出は行っていない。

| 指標 | 技術文書の既存validation章 | 会話16文書 |
| --- | ---: | ---: |
| training未出現letter | 13 / 21,273 | 57 / 30,445 |
| matrix外の隣接letter pair | 11 / 16,793 | 55 / 22,213 |
| matrix内のtraining未観測pair | 232 / 16,782 | 531 / 22,158 |

会話のcategory質量0/1/2/3は `[531, 0, 1550, 20077]`。
文書境界を跨ぐpairは作らず、文数やサイズvariantを独立文書として重複計数しない。
表の比率は出現回数によるmicro集計であり、長文の寄与が大きい。

**これはencoding accuracyでも、native confidenceの較正でもない。**
ジャンルを追加すると固定tableの未観測範囲が変わることを示す材料であり、
「会話で誤判定が増えた」「新modelより旧modelが良い」とは結論しない。
trainingのfilterはidentityのまま、`NOT_ENGINE_CALIBRATED`を維持する。

## コーパス横断の重複監査

French Rust book / French Tatoeba / Paris Storiesの3manifestを既存overlap profileで監査した。
読込対象219 source、23,871 pair。Rust book独立章1件の本文は開いていない。
近似候補は2組で、どちらも同一Tatoeba manifest内。cross-manifest / cross-split候補は0組。

対象には短文と文書が混在し、文字5-gram集合のJaccardは部分転載や翻訳を見逃す。
したがって0件でもcorpusの独立性や無漏洩を保証しない。自動削除・再分割も行っていない。

[集計JSON](benchmarks/v3-spoken-corpus-2026-09-21.json)にmanifest/report hashと整数分母を保存した。
今回もP01の安全性調査と独立holdout予測は保留のまま。

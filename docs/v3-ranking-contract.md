<!-- SPDX-License-Identifier: MIT -->
# 現行candidate rankingのsource上の契約

調査revision: uchardet `04f3bc4a927d116da12a8e161273239a804e21c5`。
sourceを読んだ整理であり、新しい入力のnative実行、ranking再実装、
安全性修正、公開API変更は行っていない。

## 一つの「順位問題」にまとめない

候補が返るまでには異なる段階がある。

1. prober内で候補とscoreを作る。
2. UniversalDetectorがshortcutまたはthresholdを通った候補をReportする。
3. C API側が既知languageの重複を整理し、confidence順へ挿入する。
4. language weightが有効なら別候補列を重み付きconfidence順へ並べる。
5. Python wrapperが結果を公開する。

現在のtraceは2のraw Reportを別のobserver subclassで記録する。
最終C API候補列の内部操作をその場で記録しているわけではない。
raw Reportに存在しないencodingが、最初から未実装なのか、prober内部で失われたのか、
threshold以下だったのかは、raw Reportと最終結果だけでは区別できない。

## sourceで確認した規則

| 段階 | 確認した挙動 | 分析時の注意 |
| --- | --- | --- |
| shortcut | shortcutがあるとその候補をReportして終了 | 通常のhigh-byte候補収集と同じ経路ではない |
| threshold | high-byte経路はscoreが0.20より大きい候補だけReport | 0.20と同値は通らない。閾値はこの経路のもの |
| 重複 | encodingが同名かつ双方のlanguageが非null・同名なら重複比較 | null-language同士はこの条件を満たさない |
| 同一候補 | 新scoreが既存より大きければ置換、以下なら新Reportを採用しない | codec aliasの同等性で重複整理しているわけではない |
| 挿入順 | 自分より小さいconfidenceの手前に挿入 | 同scoreでは既存候補の後。alphabetical tie-breakではない |
| weight | raw候補列からweighted列を再構築 | final confidenceはraw confidenceと同一とは限らない |
| weighted同点 | raw候補列の走査順を保つ挿入 | 同点化後も元の順序が影響する |

weightは指定languageならその係数、それ以外はdefault係数をraw confidenceに掛ける。
C APIのgetterがweighted列を選ぶ条件はlanguage weight mapが空でないことである。
default weightだけを設定する場合を、Pythonのlanguage_weightsと同じ契約として説明しない。
Python側はlanguage keyを小文字化し、係数を有限の0〜1へ検証する。
C APIを直接呼ぶ場合まで、そのPython検証が適用されるとは限らない。

ここでの順序説明は通常の有限scoreについてのsource整理。
NaN等の異常score、reset後の全lifecycle契約、allocation failureを検証した記述ではない。
これらの追加native安全性検証はP01の保留を維持する。

## sourceと入力ごとの原因証明を区別する

規則が分かっても、ある入力の正解候補が下位だった理由を自動確定できるわけではない。
model coverage、候補を作ったprober、threshold前score、Report順序、
実際に設定されたweightを同じrevision・入力・feedで対応付ける必要がある。
同score・同labelのReportが複数あれば、保存値の一致だけで採用元を一意に決めない。

したがって[保存値の対応照合tool](v3-report-attribution.md)の
`ranking_reason=UNRESOLVED`は変更しない。Pythonへrankingを複製して
engineと独立に乖離する第二の判定実装を作らない。
将来の診断追加では、まず「threshold前」「Report」「重複整理」「weight後」の
どの段階を観測したかを明示し、最終順位だけから推測した理由をlogへ入れない。

## 固定した根拠

- `src/nsUniversalDetector.cpp`: DataEnd、MINIMUM_THRESHOLD。
  Git blob `06c2d9a2306afdb136d99e9020863c576d22c492`。
- `src/uchardet.cpp`: HandleUniversalDetector::Report / WeighCandidates / getters。
  Git blob `f5b46ba9b31e7c435523f1b03a8d29f96cb8f20e`。
- cChardet `src/cchardet/__init__.py`: _validate_language_weights。

この調査をcandidate stability、score較正、全入力での正当性の実行証拠に読み替えない。

<!-- SPDX-License-Identifier: MIT -->
# v3 基盤整備の結果と残作業

2026-09-20時点。Phase 1〜3全体の完了報告ではない。

## native lifecycleの追加検証（2026-09-21）

[uchardet #43](https://github.com/PyYoshi/uchardet/pull/43)を統合し、
続く[uchardet #44](https://github.com/PyYoshi/uchardet/pull/44)の修正を含め、
nativeを`f2873ba1fdf521fc7311fbb3c1272be83d87c667`へ固定した。
[再現手順と比較範囲](../src/ext/uchardet/test/LIFECYCLE.ja.md)に従い、
空入力・ASCII・UTF-8・cp1252の4入力を3巡する12比較をCTestへ追加した。
finalize後のresetと途中の文書を破棄するresetについてfresh detectorを対照とし、
同一feed後・1回のfinalize後の候補数、順序、encoding、language、confidence bit列、
doneを比較する。languageのnullと空文字を区別し、getter再読の安定性も確認する。

ローカルの154 CTestは失敗なし（既存corpusの5件はconfigure時に対象外）。
GCC・Clang sanitizer・AppleClang・MSVC等の11 CIも成功した。
これは小規模な通常入力の再利用検証であり、accuracyやchunk間一致の保証ではない。
nativeの繰返しfinalize、finalize後feed、weight、error/OOM、大入力、並列利用は
このtestの対象外。Python wrapperのcloseのべき等性とnative C APIの保証を混同しない。
engine・公開APIは変更せず、P01と#117全体は未完了のままとする。

cChardetのshared sanitizer CIでは、既存公開関数`uchardet_is_done`のGNU/Darwin
export一覧への登録漏れがリンク失敗として現れた。#44で登録を補完し、
Linux/macOS/WindowsのRelease shared build・lifecycle実行をnative CIへ追加した。
全11 CIは成功。ローカルGCC Release shared build・CTest・symbol exportも確認した。
公開headerの13関数、export一覧、GCC shared objectの定義済みdynamic symbolを
照合し、13関数すべてがexportされることも確認した。
ローカルGCC sanitizerは環境の`/usr/lib64/libasan.so.8.0.0`欠落でリンクできず、
実行成功とは扱わない。shared sanitizerの統合確認はcChardet CIで行う。

## 統合済みnative基盤

- [uchardet #10](https://github.com/PyYoshi/uchardet/pull/10): build preset、Debug/sanitizer分離、compiler CI。8構成成功。
- [uchardet #11](https://github.com/PyYoshi/uchardet/pull/11): 候補の正確な比較、任意の内部observer、観測artifact。9 CI成功。
- [uchardet #12](https://github.com/PyYoshi/uchardet/pull/12): corpus、model生成試作、固定source取得recipe。9 CI成功。
- [uchardet #13](https://github.com/PyYoshi/uchardet/pull/13): UTF-8 test I/OとC++11の移植性修正。corpusのWindows/macOS検証を追加し11 CI成功。

native統合点: `4117df7`（#19の旧generator廃止を含む）。C++標準の既定値、公開API、標準model、runtime対応条件は変更していない。
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
SequenceModelの形式契約とC++出力は追加済み。同じengineでの品質比較は未完了。

さらにPython-onlyの[明示training profile](../src/ext/uchardet/models/experimental/SEQUENCE_TRAINING.md)
で、同じFrench training文書から54文字の形式契約を生成した。
整数countsからの再計算、manifest本文からの再生成照合、別出力先とのbyte一致を確認した。
[hashと確認結果](benchmarks/v3-sequence-training-2026-09-20.json)を公開するが、model本文は公開しない。
文書境界・同頻度tie・category化・binary32丸めを固定した未較正profileであり、
既存SBCS filterに合わせたtrainingやconfidence較正ができたことを意味しない。

### 別sourceの追加

[Tatoeba CC0 pilot](../src/ext/uchardet/corpus/sources/TATOEBA.md)を追加した。
公式の仏語・露語CC0 archiveを各1回取得し、圧縮転送量は計827,069 bytes。
各200 sentenceを採用し、UTF-8/legacy codecとサイズ別の計2,400 variantを試行、
2,367件成功・33件skipとなった。skipはsentence数ではなくvariant数。
別出力先で再生成し、manifest・本文・生成reportがすべてbyte一致した。

全sourceはvalidation専用で、翻訳関係未確認のため同じoriginグループとする。
独立holdoutやtrainingには混ぜず、native評価は実施していない。
低いsentence ID順の抽出は代表性のある無作為抽出ではない。
hashと件数のみを公開し、原文・archive・生成本文はGitへ同梱しない。

## 保留と継続可能な作業

[会話ジャンルのvalidation corpus](v3-spoken-corpus.md)を追加した。
Paris Storiesの16録音文書・692文を固定取得し、128variant生成・別出力のbyte一致と
固定tableのcoverage診断を確認した。trainingやnative精度評価は行っていない。

[標準機能・コーパス偏り・生成物再実行の追加検証](v3-reproducibility-results.md)では、
独立C++20 probe、重複候補の連結成分、単一生成物の排他的公開を記録した。

[コーパス重複監査と固定モデルの validation 診断](v3-corpus-quality.md)を追加した。
Tatoeba 400文から近似候補15組を検出し、別章での未観測文字・pairを整数集計した。
native 検出・独立 holdout 予測は実施しておらず、精度改善の実績とは扱わない。

追加の基盤整備:

- [manifest分析tool](v3-manifest-analysis.md): 評価対象と対象外を明示し、旧pilot 96件を予測なしで棚卸し。
- [C++20配布検証](v3-cxx20-distribution.md): 任意有効化によるローカルwheel検証。既定値は維持。
- [uchardet #14](https://github.com/PyYoshi/uchardet/pull/14): 生成成功/skip理由の記録、ground truth由来、metadataのみのsplit監査。11 CI成功。
- [uchardet #15](https://github.com/PyYoshi/uchardet/pull/15): 明示的なSequenceModel接続契約とC++出力。人工modelの構造体適合・binary32一致を検証し11 CI成功。既定modelへの登録はしない。
- [uchardet #16](https://github.com/PyYoshi/uchardet/pull/16): group直下childのactive/stateと前回snapshotとの差分。小fixtureで従来出力一致を確認し11 CI成功。詳細原因はunknownのまま。
- [uchardet #17](https://github.com/PyYoshi/uchardet/pull/17): Tatoeba CC0 snapshotとoffline取り込み。source 17 testsとframework 24 tests、11 CI成功。検出精度を測った結果ではない。
- [uchardet #18](https://github.com/PyYoshi/uchardet/pull/18): 未較正のPython-only training profile。14限定testsと11 CI成功。自然文trainingでも生成・再計算の再現性を確認したが、native品質比較はしていない。
- [uchardet #19](https://github.com/PyYoshi/uchardet/pull/19): 現build等からの参照がない旧generator 2本と専用依存定義を廃止。保持対象160filesはhash一致、11 CI成功。生成済みmodel・header・由来ログは変更せず、削除したtoolはGit履歴から復元可能。
- [改善対象の暫定順位](v3-improvement-priorities.md): 保存済み観測と原因未確定を分離し、model形式・corpus多様性・品質評価の順序を整理。

[判断ログP01](v3-decision-log.md#p01-安全性検証の一部を保留2026-09-20)に従い、
追加安全性検証と未検証修正は保留した。既存sanitizer CIは維持している。

先頭4-byte bufferingの非デフォルトBOM試作はlocal branch `v3/bom-prototype`に保持する。
BOM分割の一部を改善する一方、通常入力の候補副作用、completion遅延、短いUTF-16の未解決点がある。
既存engineの大入力で停止が報告されているため、性能比較・標準採用は保留する。
未検証の修正や試作を統合済みnativeへ含めていない。

残作業:

- #116: C++20の30 wheel build/smokeは成功。最低配布runtimeと新標準library機能のavailability確認は残る
- #118/#119: P01の安全性検証と修正。OOM注入・weight/reset契約も未完了
- #120: group直下とlanguage detectorのstate/counterは追加済み。reject/ranking理由は未観測
- #123: native filterとtrainingの適合、model品質比較、生成modelの権利判断
- #124: 独立corpus・real-world入力を含む失敗分析、family/coverage/校正の原因分類
- #125/#126: 3.0採用範囲、移行契約、試作の採否

上記を完了扱いにせず、保留部分を切り離して後続の独立作業を進める。

## 多言語script pilotの追加（2026-09-21）

[日本語・アラビア語・ヘブライ語CC0 pilot](v3-script-corpus.md)を追加した。
31文・186 variantsの再生成一致を確認したが、日本語・アラビア語は各2文しかない。
取得成功を代表的な精度評価や十分なcoverageと扱わず、追加sourceの必要性を記録した。

## language detector観測の追加（2026-09-21）

既定OFFのnative traceで、内部language detectorのstate・累積文字数・sequence統計を
読み取れるようにした。追加のconfidence計算や名前取得methodは呼ばず、既存headerは
friend宣言のみ。モデル名は静的labelであって予測結果ではない。

従来の空・ASCII・135-byte日本語の同一feedで旧snapshot/raw Reportと最終候補が一致した。
GCC16.2.1の同一Release buildでは全61 engine object memberがbyte一致した。
archive自体のmetadata差、他compiler、一般的な性能測定とは区別する。
手順・比較のskip条件は[native診断文書](../src/ext/uchardet/benchmark/introspection.ja.md)。

日本語fixtureのFrench language modelではsequence総数35に対して4分類counter合計0を
観測した。model外の文字対は分母のみ増えるため、単純なcategory比率と同一視できない。
これはUnicode language detectorの観測であり、新規SBCS trainerとの適合を確認したわけではない。
reject/ranking原因はunknownを維持し、#120全体は未完了とする。

[raw Reportと最終候補の対応照合](v3-report-attribution.md)も追加した。
保存artifactの完全一致候補を列挙するだけでrankingを再実装せず、同値重複の曖昧さや
異なるinput/buildを照合した可能性を隠さない。既存小fixtureの9通りでも確認した。

## coding state・SBCS統計の観測（2026-09-21）

native traceの追加field `prober_evidence` で、MBCS childのcoding stateと
SBCS modelの初期化済みcounterを読み取る。Big5は独自処理なのでcoding stateをnullとし、
Hebrewの補助proberは統計model一覧から除く。静的model labelを最終候補と同一視しない。

baseline `a56fd958` と同じGCC16.2.1 Release buildで、全61 library object memberが
byte一致した。既存3小fixtureの5 feed scheduleで追加field以外の観測が一致し、
fresh/reuseと固定randomを含む6 scheduleでも最終候補が一致した。
追加testは4件成功。詳細とskip条件はnative診断文書を参照する。

これはfeed後のsnapshotであり、全byteの状態遷移履歴ではない。rejectの根本原因や
ranking理由は未解決のまま。P01保留中の作業や追加の不正入力探索は再開していない。

[固定model coverageの文書平均・サイズ別評価](v3-coverage-strata.md)では、
会話16文書が1〜4 KiBに集中し、短文・大文書の評価が欠けていることを明示した。
microだけでなく文書macroを厳密分数で記録し、未定義分母・空区間を区別する。

[trace ON/OFFの限定測定](v3-trace-cost.md)では同一buildのlibraryとbenchmarkが
byte一致した。native小fixtureの計測値も記録したが、最初の条件に時間ドリフトがあり、
同一実行ファイルの差を高速化やregressionとして扱わない。

[ranking契約のsource調査](v3-ranking-contract.md)では、threshold、既知languageの
重複整理、同点順序、weightを別段階として整理した。入力ごとの原因証明とは分け、
保存値照合の`UNRESOLVED`を根拠なく確定理由へ置き換えない。

[日本語codec matrix](v3-japanese-codec-matrix.md)では既存validation章の2抽出profileから
7 codec・4形式・6上限・2境界を生成し、480成功・192変換不能を区別した。
別出力の全file一致を確認したが、profileの段落選択biasを精度向上と扱わない。

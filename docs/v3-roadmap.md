# cChardet v3 開発ロードマップ

状態: 開発の方向性は合意済み。具体的な実装計画・評価閾値は本書の提案を出発点として検証する。

現状確認日: 2026-09-20。対象は cChardet `bc41189`（2.3.0）と、同梱する
PyYoshi/uchardet `7993e0a`。本書の公開をもって各作業が実装済みになったとは扱わない。
リリース日は未定。

本書および今後のv3開発文書は日本語で管理する。
利用者向けのREADME、APIリファレンス、公開リリースノートなどは英語を基本とする。
開発上の議論と利用者向けの説明を分け、確定した仕様は利用者向け文書にも反映する。

## 目次

- [目指す製品と対象範囲](#direction)
- [現状と根拠](#baseline)
- [リポジトリ・ブランチの責務](#ownership)
- [優先順位・依存関係・リリース範囲](#phases)
- [Phase 1: native開発基盤](#phase-1)
- [Phase 2: corpusとmodelの基盤](#phase-2)
- [Phase 3: 失敗分析](#phase-3)
- [Phase 4〜6: 検出器の改善](#phase-4-6)
- [Phase 7〜9: 代替実装と長期研究](#phase-7-9)
- [測定方法と変更の受け入れ基準](#measurement)
- [v3で決める契約と移行方針](#contracts)
- [最初の実装単位](#first-prs)
- [リリース条件・リスク・進捗管理](#release)

<a id="direction"></a>

## 目指す製品と対象範囲

cChardet v3は、実際のデータ取り込み処理に適した、高速・軽量・並列化可能な
native文字コード検出器を目指す。主要用途はスクレイピング、クローリング、
HTML・文書の取り込み、RAG前処理、学習用corpusの整備、ETL、大量ファイルの並列処理とする。

特に数KiB〜数百KiBの入力における速度、少ないallocation、incremental処理を重視する。
通常のCPythonとfree-threaded CPythonの双方で、独立したdetectorを効率よく並列実行できる
設計を維持する。複雑な判定ロジックはPython wrapperへ移さず、native側で扱う。

ダウンロード数増加の原因は未確定である。AI用途、大規模downstream、使い捨て環境での
再インストールなどは仮説として扱い、ダウンロード数から入力分布や利用目的を断定しない。

chardetとの完全互換を最上位目標にはしない。馴染みのあるAPIは価値があるが、
必要な改善を互換性が妨げる場合は、Python API、C API/ABI、検出結果、デフォルト設定の
破壊的変更をv3の選択肢に含める。変更には理由、測定結果、明示的な仕様、移行方法を用意する。
互換アダプターは必要に応じて検討し、nativeの主要な処理経路に恒久的な複雑さを持ち込まない。

本書はv3系列全体のロードマップであり、すべてのPhaseを3.0までに終える計画ではない。
Rust、新しい検出器architecture、SIMDは条件付きの後続作業とする。
3.0では基盤整備に加えて利用者に意味のある改善を届けるが、具体的な対象は失敗分析の後に選ぶ。

<a id="baseline"></a>

## 現状と根拠

以下は現在のリポジトリを確認して得た事実であり、本書の作成時に既存テストや測定を
すべて再実行したという意味ではない。

| 領域 | 既にあるもの・確認先 | 今後必要なこと |
| --- | --- | --- |
| Python開発環境 | [uv設定](../pyproject.toml)、[Makefile](../Makefile)、型情報、テスト | lockされた環境を維持し、engine用toolとwrapper用toolの責務を分ける |
| CI・native安全性 | [Test workflow](../.github/workflows/test.yml): Linux ASan/UBSan、3 OSでのPython 3.11〜3.14/3.14t | native compiler・build構成のmatrix、専用fuzzing、静的解析の継続実行 |
| native build | [CMake設定](../src/ext/uchardet/CMakeLists.txt): 最小版宣言は3.5、C++11、DebugでASan付与、CPU/浮動小数点flagはglobal | 明示的で移植可能なoption、target単位のflag、実際の最小版とmulti-config動作の確認 |
| native test | [CTest登録](../src/ext/uchardet/test/CMakeLists.txt)で既知の失敗5組を除外 | 対象・失敗理由を可視化し、既知の失敗を黙って集計から消さない |
| 挙動比較 | [random bytesのwrapper test](../tests/test_robustness.py)、[native候補出力tool](../src/ext/uchardet/benchmark/uchardet-output.cpp) | 機械可読な比較、lifecycle・終了状態の追跡、失敗入力の最小化 |
| 性能測定 | [native benchmark](../src/ext/uchardet/benchmark/README.md)、[Python比較](../benchmarks/pyperf_compare.py)、[threading比較](../benchmarks/pyperf_free_threading.py) | version付きworkload、測定値の分布、allocation・memory・並列scalingの報告 |
| 精度測定 | [評価script](../benchmarks/accuracy.py)でcorpus別のexact/compatible/decode-equivalentとlanguage指標 | sample単位の記録、評価定義のversion管理、data分割、失敗分類 |
| test data管理 | [Test data policy](test-data-policy.md) | corpus manifest、license一覧、決定的な生成、data混入の検査 |
| model生成 | [生成手順](../src/ext/uchardet/script/README)、[BuildLangModel.py](../src/ext/uchardet/script/BuildLangModel.py)、language/charset定義と生成log | 参考調査と由来の記録。既存generatorは非採用を基本とし、再現性・品質を検証できる新規実装を作る |
| packaging | [wheel workflow](../.github/workflows/build.yaml)、[wheel smoke test](../tools/wheel_smoke.py) | native連携を変更しても配布物をinstallした状態で検証 |

[既存の性能分析](performance-analysis.md)には、同梱fixture 158件について、2.2.0 baselineから
nativeの実行時間がwhole-fileで54.5%、64-byte chunkで51.6%減少した測定がある。
これは特定workloadでの結果であり、すべての入力で同じ改善があるという意味でも、
新しいv3の測定結果でもない。engineを変更する前にbaselineを取り直す。

既存の候補比較だけでは、任意のchunk境界で必ず同じ結果になることや、異なるplatform間での
bit単位の一致までは証明できない。その保証範囲も今後明示する。

<a id="ownership"></a>

## リポジトリ・ブランチの責務

### cChardetのブランチ運用

`master`を安定版、`dev`をv3の開発統合先として分ける。
`dev`は2.3.0リリース後の`master`から開始し、v3の作業branchは原則として`dev`から作成する。
v3開発用のDraft PRは`dev`をbaseにする。本ロードマップのPRも同じ運用に従う。

安定版に必要な修正は`master`向けPRとして扱い、`dev`にも必要な修正を計画的に反映する。
v3の破壊的変更を2.xへまとめて逆流させない。
3.0の公開前に、`dev`の内容を`master`へ統合するrelease PRでリリース条件を確認する。
公開tagは承認したrelease commitに付け、branch名だけを公開の根拠にしない。

CIは`dev`向けPRと`dev`へのpushを専用の入口から実行し、テスト・wheel buildの本体を
既存workflowと共有する。変更がMarkdown（`.md`）/reStructuredText（`.rst`）だけなら、
`dev`ではworkflow自体を起動しない。code・設定・submodule更新を含む場合は通常どおり検証する。
`master`向けPRでは既存の必須checkを維持するため、文書だけでもCIを実行する。
release tagと手動実行も引き続き検証対象にする。
GitHubのpath filterによる省略はPR全体の差分で判断され、code変更のあるPRへ文書commitを
追加した場合もCIは実行される。今後`dev`に必須checkを設定する場合は、文書PRでcheckが
未報告のままmerge待ちにならない設計を選ぶ。
Rulesの適用範囲とprereleaseの起点も開発基盤整備で確認し、`dev`という名前だけで既存の
保護・release設定が引き継がれるとは仮定しない。

### uchardetのブランチ運用とsubmodule連携

PyYoshi/uchardetも`dev`をv3の開発統合先として分離する。
開始点はcChardet 2.3.0が使用している`7993e0afe3b6c64f0ea3b43c7d4987118f6c5c12`とする。
既存の`cchardet`を改名・置換せず、v2のnative保守先として残す。

| 用途 | cChardet側 | PyYoshi/uchardet側 | 連携方法 |
| --- | --- | --- | --- |
| v2安定版・保守 | `master`（v3公開前） | `cchardet` | v2互換の修正をnative側へmerge後、承認したcommitへsubmoduleを更新 |
| v3開発 | `dev` | `dev` | native側の`dev`向けPRをmerge後、cChardetの`dev`向けPRでcommitを固定 |
| 過去の実装 | 過去のtag・履歴 | `obsoleted-cchardet` | 履歴参照用。新規開発やv2保守のbaseにはしない |

uchardetのv3作業branchは`dev`から作り、Draft PRのbaseも`dev`とする。
既存のuchardet `master`はv3統合先に転用せず、現在の履歴を維持する。
双方のrepositoryで`dev`を作っても、自動的に同じ時点の実装になるわけではない。

cChardetのv3開発側では`.gitmodules`の`branch`を`dev`、v2保守側では`cchardet`とする。
URLは引き続きPyYoshi forkを指す。`branch`は主に`git submodule update --remote`で参照する
branchの指定であり、通常のcheckoutやCIが使うのは親repositoryに記録したcommitである。
branch指定だけの変更ではgitlinkを進めず、実際のnative更新は別途レビュー・検証する。
CIやrelease buildでbranch先端を自動取得せず、必ず記録されたcommitを使う。

共通のbug修正は、v2でも成立する小さな修正なら`cchardet`へ先に適用し、
`dev`向けの別PRでcherry-pickまたは同等の修正を反映する。
v3で先に見つけた問題はv2への影響を調べ、必要な修正だけを個別にbackportする。
元PR・commitと反映先を紐付け、両方で検証する。v3のbranch全体をv2へmergeしない。
upstream由来の修正も、各branchへの必要性とAPI互換性を確認して取り込む。

3.0公開時にもuchardetの`cchardet`はv2保守先として維持し、`dev`はv3系列の統合先として使う。
nativeのrelease対象commitを記録し、cChardet releaseのgitlinkで固定する。
cChardetの`master`をv3へ移行する前には、2.xの保守を継続する場合の専用branchと保守期間を
Betaまでに決める。安定版branchを移行したためにv2の修正先が消える状態にしない。
uchardetの`dev`に適用するCI・RulesもPhase 1で確認し、branch作成を保護設定の完了とは扱わない。

### Repository間の分担とPR

- cChardetは、全体ロードマップ、Python API/CLI、packaging、downstream連携、
  Python経由の競合比較、リリース時の移行案内を管理する。
- PyYoshi/uchardet forkは、native build、安全性検証、fuzzing、内部状態の追跡、C API、
  engine benchmark、engineの挙動比較を管理する。v2は`cchardet`、v3は`dev`で管理する。
  実体のあるforkを使い、submoduleはcommitを固定する。
  `.gitmodules`をAPI互換性のないupstreamへ切り替えない。
- corpus/model toolは、まず利用するnative engineと同じforkに置く。
  Python製toolにはuvでlockした環境を用意し、取得・生成・評価を別moduleとして扱う。
  data専用repositoryへの分離は後から判断し、初期着手の前提にはしない。
- native変更をforkのPRでmergeした後、依存するcChardet側PRでsubmoduleを更新する。
  連携testは実際に固定するnative commitを対象にする。
  cChardetとuchardetのversion番号を揃える必要はなく、native ABIのversionは別に判断する。
- PRはDraftで作成する。local検証後に関連変更をまとめてpushし、CIの再試行や状態確認のためだけに
  pushを繰り返さない。不要なCIはcancelし、重い定期job・release wheel buildと軽いPR検証を分ける。
- Gitには小さな再配布可能fixture、schema、生成recipe、設計判断、要約reportを置く。
  大規模dataと生のbenchmark結果は別保管とし、hashと保管先・保持方針を記録する。
  通常のCIではWebのlive crawlingを行わない。

実装時の配置案は以下とする。まだ存在しないpathを含み、実装済み成果物や実行可能commandを
表すものではない。

| 管理先 | 配置するもの |
| --- | --- |
| cChardet | `docs/decisions/`、`docs/v3-migration.md`、version付きbenchmark report |
| uchardet | `CMakePresets.json`、`fuzz/`、`test/`または`tools/`内の挙動比較・trace tool |
| uchardet | `corpus/`内のschema・manifest・recipe、`modelgen/`内のoffline generator |
| uchardet | model一覧と`legacy`/`generated`の由来分類。実際のfile移動は必要性がある場合に行う |

<a id="phases"></a>

## 優先順位・依存関係・リリース範囲

| Phase | 優先度 | 依存するもの | 完了を示す成果物 | リリース上の位置づけ |
| --- | --- | --- | --- | --- |
| 1. native開発基盤 | P0 | 現状棚卸し | 移植可能なbuild、安全性検証、挙動比較、trace | 3.0の必須基盤 |
| 2. corpus/model基盤 | P0/P1 | Phase 1のbaseline。schema作業は並行可能 | 監査済みcorpus v1、用途別分割、再現可能なmodel生成の試作 | 3.0の必須基盤。全model置換は不要 |
| 3. 失敗分析 | P1/P2 | Phase 2の評価dataとPhase 1のtrace | 再現可能な失敗report、優先順位付き改善候補 | 3.0で利用者に届ける変更を選ぶ |
| 4. 対象を絞った精度改善 | P2 | Phase 3 | 変更前後のreport、意図した候補差分、移行判断 | 3.0の候補 |
| 5. encoding/language拡充 | P2 | Phase 2〜3 | 独立dataで評価したmodel追加と処理cost測定 | 3.0または後続v3の候補 |
| 6. 段階的検出とevidence方針 | P3 | Phase 3〜5の知見 | hint、入力制限、早期終了の実験 | 3.0に含めるか個別判断。後続なら互換性を再確認 |
| 7. Rust試験実装 | P4 | Phase 1〜2のmodel・挙動の契約 | 挙動を維持した並行実装と比較report | 3.0の必須条件ではない |
| 8. 次世代model/engine | 研究 | Phase 2〜3。実装言語比較にはPhase 7 | 現在の限界を根拠にした設計提案 | 後続。互換性は改めて判断 |
| 9. 高度な最適化 | P5 | profilingで確認した遅い箇所と回帰検証基盤 | portable fallback、runtime dispatch、実測した効果 | 必要な場合のみ |

主要な順序は「1 → 2 → 3 → 選択した4/5 → 3.0」とする。
corpus schemaとmodelの棚卸しはPhase 1と並行できるが、検出結果を変える作業は評価基盤を待つ。
後半のPhaseは、問題なく動くengineを必ず書き換えるという約束ではない。
3.0公開後に必要になった破壊的変更は、ロードマップに載っていたことを理由にminor releaseへ
押し込まない。必要なら次のmajor releaseで扱う。

<a id="phase-1"></a>

## Phase 1: native実装を安全に変更し、結果を説明できるようにする

### Build・静的解析・CI

Debug/Releaseとsanitizer有効化を分離する。CMake/compilerの最小versionは、実際に使う機能と
wheelの対象環境から決めて文書化する。
C++20を有力候補として検証し、安全性・保守性に役立つ機能を採用する。
既存のC++11維持を目標にはせず、採用する機能と配布条件を根拠に規格を決める。
warning、sanitizer、benchmark、fuzzのoptionをtarget単位に整理し、static/shared build、
install/exportのsmoke test、再現可能なpresetを用意する。
native toolはPythonをimportせずにbuild・実行できるようにする。

setuptools経由の拡張module buildには独自の連携がある。
CMakeの検証だけでwheelも確認できたとは扱わず、両方を検証する。
platform・浮動小数点flagの変更は候補scoreに影響し得るため、toolchain整理とscore変更を分ける。
配布binaryでは`-march=native`や実行環境を選ぶISAの無条件有効化を行わない。

### C++規格とmemory safetyの改善

規格の更新だけで安全になるとは扱わず、所有権・寿命・境界条件をcodeで表現するために使う。
まずC++20で必要な機能を小さく試し、配布対象すべてで検証してから採用を確定する。
さらに新しい規格の機能も、解決する問題と配布costを示せる場合は個別に検討する。

| 改善対象 | 採用候補 | 確認すること |
| --- | --- | --- |
| 所有するbuffer・resource | `std::vector`、`std::unique_ptr`などのRAII | 解放漏れ・二重解放・error経路の後始末を減らす。再利用するbufferのallocation回数や初期化costも測る |
| 借用するbuffer | C++20の`std::span`、読み取り専用なら`std::span<const T>` | pointerとlengthの食い違いを減らす。所有者・有効期間・再allocationによる無効化を明示する |
| 状態・値の区別 | `enum class`、index/長さなど用途ごとの型 | magic valueや異なる単位の混同を減らす。C APIとの変換点で値域を検証する |
| model tableの整合性 | `constexpr`、`static_assert` | tableの寸法・定義・参照の整合性をbuild時に検証する。生成物にも検証を適用する |

RAIIなど既存規格でも使える機能の導入を、C++20採用の決定まで待つ必要はない。
一方、`std::span`は所有権を持たず、参照先の寿命や範囲外アクセスを自動的に保証するものではない。
境界検査、整数overflow、符号付き/符号なし変換、buffer無効化の規則は別途整理する。
`const`なviewでも別threadによる元bufferの書き換えは防げないため、Pythonから借用する可変bufferと
GIL解放の扱いも確認する。ASan/UBSan、fuzzing、allocation失敗の検証と組み合わせる。

規格採用の判断では、構文のcompile成功と、標準library・runtime・ABIの互換性を分けて確認する。

- Linux: 対象manylinux imageと最小glibc条件を固定し、必要なC++機能をbuildする。
  `auditwheel`で`GLIBC_*`/`GLIBCXX_*`などの要求を調べ、最低対応環境でwheelを実行する。
  musllinuxを追加する場合は別の配布対象として検証する。
- Windows: 対応MSVC toolsetとruntime条件を決め、生成したwheelのimport・native処理を検証する。
- macOS: Apple Clang、SDK、deployment target、libc++の機能可用性を確認し、最低対応OSで実行する。
- Python連携: standalone CMakeとCython/setuptoolsの両経路で同じ規格方針を適用し、
  通常版・free-threaded版のwheelと、sdistからのbuildに必要なcompiler条件を確認する。

結果は「使う機能・規格・最小toolchain・最低対応OS/runtime・検証artifact」を対応付けた
設計判断に残す。利用したい機能が現在の最低環境で使えない場合は、代替実装だけでなく
v3で最低環境を引き上げる選択肢も、利用者への影響と利益を比較して判断する。

PRは、規格/build設定の変更、所有権・型の整理、検出algorithmの変更に分ける。
所有権の整理は小さな対象から進め、同じ入力・feed手順で候補結果を比較し、
allocation・memory・latencyの変化を測る。必要なerror契約の変更は明示的にレビューする。
規格更新と同時にscoreやrankingを変えず、差分の原因を追える状態を維持する。

### CIの実行範囲

| CI区分 | 対象 | 初期budget・運用方針 |
| --- | --- | --- |
| 関連PRごと | Linux GCC/Clang、Windows MSVC、macOS Apple Clang。代表的なDebug/Releaseとstatic/shared | 全組合せではなく必要な軸を覆う。native job単位で15分以内を初期目標 |
| native PRごと | Linux ASan + UBSan、決定的な挙動比較、最小化済みfuzz回帰入力 | 問題検出時は失敗させる。sanitizer有効時の速度を通常buildと比較しない |
| native PRごと | Clang Static Analyzer、対象を絞ったclang-tidy | 既存指摘には理由・担当を付け、新しい未説明の指摘を増やさない。抑制よりinvariant明示を優先 |
| native PRごと | 時間制限付きlibFuzzer smoke test | 初期値はtargetごと60秒。既知の回帰入力は毎回再実行 |
| 定期・手動 | 長時間fuzz、compiler構成の拡大、利用可能ならnative ARM64、統制した環境での性能測定 | fuzzはtargetごと30分を初期値とし、実行回数・coverage・seed corpusを記録 |
| Release candidate | サポートするPython/wheel matrix、installed-wheel smoke、sdistからのbuild | 通常版とfree-threaded版。リリース時の対応範囲を明示 |

これらの時間は初期案であり、現在のCI設定でも、十分なfuzz coverageの証明でもない。
実測に応じて調整する。依存libraryのinstrumentationとplatform条件が整う場合に、
未初期化memory検出のMSan、独立detector間の競合検出のTSanを検討する。
CodeQLはlocal解析が役立つ状態になってから、導入・維持costを踏まえて判断する。

### Nativeの挙動比較とfuzzing

既存の候補出力toolを拡張し、比較結果を機械可読にする。
fixtureと決定的に生成した入力ごとに、one-shot、1・7・64・1,024 byte単位、
seed固定のrandom境界でfeedする。
空・極短入力、NUL、壊れたmultibyte sequence、長い繰り返しや不利な入力、reset/reuse、
複数回のfinalize、candidate取得、終了状態を対象にする。
fuzz入力には上限を設ける。巨大入力やallocation失敗は別のresource budgetとfault injectionで
検証し、通常のPRに数GiBのfixtureを要求しない。

次の2種類の比較を区別する。

1. **変更前後・実装間の同等性**: 同じ環境・同じfeed手順で旧実装と新実装を比較する。
   candidate数・順序、encoding、language、confidence、最終結果、error、終了eventを対象にする。
2. **chunk境界によらない結果の一致**: 同じbytesを異なる区切りで渡した場合を比較する。
   まず現状の差を記録し、bug、仕様上の早期終了の影響、意図したv3の仕様変更のどれかを判断する。
   変更前後で同じだったことは、chunk境界への非依存性を証明しない。

呼び出し側が渡したbyte数、観測可能な範囲でengineが実際に調べたbyte数、`done`が変化した
eventを記録する。chunk単位の終了判定を、終了の根拠になった正確なbyte位置とはみなさない。
終了後のfeedを無視・拒否・継続処理のどれにするかも、trace比較の前に定義する。

同じtoolchainで挙動維持を目的とする変更は、まずexact comparisonを基準にする。
既存toolの10進数出力は出発点として使うが、bit単位の一致を主張する場合は浮動小数点の
生の表現も記録する。異なるtoolchain間の差は、根拠のないepsilonで隠さず、数値計算の契約を決める。

public APIと関連するmodel/state machine内部をfuzzし、one-shotとincrementalの比較も行う。
失敗は最小化し、seed、build flag、再現commandを付けてtest data policyに従って保存する。
allocation失敗を注入し、OOM時の解放・error通知を検証する。
C ABI境界から想定外の例外が漏れないようにする。

独立detectorと共有する不変model dataのthread safetyを定義する。
可変なdetectorを複数threadで共有できるかは別の契約であり、GILを解放するだけでは保証されない。

### 内部状態の追跡とmodel生成過程の調査

任意で有効化するnative traceに、稼働・除外されたprober、score、language、状態遷移、
早期終了理由、rankingと同点処理の理由を記録する。
分析に使う理由codeとmodel/prober IDは安定させ、詳細event形式は開発用interfaceとして扱ってよい。
release buildではtraceをcompile時に除外するか、無効時costが十分小さいことを測定する。
入力本文はデフォルトでlogに残さない。

model familyごとにgenerator、入力source、revision、license表記、parameter、生成file、
手動変更を棚卸しする。`script/BuildLangModel.py`、language/charset定義、既存logから始める。
既存手順で自動生成が説明されているのはsingle-byte modelであり、multibyte tableにも
同じ手順が使えるとは仮定しない。追跡できない由来は「不明」と記録し、推測で埋めない。
調査は既存modelの理解とprovenance把握のために行い、既存generatorの改修・再利用を前提にしない。

保守者から、過去の利用で「同じ処理を繰り返しても結果が安定せず、生成modelの品質がかなり
落ちる傾向があった」と報告されている。これは過去の経験に基づく判断材料であり、今回の
再現実験で原因を特定したという意味ではない。v3では既存のmodel生成scriptの使用を推奨せず、
新しい生成基盤の依存にしないことを基本方針とする。

調査範囲は入力取得・正規化・統計処理・出力形式・既知の制約の把握に絞る。
旧scriptの再現や修復を新規開発の必須条件にはしない。
v3側での削除は、依存するbuild・文書・生成物の参照と必要な由来記録を確認したうえで別PRにする。
v2の保守branchと既存modelは一括削除しない。既存modelの品質とgeneratorの品質も別々に評価する。

Phase 1の完了条件は、新規checkoutから文書どおりにbuild・検証できること、既知の安全性問題と
test失敗が見えること、native比較を再現できること、代表的な誤判定をtraceで説明できること、
model生成の再現可能範囲と不足が明確になっていることとする。

<a id="phase-2"></a>

## Phase 2: corpusとmodelの再現可能な基盤を作る

### Corpusの役割・層とdata混入の防止

corpusの**用途**と**性質による層**を別々に扱う。
用途はtraining/model生成、tuning、validation、independent evaluationの4区分とする。
層は次のとおり。

| 層 | 目的 | 初期候補と制約 |
| --- | --- | --- |
| A: 文字・構造の網羅 | codec mapping、状態遷移、境界条件 | version固定のmappingと生成case。自然言語精度の根拠にはしない |
| B: 制御した自然文 | language model、ranking、confidence、入力sizeごとの傾向 | 由来を確認した多言語Unicode sourceをstrictに再encode |
| C: 独立評価 | 汎化性能と競合比較 | revision固定のchardet/charset-normalizer corpusなど、独立して管理されるdata |
| D: 実際の文書 | 壊れたdata、宣言、現実の取り込み処理 | local archive抽出と再配布可能な文書。Common Crawl本文はcommitしない |

encoding変換、切り出し、HTML化、size別生成を行う**前に、元の文書/source group単位で分割**する。
分割のseed、algorithm、割り当て結果を固定する。
完全一致・近似重複を検出し、可能な範囲でlegacy corpus/modelのsourceとの重複も調べる。
過去の学習dataとの重複が不明なら、完全に独立した評価とは主張しない。
評価dataの失敗を見てtuningした場合は、その参照を記録する。
以後の独立評価には新しい未参照のholdoutを用意する。
同じ原文の文字コード違い・size違いを別の独立文書として数えない。

source候補は、多言語自然文のLeipzig、mapping・境界条件のUnicode data、作品ごとに権利確認した
Gutenberg、local Web評価のCommon Crawlとする。
collection全体で同じlicense・再配布権・生成modelの配布条件が適用されるとは仮定せず、
dataset単位で確認する。取得adapterは任意で使えるものとし、取得不能によって通常buildが
壊れたり、評価の母数が黙って減ったりしないようにする。

archive由来sampleはsnapshot、WARC位置、offset/length、content hash、抽出recipe、正解labelの
根拠を持つ。charset宣言だけを正解にはしない。
確認済みlabel、複数のcompatibleな可能性、未解決caseを分ける。
未解決caseは堅牢性や遭遇頻度の観測に使い、正解率を出すために推測でlabelを付けない。
archiveの公開状況や削除要請で再現できなくなったsampleは、欠落として明示する。

### Manifestと生成の契約

version付きJSON/JSONL schema、validator、受理・拒否される小さな記述例を用意する。
初期の必須項目は以下とする。

| 記録 | 必須情報 |
| --- | --- |
| Source | 安定したID、URL/保管位置、license識別子・原文参照・確認状態、revision、元dataのhash、languageとlabel決定方法 |
| Sample | schema/corpus version、sample/source-group ID、用途・層、language、encodingとlabel確度、encoder/version、source textとbytesのhash、byte/文字数、変換parameter、生成日時 |
| 派生関係 | 親ID、正規化方針、切り出し範囲、目標/実size、分割先、途中切断・不正sequenceの状態、該当するHTML templateと宣言 |
| 実行記録 | manifest hash、tool/engine commit、環境、command、seed、除外/欠落数と理由、成果物hash |

元のUnicode sourceを保存し、正規化、改行変換、大文字小文字処理、本文選択を明示・version管理する。
判定に役立つ情報を黙って正規化で消さない。
encodeはstrictを使い、decodeで元に戻ることを確認する。
表現できない文は生成対象から外した理由を記録し、`ignore`/`replace`で黙って変換しない。
alias、CP932とShift_JISのようなvariant、superset関係は実際のmappingに基づくversion付き定義で扱う。

入力sizeは16・32・64・128・256・512 B、1・4・16・64・256 KiBを目標budgetにする。
正常sampleは完全なencoded文字境界で止め、実sizeを記録する。
stateful encodingは終端・状態の復帰も含めてbudget内で正しく生成する。
sequence途中で切れるsampleは、明示的な途中切断・異常系として別に生成する。
短いsourceを繰り返しで埋めて、大きな自然文の代表として扱わない。
同じ本文を使う比較と、同じbyte budgetを使う比較も区別する。

plain textはclean/adversarial、HTMLはclean/declared/undeclared/mismatched/malformedに分ける。
HTTPとmetaの不一致、UTF-8宣言なのにCP932のbytes、宣言なし、XML宣言、entityの多いmarkupなどを含める。
宣言内容と実際のencodingは独立に記録する。
API response、CSV、e-mail、subtitle、document exportも由来を確認したworkloadとして段階的に追加する。
生成HTMLだけで実Webの評価を済ませない。

### Model生成とprovenance

生成pipelineは完全新規実装を基本とする。既存scriptを抽出・整理して使い続ける計画にはしない。
取得 → 正規化 → language/encodingによる選別 → 統計生成 → 検証 → 出力を、それぞれ検証可能な工程として設計する。
必要な仕様・数式・data形式とその出典を記録し、旧codeやtableを取り込む場合は再利用として明示する。
新しいfileに書いたことだけを理由に、独立した由来や希望するlicenseを適用できるとは判断しない。
まず棚卸しを基にsingle-byteのlanguage/encoding familyを1つ選ぶ。
再配布可能な小さなcorpusで決定性を検証し、別途、現実的なtraining dataでmodel品質を調べる。
小さなdataから再現可能に生成できただけでは、実用modelが完成したとはしない。

generator/runtime/dependencyはuvで固定し、走査・出力順序、乱数seedを固定する。
network利用は取得工程に限定する。
独立したclean環境で2回生成し、canonicalなmodel内容のhashが一致することを確認する。
実行日時はcanonicalな内容から分離するか再現可能な時刻規則を使い、
記録用timestampのために同じmodelが異なるhashにならないようにする。
同じ作業directoryで繰り返しても既存出力を二重集計しないこと、途中失敗後の再実行でも
結果が変わらないことを検証する。固定入力に対する決定性と再実行時のべき等性を別々に確認する。
生成したmodelは同じengine上で既存modelと比較し、未使用dataで精度・候補・confidence・
性能を評価する。hashが一致するだけでは品質の合格とせず、採用基準を満たすまで既存modelを置換しない。

生成modelにはmodel/format version、generator version/commit、corpus revision/hash、
source license参照、language/encoding family、生成parameter、由来分類、生成日時の規則、
内容hashを付ける。legacy modelの実際のlicense表記や不明項目は保持する。
新しいgeneratorで処理しても、再利用したtableや変換処理の由来が消えるわけではない。

試作modelには、特定言語に依存しない小さな表現形式を定義する。
tableの次元、順序、数値型、量子化、検証条件を明示し、まずbuild時のC++ source生成を使う。
必要性を示さずruntime loaderやallocationを追加しない。
出力前に次元・値域・参照を検証し、将来のRust emitterも同じcanonical artifactを使う。
初期schemaで歴史的modelすべてを表す必要はなく、未対応familyを明記してversionを上げながら拡張する。

### 新規fileのlicenseを決める時期と対象

新規fileに適用するlicenseは未決定である。
利用・組み込み・開発参加のしやすさを重視し、LGPL、MIT、Apache-2.0などを候補として比較する。
LGPLはversionと「or later」の有無も決める。以前のMPL-2.0を第一候補とする案は固定方針にせず、
由来に応じた条件を確認する。ここでは候補の適用可否や既存資産のrelicense可否を確定しない。

Phase 1のV3-01でlicenseの設計判断を行い、対象componentの新規実装・外部contributionを
受け入れる前に、そのcomponentで使うlicenseとfile表記の規則を決める。
model generatorの新規実装まで未決定を持ち越さない。
全componentを一括で決める必要はないが、未決定の対象を明示する。

| 対象 | 判断時に確認すること |
| --- | --- |
| 新規engine/tool/generator/test | 独自実装か既存codeの派生か、依存library、希望するlicenseの適用条件、利用・修正・配布時の扱い |
| 既存codeと改修file | 現在のlicense・著作権表示・由来。新規file向けの選択を一律に適用しない |
| Corpus | sourceごとの条件、取得・加工・再配布・model生成に関する確認事項 |
| Generated model/table | corpus・generator・再利用tableの由来、生成物の配布条件。generatorと同じlicenseだと自動判断しない |
| 開発文書・schema・sample | codeと同じ方針にするか、外部資料やsampleの条件、帰属表示 |

判断結果は`docs/decisions/`に日本語で残し、対象範囲、採用licenseとversion、選定理由、
未解決事項を記録する。確定後、対応するLICENSE/COPYING、file header/SPDX、package metadata、
contribution案内を整合させ、配布物の表記も確認する。
希望するlicenseへの移行を妨げる既存資産は由来を追跡し、必要なら段階的な独自実装・model置換を検討する。
既存の表示を削除して方針に合わせることはしない。
取り込み・再配布・表記変更前の確認が済まないdataは、local参照に留める選択肢を持つ。

Phase 2は、corpus v1、検証済みのmanifest/分割validator、決定的なsize/encoding/HTML生成、
provenance一覧、C++ emitterを含む再現可能な試作modelが揃った時点で完了とする。
不明な歴史的training dataの復元や、全legacy modelの置換は完了条件にしない。

<a id="phase-3"></a>

## Phase 3: 失敗を分析し、改善対象を選ぶ

固定した2.3.0 referenceと開発中engineを、利用可能な固定済みcorpus全体に対して実行する。
sampleごとの予測、候補、score、label確度、source group、入力size、model version、必要なtraceを残す。
corpus・language・encoding family・size・workload別に件数と母数を公開し、
data欠落、未対応codec、判定保留、crash、誤判定を区別する。

失敗は無理に一つへ分類せず、根拠とともに複数labelを付けられるようにする。

| 分類 | 必要な根拠 |
| --- | --- |
| `UNSUPPORTED_ENCODING`、`MODEL_MISSING` | 対応一覧・model一覧と、欠けているcodecまたはlanguage coverage |
| `WRONG_ENCODING_FAMILY`、`RIGHT_FAMILY_WRONG_CODEC` | version付きfamily/mapping定義と候補の観測結果 |
| `SUPERSET_AMBIGUITY`、`INSUFFICIENT_EVIDENCE` | 複数codecで同じbytesが妥当・同値になること、または識別根拠の不足 |
| `RANKING_FAILURE` | 正しい可能性のある候補が負けた理由を示すtrace。候補に含まれることだけでは断定しない |
| `CONFIDENCE_CALIBRATION` | 定義したscoreの意味と実際の正解頻度が、未使用dataでも継続してずれること |
| `STRUCTURAL_VALIDATION_FAILURE`、`LANGUAGE_MODEL_FAILURE` | decoder/state machineまたはmodel/proberの挙動による根拠 |
| `DECLARATION_CONFLICT` | bytesとmetadata・宣言内容の不一致 |
| `UNRESOLVED` | 根拠不足。考えられる原因を残して調査する |

top-k candidate recallを測り、候補生成とrankingの問題を分ける。
confidenceは初めから正解確率とはみなさず、まずscoreとして扱う。
何の正しさを校正するのか（exact codec、compatibleなdecode、languageとの組合せ）を定義し、
binごとの件数を伴う信頼度曲線や、判定保留率と誤り率の関係を調べる。
確率としての校正結果は未使用dataで評価する。

少数の文書しかない区分から強い結論を出さず、件数の不足を明示する。
不確かさを推定する際はsource group単位で再標本化し、多数の派生sampleを独立観測として扱わない。

改善候補は、実際の遭遇頻度と誤判定cost、見込める精度改善、実装工数、実行時間・memoryの増分、
provenanceの整備状況から優先順位を付ける。
costが高いほど優先度が上がるような単純な掛け算は使わない。
収集しやすいcorpusでの頻度を、そのままWeb全体の頻度とはみなさない。
選んだencoding familyごとに根拠と不確かさを公開する。

Phase 3は、再実行可能なreport、人が確認した代表的失敗、優先順位付きbacklog、3.0範囲の決定で完了とする。
評価指標の定義はレビュー・version固定し、競合すべてに同じものを適用する。
現在の`chardet.evaluation`依存もversion付きの実装であり、永遠に不変な正解定義として扱わない。

<a id="phase-4-6"></a>

## Phase 4〜6: 根拠に基づいて検出器を改善する

### Phase 4: 対象を絞った修正

確認できた構造検証・BOMの問題、model選択、ranking、confidenceから着手する。
変更ごとに失敗分類を紐付け、一般化できるbytes/modelの性質を修正し、
成立する例・成立しない例・曖昧な例を用意する。
corpusごとの変更前後の全結果と候補差分を、悪化したcaseも含めて公開する。
外部benchmarkに直接合わせる調整や、その場しのぎのheuristicの積み重ねは避ける。

languageのconfidenceはencoding labelと区別する。
ASCIIだから英語とは限らず、複数言語が混じる入力は、無理に一つを断定せず
unknownや複数languageを表す仕様が必要か検討する。

### Phase 5: 必要性の高いcoverageを増やす

調査候補は日本語、簡体字・繁体字中国語、韓国語、Cyrillic、中東欧、トルコ語、ギリシャ語、
ヘブライ語、アラビア語、ベトナム語とする。
これは候補一覧であり、これらがすべて未対応という意味ではない。
実際に不足するlanguage/codecの組合せはPhase 3の結果から選ぶ。

model追加ごとにprovenance、training/tuning/evaluationの分離、独立corpusと実dataでの検証、
別familyの誤検出、初期化・allocation cost、model size、throughput、候補安定性を確認する。
旧modelと新modelを同じengineで比較してから、engine書き換えの効果を判断する。

### Phase 6: 段階的な判定とcontent hint

安価な構造検証（BOM、ASCII、UTF-8としての妥当性、UTF-16/32構造、escape sequence）と、
任意のXML/HTML/HTTP hintを試作する。
特に短いASCII互換入力では、UTF-8として妥当なだけで元のencodingを確定できるわけではない。
選んだ仕様の下で確定的な根拠になるものと、候補の順位付けに使うものを分ける。

metadataの不一致・欠落、壊れたmarkup、hintとbytesの不整合時の挙動を定義する。
native側で処理量に上限のあるparseを行い、costを測る。
HTML専用APIまたは明示的hintを検討し、汎用detectにWeb固有の意味を黙って持ち込まない。
統計的な判定ロジックはnative側に置く。

evidence limitは64 KiB、200 KiB、1 MiB、unlimitedを比較する。
識別に必要な情報が後半に現れる入力も含め、調べたbyte数、精度・confidence、latency、
allocation、memoryを報告する。
現在のunlimited defaultは比較基準であり、v3の制約ではない。
根拠が揃えば変更し、明示的に制限を解除する方法と移行案内を用意する。

早期終了と候補の枝刈りは、捨てる候補の上限に関する根拠、または実測による評価を必要とする。
後続bytesが判断を覆すcaseを検証する。
architecture変更の前にprofilingと失敗分析を行い、重複計算をSIMDで埋め合わせない。
Phase 4〜6は大きな一括mergeではなく、選んだ機能ごとに完了を判定する。

<a id="phase-7-9"></a>

## Phase 7〜9: 代替実装と長期研究

Rustの試験実装は、共通のmodel形式と挙動比較の契約が使えるようになってから着手する。
目的は性能比較に加え、安全に保守できることと開発参加の容易さである。
C++を実行可能なreferenceとして残し、最初は入力から結果までを通せる小さな範囲を選ぶ。
初期portは承認済みmodelを再利用して挙動を維持し、score/model改善と同じ変更に混ぜない。

encoding、language、candidate、状態を型で表し、可変状態はdetector内に閉じ、所有関係を明確にする。
通常の検出logicはsafe Rustを基本とし、`unsafe`はFFI、dispatch、最適化kernelなどへ局所化して
必要な理由を記録する。
`cargo test`、rustfmt、clippy、property-based test、fuzzing、Miri、sanitizerは、
それぞれ実際に検証できる範囲を踏まえて使う。

薄いC ABI層は選択肢だが、Rust内部へC APIの構造をそのまま移す理由にはしない。
FFI境界ではbufferの寿命、所有権、panic/errorの変換、独立detectorのthread safetyを定義する。

同じfeed手順、壊れた入力、lifecycle、終了event、候補順序・language・confidence、model内容を比較する。
数値計算の契約上可能ならexactに一致させ、不一致を調査した後でのみ根拠のある許容差を検討する。
native latency、throughput、memory、allocation、並列scaling、binary size、build/install cost、
wheel対応範囲も比較する。
Rustで書いたという事実だけでは、安全性、独立した著作物であること、license適合性の証明にはならない。

Rustを主実装にするか、両engineを維持するか、C++を主実装のままにするかは、比較reportの後に決める。
独自生成modelの拡大や新architectureは、既存の限界を示す根拠が得られてから、互換性も別途判断する。

SIMDやarchitecture固有kernelは最後に検討する。
profilingで確認した遅い箇所、runtime feature dispatch、portable fallback、architecture間の正しさ、
小〜中規模workloadでの実際の利益を条件とする。
dispatch・allocation・保守のcostが効果を上回る最適化は採用しない。

<a id="measurement"></a>

## 測定方法と変更の受け入れ基準

engineの性能改善にはnative C API benchmarkを使う。
cChardet/chardet/charset-normalizer間の比較にはinstall済みrelease wheelを使う。
native engineの処理時間とPython API経由の時間は意味が異なるため、別々に公表する。

競合に利用可能なnative acceleratorがあれば有効にし、実際にloadされたmodule pathを確認する。
Pure Python fallbackは別構成として報告し、package名だけから実装方式を推測しない。
version、wheel hash、interpreter/GIL mode、compiler flag、CPU/OS、利用可能ならaffinityと電力設定、
corpus hash、commandを記録する。

bytesは測定前にmemoryへ読み込み、code/modelを同じ条件でwarm-upする。
baselineと変更版の実行順を交互にし、測定値の分布を保存する。
detectorを毎回生成する場合とreuseする場合の両方を測る。
warm-upを理由に、毎回生成する測定から初期化costを黙って除外しない。

最上位結果だけの取得と全候補取得、serialとmulti-thread、one-shotとincrementalを分ける。
I/O込みのend-to-end測定は別枠にする。
affinityを設定できないplatformでは未設定と記録し、同じ統制条件を満たしたと主張しない。
p50/p95 latency、throughput、allocation回数・byte数、peak memory、model/binary sizeを、
測定toolの制約とともに報告する。

精度reportにはexact codec、compatible/superset、decode-equivalent、language、
encodingと言語の組合せ、判定保留、正解不明による除外を含める。
decodeはstrictに行い、不正・途中切断入力でdecode-equivalenceを定義できない場合は別に扱う。
corpus別・区分別の件数を維持し、macro平均やworkloadで重み付けした平均だけにまとめない。

リリース時には精度・性能reportに加え、次の評価表を維持する。

| 評価軸 | 残す根拠 |
| --- | --- |
| Coverage | codec/language/script対応一覧、観測した未対応sample、明示したworkload分布に限った重み付きcoverage |
| 堅牢性 | 最小化した異なるfuzz不具合、sanitizer指摘、chunk/lifecycle不一致、OOM処理結果、fuzzのcoverageとbudget |
| 保守性 | 新規checkoutからのsetup手順・時間、検証したcompiler/platform、静的解析の残課題、model生成の再現性、由来の未解決事項 |
| 代替engine | FFI/unsafeの使用箇所と理由、buildの複雑さ、挙動差、速度・memoryと並べた維持cost |

fuzzで失敗を観測しなかったことをmemory safetyの証明とはしない。
対応encoding数が増えたことだけを、実際のdataに対する精度改善ともみなさない。

Phase 1のbenchmark手順とともに確定する、初期のレビュー基準は次のとおり。

- **安全性**: 未調査のcrash、sanitizer error、新しい静的解析指摘、不正な出力を残さない。
  既知の問題は明示し、xfailを精度testの成功として数えない。
- **機械的変更・port**: 定義した同等性の範囲で、未説明の候補・lifecycle差分を残さない。
  意図して変える挙動は別のレビュー対象にする。
- **性能**: 主要workloadのいずれかで、native median latency/throughputに再現する5%超の悪化、
  またはp95/memory/allocationに10%超の増加があれば調査する。
  throughputの悪化はbytes/secの減少、latencyの悪化は時間の増加であり、同じ百分率として扱わない。
  allocationが0だった処理は百分率ではなく絶対数で比較する。
  noiseが大きい、または測定数が不足する結果は未確定とし、統制した環境で再測定する。
- **精度**: 正解が既知の入力で変わった結果をすべて列挙する。
  全体の改善でfamily/size別の未説明の悪化を隠さない。
  曖昧な入力で想定した変化や統計的に未確定の改善は、そのように明示する。
- **トレードオフ**: 精度と性能の交換は、対象範囲、測定結果、緩和方法を記録した判断で受け入れられる。
  閾値はレビューのきっかけであり、価値あるv3変更の禁止でも、閾値未満なら無条件に悪化してよいという意味でもない。

<a id="contracts"></a>

## v3で決める契約と移行方針

publicな挙動を変更する前に、以下の設計判断を文書として残す。

| 判断対象 | 決めること | 判断時期 |
| --- | --- | --- |
| 結果・confidence | mappingか型付きresultか、unknown/判定保留、scoreの意味、language名、候補の同点処理 | 新しい結果APIの実装前。Betaまでに固定 |
| Streaming | `done`、終了後feed、finalize/reset、未完のmultibyte状態、chunk非依存性、error | 挙動比較の期待値をv3の契約にする前 |
| Resource・evidence | default `max_bytes`、切り詰めの通知、copyと寿命、GIL解放中の可変buffer、OOM | 制限やbuffer処理の変更前 |
| Hint・検出範囲 | 汎用とHTML/XMLの区別、metadata優先順位、不正/binary/混在encoding入力の扱い | hint APIまたはfallback方針の変更前 |
| Native境界 | 公開symbol、該当するABI version/SONAME、所有権、error code、Cythonとの結合 | native API変更と連携PRの前 |
| C++規格・安全性 | C++20を有力候補とした機能選定、RAII/借用view/型の方針、標準library・runtime条件 | 規格依存機能の導入前。各配布環境での検証を根拠に決める |
| Platform | Python/compiler/CMake最小版、architecture、free-threaded対応、packaging負担 | Beta前。偶然サポートを失わない |
| 新規fileのlicense | LGPL/MIT/Apache-2.0等の比較、component別の適用範囲、version・表記・contribution方針 | Phase 1のV3-01で着手。対象componentの新規実装・外部contribution受入れ前 |
| Data/model | format version、reader互換性、由来、配布条件 | model公開前。新規generatorのlicenseは実装前に決定 |
| Engine選択 | Rust試作の完了条件、両実装の維持cost、default engine | Phase 7の根拠が揃ってから |

破壊的変更ごとに、旧/新の例、影響する利用者、変換方法または代替API、変更されるversion、
理由、回帰検証、戻す方法を示す。
意味が曖昧な互換flagより、明確な移行を優先する。
低costでできるなら2.xでの非推奨化は有用だが、正当なv3変更の必須条件にはしない。

2.xへの新機能backportや無期限保守は本書では約束しない。Beta時点で保守期間を定義する。
2.3.0はbenchmark referenceとして固定し、結果やconfidenceの意味を永久に縛る仕様にはしない。

<a id="first-prs"></a>

## 最初の実装単位

各行はPRに分けて着手する単位の案とする。
nativeとwrapperで管理先が異なる場合は、依存関係を示した別PRに分ける。
現時点ではすべて未着手。本ロードマップPRと`dev`作成は、以下の実装完了には数えない。

| ID | 管理先 | 作業・成果物 | 受け入れ条件・依存関係 |
| --- | --- | --- | --- |
| [V3-01](https://github.com/PyYoshi/cChardet/issues/115) | 両repository | baseline棚卸し、両repositoryの`dev`のCI・Rules確認、新規fileのcomponent別license判断。既知の失敗・toolchain・model family・benchmark manifestと測定hashを記録 | 再現手順を記録。測定なしに性能効果を主張しない。新規実装前に対象licenseを決定 |
| [V3-02](https://github.com/PyYoshi/cChardet/issues/116) | 両repository、別PR | sanitizerとDebugの分離、build preset、C++20機能と配布互換性の検証、規格採用の設計判断 | GCC/Clang/MSVCとApple Clang、CMakeとCython経由で検証。最低対応runtimeでwheelを実行しsdist要件も記録。V3-01に依存 |
| [V3-03](https://github.com/PyYoshi/cChardet/issues/117) | uchardet | 機械可読なnative出力、比較harness、終了/lifecycle case | 同じfeedでの同等性とchunk間差分を分けて報告。V3-01 |
| [V3-04](https://github.com/PyYoshi/cChardet/issues/118) | uchardet | ASan/UBSan preset、上限付きfuzz target、回帰seed | 再現可能なsmoke実行と最小化入力の再検証。V3-02/03 |
| [V3-05](https://github.com/PyYoshi/cChardet/issues/119) | uchardet中心、必要に応じwrapper | Analyzer/tidyの既存指摘一覧、RAII・借用buffer・状態/値の型・compile時検証による安全性改善 | 小さなPRに分けて候補同等性とallocation/memory/latencyを検証。規格更新・判定のtuningと分ける。V3-02/03、安全性検証はV3-04も利用 |
| [V3-06](https://github.com/PyYoshi/cChardet/issues/120) | uchardet | 任意で有効化するprober/ranking trace | 代表的失敗を説明でき、無効時costを測定済み。V3-03 |
| [V3-07](https://github.com/PyYoshi/cChardet/issues/121) | uchardet | corpus manifest/分割schema、license一覧、validator | 権利情報欠落や分割を跨ぐ派生dataを拒否。V3-02と並行可能 |
| [V3-08](https://github.com/PyYoshi/cChardet/issues/122) | uchardet | offline strict再encode、正常境界でのsize生成、HTML生成 | 決定的hash、生成できなかった件数、data混入test。V3-07 |
| [V3-09](https://github.com/PyYoshi/cChardet/issues/123) | uchardet | legacy generatorの参考調査、新規offline generator・試作model・C++出力。旧script廃止は参照確認後に別PR | 決定性・再実行のべき等性・未使用dataでの品質を別々に検証。新規generatorのlicense決定済み。V3-01/07/08 |
| [V3-10](https://github.com/PyYoshi/cChardet/issues/124) | 両repository | 失敗report、top-k分析、coverage/ranking改善の優先順位 | 代表例を確認済みで、未参照holdoutがある。V3-03/06/08 |
| [V3-11](https://github.com/PyYoshi/cChardet/issues/125) | cChardet | 3.0範囲・契約の設計判断、移行案内の初版 | V3-10から測定可能な利用者向け改善を選ぶ。日程を満たすために範囲を捏造しない |
| [V3-12](https://github.com/PyYoshi/cChardet/issues/126) | 両repository、別PR | 選択した修正/model、submodule連携、report | 上記の基準、wheel/API test、意図した差分のレビュー。該当するV3-09/10/11 |

<a id="release"></a>

## リリース条件・リスク・進捗管理

### Alpha・Beta・正式版の条件

**Alpha**: Phase 1〜2の一連の工程が小さな対象で動き、選択した利用者向け改善を評価pipelineに
通せること。試験中・破壊的なAPIを明記し、未完了の項目も公開する。
Alpha公開を安定性の保証とはしない。

**Beta**: Phase 3で範囲を合意し、選択した機能が受け入れ基準を満たすこと。
publicな契約と移行例を固定し、corpus/modelの由来を確認済みとする。
対応platformと2.xの保守方針を文書化する。
HTML/CSV/streaming/threadingなど、代表的なdownstream利用をsmoke testへ加える。

**Release candidate・3.0**: 固定した評価と統制した性能測定を再現し、公開を妨げる安全性問題と
未説明の挙動回帰を解消する。
対応するwheelとsdistをinstallした状態で、型情報、CLI、free-threaded動作まで検証する。
code/model/corpusのrevisionと成果物を紐付ける。
release notesは直前のstableとの差分にし、2.xの機能を新機能として再掲しない。
[リリース手順](releasing.md)に従い、最初のAlpha前にprerelease用の手順も整備・検証する。

全corpusの置換、Rust、段階的検出、SIMDの完了を一律に3.0の条件にはしない。

### 主なリスクと対応

| リスク | 対応・再判断のきっかけ |
| --- | --- |
| 互換性が必要な改善を妨げる | v3の破壊的変更と移行記録を使う。3.0以後は次のmajorが必要か再評価 |
| 基盤を整えても明確な精度改善が出ない | 改善しなかった結果も公開し、label/traceを改善して範囲を見直す。benchmarkの見かけだけを良くしない |
| corpusの偏り・混入・正解の曖昧さ | source groupで分割、参照履歴、未使用holdout、確度を区別した指標 |
| corpusの消失・配布権不明・model由来不明 | 再配布を保留し、hash/recipeと不明点を保持。監査可能な置換を優先 |
| 新modelで速度・memoryが悪化 | modelごとのcostを報告し、根拠のある枝刈りを検討。正当化できない増分は採用しない |
| platformや浮動小数点計算による差 | compiler matrix、明示した契約、不一致の再現artifactを保存 |
| CI cost・Actions rate limit | local検証、まとめたpush、上限付きPR job、重い処理の定期実行 |
| Rust portだけが膨らむ | 小さな試作と比較判断を区切りにし、C++ referenceを維持 |
| 文書と実装が乖離する | 実装PRで完了の根拠と設計判断も更新 |

### 進捗の記録方法

GitHubでの作業は[cChardetのv3 Issue一覧](https://github.com/PyYoshi/cChardet/issues?q=is%3Aissue+label%3Av3)
へ集約し、[ロードマップ追跡Issue #114](https://github.com/PyYoshi/cChardet/issues/114)から
V3-01〜V3-12の子Issueと依存関係を確認できるようにする。
uchardet実装もここで追跡し、実装先repository・base branch・依存Issue・完了条件を明記する。
実装PRは対象Issueへリンクし、native側のmergeだけでPython連携まで完了したとは扱わない。
初期の作業は[「v3 基盤整備・スコープ確定」milestone](https://github.com/PyYoshi/cChardet/milestone/1)
にまとめ、期日は根拠が揃うまで設定しない。長期計画には既存stale設定の除外対象である
`pinned`ラベルを付け、未更新という理由だけで自動整理されないようにする。
Rust/SIMDなどの条件付き研究を3.0の必須作業として扱わない。

作業は未着手・進行中・blocked・延期・完了で管理する。
完了にはmerge済み実装、再現command、artifact hash、受け入れ条件の根拠への参照を必要とする。
blockerや延期理由は記録し、黙って完了条件を縮めない。

Phase 1終了時、最初の失敗report完成時、各リリース判定時に本書を見直す。
合意した方向性、提案中の閾値、試験的な選択肢、測定済みの結果を区別し、
範囲の変更と設計判断をGitの履歴で追跡できる状態を維持する。

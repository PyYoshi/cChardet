<!-- SPDX-License-Identifier: MIT -->
# V3-02: C++20配布互換性の検証

## 位置づけ

`CCHARDET_CXX_STANDARD=20`は開発者向けの明示的なbuild opt-inであり、
既定規格、対応Python、OS、runtimeの最低条件を変更しない。
未設定時は従来のGCC/Clang C++11、MSVC C++14を使う。
空文字列を含むその他の値はエラーとする。native CMake側の規格設定とは独立している。

同じExtensionにCython生成wrapperとuchardet sourceを渡すため、両方に規格が適用される。
`CXXFLAGS`で規格を渡す方法はsetuptools側の引数に上書きされ得るので使わない。
このopt-inでもユーザー独自compiler wrapper等の挙動は保証せず、実際のcompile logを確認する。

規格切替時は既存objectを再利用しないよう、新しいworktreeでbuildする。
以下はPOSIX shellの例。成果物と環境のパスは未使用のものを選ぶ。

```sh
uv venv /tmp/cchardet-cxx20-env --python 3.14
CCHARDET_CXX_STANDARD=20 uv build --wheel --verbose --out-dir /tmp/cchardet-cxx20-dist
uv pip install --python /tmp/cchardet-cxx20-env/bin/python /tmp/cchardet-cxx20-dist/*.whl
/tmp/cchardet-cxx20-env/bin/python tools/wheel_smoke.py
c++ -std=c++20 -Wall -Wextra -pedantic tools/cxx20_smoke.cpp -o /tmp/cchardet-cxx20-smoke
/tmp/cchardet-cxx20-smoke
```

standalone probeは`std::span`とRAII所有者をcompile/runする。
viewが所有者より長生きしない最小例であり、detectorの安全性の証明ではない。
MSVCでは`cl /std:c++20 /Zc:__cplusplus /EHsc tools/cxx20_smoke.cpp`に相当する。
probeをwheelやhot pathには組み込まない。

## 手動CIと採用gate

`C++20 wheel compatibility (opt-in)`は明示的な依頼時だけmatrixを実行する。
通常のpush、PR作成、commit追加（`synchronize`）では起動しない。
既存cibuildwheel設定を共有し、Linux・macOS・Windows、既存architecture、
Python 3.11〜3.14/3.14tを維持する。Linux containerへopt-inを明示的に転送する。
wheel smoke testとartifact保存を行うが、公開処理は持たない。
通常CIの必須checkを増やさず、masterのRulesも変更しない。

[GitHubの仕様](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_dispatch)
では`workflow_dispatch`のworkflowがdefault branchにも存在する必要がある。
この経路は将来用に維持するが、jobは`dev`のdispatchだけ許可する。
このためだけに`master`へworkflowを追加することはしない。

現在は、workflowを含む`dev`向けPRへ`v3-cxx20-validation` labelを付けて起動する。
[`pull_request`イベント](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#pull_request)
を使用するためdefault branchへのworkflow追加は不要で、Draft PRでも利用できる。
merge conflictのあるPRでは起動しない。forkからのPRにはGitHubの承認制限が適用され得る。
`pull_request_target`やwrite権限、公開credentialは使用せず、PRのmerge refを検証する。

- 対象はbaseが`dev`で、PR全体の差分に`.md`/`.rst`以外の変更があるもの。
- 検証したいcommitをpushした後、担当者が上記labelを明示的に付与する。
- 他labelの付与ではjobをskipする。すでに動いているmatrixもキャンセルしない。
- labelを残したままcommitを追加しても再実行しない。新しいcommitを検証する場合は
  labelを外して再付与する。同じcommitの一時的な失敗はActionsの再実行を使う。
- 再実行ボタンは元のrunのcommitを対象とするので、新しいcommitの検証には使わない。
- labelの有無だけでは検証済みと判断せず、merge前にrunのSHAと結果を確認する。

branch/path条件は[GitHubのfilter仕様](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#onpull_requestpull_request_targetbranchesbranches-ignore)
に従う。docs-only PRはlabelを付けても起動せず、通常CIの必須checkにも指定しない。

C++20を既定化する前に以下を確認する。

- 手動matrixの各build/test結果と、wrapper/native両方の実compile引数。
- manylinux repair結果・tag・依存symbolと対象runtimeでのimport。
- macOS deployment target・libc++の利用機能availabilityと両architecture。
- MSVC toolset・配布CRT条件、Windows wheelのimport。
- CPython 3.14tでGILを再有効化せず既存smoke testが成功すること。

native CMakeのcompiler matrix成功だけではPython wheelの条件を満たさない。
ローカルLinux wheelの成功もmanylinux互換性や他OS互換性を証明しない。
新しい標準library機能を本体へ導入する際は、規格フラグだけの検証とは別に再検証する。
現行環境の切り捨てが必要なら、既定化を保留して判断ログへ記録する。

## ローカル確認結果（2026-09-20）

- CPython 3.14.2、GCC 16.2.1、Cython 3.3.0、setuptools 84.0.0。
- uchardet `9ac0f79feefb0c58c11fb8ea1ca000c51f7d96f9`。
- fresh worktreeから`cp314-cp314-linux_x86_64` wheelをbuildし、独立uv環境へinstall。
- wrapperとnative sourceのcompile行末に`-std=c++20`があることを確認。
- installed wheel smoke成功、build設定10件と既存基本test15件が成功。
- ELF要求symbol versionは最大`GLIBC_2.14`、`GLIBCXX_3.4.21`、`CXXABI_1.3.9`。
  これは当該artifactの観測値であり、manylinux認証や最低環境の宣言ではない。
- このローカル確認時点では手動wheel matrixは未実行。後続のCI結果を以下に記録する。

## 配布matrixの確認結果（2026-09-20）

[専用run 35513146332](https://github.com/PyYoshi/cChardet/actions/runs/35513146332)は
3 OSすべて成功した。対象headは`87a69e3df6b1014f2b19b050103b14bbcd7a6c72`、
checkoutしたPR merge commitは`71508b9a5b741793b75ea9ec998f638541d5b9f2`。
後続の`7c20739`は分析toolとそのtestのファイル順序だけを修正しており、wheel source・
build設定・smoke入力は同じ。ただし後続SHA自体でこの専用matrixを実行したとは扱わない。

| OS | wheel数 | architecture | 実compile引数 | installed smoke |
| --- | ---: | --- | --- | --- |
| Linux | 10 | x86_64 / aarch64 | `-std=c++20` | 10成功 |
| macOS | 10 | x86_64 / arm64 | `-std=c++20` | 10成功 |
| Windows | 10 | win32 / win_amd64 | `/std:c++20 /Zc:__cplusplus` | 10成功 |

各OSでCPython 3.11〜3.14と3.14tを対象とした。wrapperとnative `uchardet.cpp`の
compile行をそれぞれ各10件確認した。3.14t両architectureのsmokeにはGILを再有効化
していないことのassertを含む。これは全APIの並列正当性を証明する試験ではない。

- Linux: manylinux_2_28 containerでbuild/testし、auditwheelが全10 wheelに
  `manylinux_2_24`と`manylinux_2_28`の両tagを付与した。
  2.24 runtimeで実行したわけではない。
- macOS: macOS 26.6.2 arm64 runnerでarm64をnative実行、x86_64を`arch -x86_64`で実行。
  arm64 tagは全て11_0。x86_64はcp311が10_9、cp312/313が10_13、cp314/314tが10_15。
  delocateによるarchitecture検証は成功したが、これら最低OSでの実行確認ではない。
- Windows: Windows Server 2025、Visual Studio 18、MSVC toolset path `14.51.36231`。
  `/MD`と3.14tの`Py_GIL_DISABLED=1`を確認。旧Windows・最低CRTでの実行確認ではない。

この結果で「現行配布workflowによるC++20指定buildとinstalled smoke」は確認できた。
最低runtimeの実行確認や今後追加する標準library機能のavailabilityは別gateとして残す。
既定規格・対応platformをこの結果だけで変更しない。

2026-09-21に[機能単位の独立probe](v3-reproducibility-results.md)を追加し、
native compiler matrixでspan / bit_cast / ranges等を確認した。
上記30 wheelは追加probeを組み込んだartifactの検証ではなく、最低runtime gateも残る。

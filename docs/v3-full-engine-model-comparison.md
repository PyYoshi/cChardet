<!-- SPDX-License-Identifier: MIT -->
# 生成モデルの候補競合評価

## 結論

Paris-only生成モデルは、今回の候補競合評価では既存モデルを置換する品質に達していない。
単一proberでの統計改善を、そのままdetectorの精度改善とは扱わない。
公開API・標準modelは変更せず、接続は非デフォルト実験targetに限定する。

## 条件

- [固定したtraining corpus](v3-spoken-training-corpus.md)の32録音から生成した
  identity/filteredモデルを使用し、今回の結果を使った再学習・parameter調整はしていない。
- [単一prober比較](v3-spoken-model-comparison.md)と同じ、未学習のParis validation
  16録音についてfull cp1252/UTF-8の32入力を使用する。全入力4 KiB以下。
- French Windows-1252の1 slotだけを差し替えるhybrid engine。
  French ISO-8859-1/15、他言語、UTF-8、rankingの実装は残す。
- 各入力をfresh detectorへone-shotで渡す。process上限10秒。
  大入力の停止調査やP01依存の実験は再開しない。
- 両生成buildの標準targetの候補・confidence bits・done観測が一致することを確認する。
- legacy trainingとの重複は不明。競合ライブラリとのbenchmarkでもない。

## 結果

各行16入力。exact codecはalias正規化後の先頭候補、decode-equivalentはstrict decode
した文字列が正解と一致する件数。encoding全体のsuperset関係は未評価。

| 入力 | model | exact codec | decode-equivalent | language一致 |
| --- | --- | ---: | ---: | ---: |
| cp1252 | legacy | 11 | 16 | 16 |
| cp1252 | identity | 0 | 5 | 16 |
| cp1252 | filtered | 3 | 7 | 16 |
| UTF-8 | legacy | 16 | 16 | 16 |
| UTF-8 | identity | 16 | 16 | 16 |
| UTF-8 | filtered | 16 | 16 | 16 |

cp1252入力ではidentityが16件すべてISO-8859-1を先頭に選択した。
filteredは3件でcp1252、13件でISO-8859-1を選択した。
decode自体は成功するが正解文字列と異なるものが、それぞれ11件・9件ある。
これは単なるencoding名のalias差ではない。

正解codecの候補内存在は、今回の入力ではexact codec件数と同じだった。
ただしこれはmodel欠落を意味しない。差し替えたcp1252 modelは存在するため、
group内部の選抜とconfidenceの競合を調べる必要がある。
単一proberのpair分類やconfidenceの改善だけを採用根拠にはできない。

実装上、`nsSBCSGroupProber::GetCandidates()`は1を返す。通常状態では
`GetConfidence()`がactiveなproberの最大confidenceだけを選び、同値では先のproberを
維持する。`eFoundIt`時は早期選抜となり、group confidenceは0.99になる。
したがって公開候補一覧は内部の全SBCS modelの順位表ではない。
これで候補不在をmodel欠落と解釈できない理由は説明できるが、各文書でどの分岐・
内部スコアが選択を決めたかは、この最終出力だけでは確定できない。

## 再現・次の判断

nativeの`models/experimental/ENGINE_PROBE.ja.md`の手順で、固定training artifactから
2つの実験buildを作り、`engine_comparison.py`でvalidation manifestを評価する。
reportには入力hash、候補順序、encoding/language、confidence bits、done観測、
build source・binary hashと集計を保持する。生corpus・生成modelはGitへ追加しない。
実装は[uchardet PR #39](https://github.com/PyYoshi/uchardet/pull/39)で11件のCI成功後、
devへ統合した。統合SHAは`e03915e00daa036e7f172bad9b395f485530d8f5`。

ローカルreport: `archives/v3-corpus/paris-full-engine-comparison-v1.json`。
content hash: `7b4695e8ff78effdeca177f71cf761081b46c64427ae8ad5c1d58de02e7e7265`。
file SHA-256: `79654809fe9985af4e89eac06aeb9d54af20001dc01301b70c4ceb7a6435a4ca`。
同じ固定入力・buildで2回実行し、report全体のバイト一致を確認した。

次は既存French ISO系modelとの競合過程を確認し、model coverageの問題と較正の問題を
分離する。このvalidationを調整用へ転用せず、調整する場合は別のtuning splitを用意する。
今回の結果だけからthresholdを動かしたり、他の候補を削除したりしない。

## 小規模1入力の内部観測

後続の原因調査として、既存`benchmark/uchardet-trace.cpp`をfiltered実験libraryへ
linkし、上記validationの先頭cp1252文書だけを10秒上限で観測した。
入力は2,473 bytes、SHA-256は
`272f13d8f2d9bb83f61c91b1dd698ff35182f3480e9005b5f45c5768822c4ea9`。
全失敗の原因をこの1件で代表させない。

feed後・end後ともSBCS groupは`detecting`だった。Frenchの3 modelはいずれも
306文字・246 frequent文字・193 sequenceを観測していた。

| model | category 0/1/2/3 | control文字 |
| --- | --- | ---: |
| 既存ISO-8859-1 | 0 / 0 / 6 / 187 | 5 |
| 既存ISO-8859-15 | 0 / 0 / 6 / 187 | 5 |
| 生成cp1252 (filtered) | 20 / 5 / 7 / 161 | 0 |

raw reportのISO-8859-1/frのconfidence bitsは`3f45eb28`で、保存済みC API観測の
先頭候補と一致した。ただしtraceのraw reportはC APIのsort/dedup後一覧ではない。
この照合を全候補の一致試験とは扱わない。

現行`nsSingleByteCharSetProber::GetConfidence()`のpositive approachは
`(positive + probable / 4 - negative * 4) / sequences / typical_ratio`を基礎とし、
さらにcontrol/out文字とfrequent文字の比率を掛ける。
今回の生成modelではnegative 20件の寄与がある一方、既存ISO系にはない。
encoding上のcontrol文字ペナルティだけでは、誤ったISO系候補を排除できていない。
これは次の較正分析の具体的な根拠であり、係数変更の正当化ではない。

観測source SHA-256は
`20099148d16425a079cc4bef795b50a8fdd5a0bbfa011c47122c71634ad19a84`、
観測実行file SHA-256は
`e9eb443b9cf1ea8fe5fdf8fb0aa713ca4e26499a729163de9329cb3d12f472fe`。
compileは`c++ -std=c++11 -O2 -Isrc/ext/uchardet/src`で、
`archives/v3-corpus/engine-paris-filtered-v1/build/src/liblibuchardet_experimental.a`
をlinkした。traceの引数は`0 INPUT_FILE`（one-shot）。model・入力を変更していない。

同じtraceと実験conformance実行fileを`UCHARDET_TRACE` / `UCHARDET_CONFORMANCE`に
指定し、`uv run --locked --offline --no-sync pytest -q tests/test_report_attribution.py`も
実行した（28 passed）。空入力・ASCII・既存の短い日本語fixtureを0/1/7-byte scheduleで
照合する9試験を含む。最終候補の値がraw reportに存在すること等の確認であり、内部rankingの
因果証明・全corpusの観測非干渉・精度向上の証明ではない。

## 選択cacheによる代表例の確認

[uchardet #45](https://github.com/PyYoshi/uchardet/pull/45)の読み取り専用traceで、
同じ2,473-byte入力と同じfiltered実験libraryを観測した。追加のconfidence/name
getterは呼んでいない。新fieldを除いた全snapshot/raw reportは旧traceと一致した。

finalize後のSBCSはdetecting、active数121、`cached_best_index=18`だった。
model統計との対応は18=ISO-8859-1/fr、19=ISO-8859-15/fr、20=生成cp1252/fr。
これにより、最終候補にcp1252がない理由をmodel欠落と解釈する余地を排除できる。

前節の実測counterと各modelの固定ratioを既存positive-approach式へ代入した。
下表は観測器による追加GetConfidence呼出しではなく、binary32丸めを入れた別計算。

| model | positive + probable/4 - negative×4 | ratio | 再計算score | float bits |
| --- | ---: | ---: | ---: | --- |
| ISO-8859-1 / ISO-8859-15 | 188.5 | 0.9990016222 | 0.7731194496 | `3f45eb28` |
| 生成cp1252 | 82.75 | 0.9603947997 | 0.3589009047 | `3eb7c1dc` |

ISO系scoreのbit列は実際のraw reportと一致する。両ISO modelはこの入力のcounterと
ratioが同一で、groupの走査は`bestConf < cf`でのみ更新するため、同点では先の18を維持する。
生成cp1252はnegative 20件による80の減点が大きく、control文字の減点がないことだけでは
逆転できない。SBCSは1候補のみを公開するため、内部にあるcp1252は候補一覧に残らない。

`DataEnd`ではconfidence照会の後に名前を取得してReportする。今回の正のscore、
選択cache、reportの一致を合わせて、この代表例は内部スコアによる選択と説明できる。
traceの汎用`selection_path`はdetecting時に`unknown`を維持する。任意のsnapshotでは
名前取得fallbackによるcache更新と区別できず、今回の根拠を全入力へ一般化しない。
また、これは生成model側の統計・較正の改善候補を示すもので、係数変更の採用承認ではない。

再現は前節のcompile commandでtrace sourceを#45版へ置き換え、同じstatic libraryと
入力を使う。入力hashは前節と同じ。生成modelは変更せず、独立holdoutは未開封。

- trace JSONL SHA-256: `d50b76a3c1c9e2f7f1636e468faf4ad69b0450c6a70332c338c2b630fd305c2d`
- 観測実行file SHA-256: `eda4b4bd4711c81f771eb48b82a7834bbd6f9917101201ca50e825c4650b7f26`

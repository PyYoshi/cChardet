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

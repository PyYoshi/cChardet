<!-- SPDX-License-Identifier: MIT -->
# v3 自走開発の実行計画

承認日: 2026-09-20。対象は[ロードマップ](v3-roadmap.md)のPhase 1〜3と改善試作。
全Phaseや3.0公開を今回の完了条件にしない。

## 権限と作業単位

- 両repositoryの`dev`へ、Draft PR、修正、CI確認、ready化、merge、Issue更新まで進める。
- `master`、uchardetのv2向け`cchardet`、tag、公開releaseは変更しない。
- 統合担当1名と最大3作業担当。担当別worktreeを使い、pushとmergeを統合担当へ集約する。
- nativeを先にmergeし、cChardet側で実際のcommit SHAを固定して統合検証する。
- ローカル検証後にpushをまとめる。性能測定中は他の重い作業を止める。

## 順序と成果物

| 段階 | Issue | 成果物 |
| --- | --- | --- |
| 0 | #115 | license適用表、baseline、既知の失敗、両devのCI/Rules |
| 1 | #116・#117・#121 | build、C++20互換性検証、候補比較、corpus schema/validator |
| 2 | #118〜#120・#122 | sanitizer/fuzz/静的解析、安全性改善、trace、strict corpus生成 |
| 3 | #123・#124 | 新規generator、再現性と品質の独立検証、失敗分類と優先順位 |
| 4 | #125・#126の一部 | 最大2件の非デフォルト改善試作、3.0採用案、判断一覧 |

依存する成果物の検証完了から着手できる。Phase全体の終了を待たない。
規格更新、安全性refactor、候補結果変更は別PRにする。C++20は既存配布環境で
成立してから採用し、platform切り捨ての判断中もRAII等の改善は続ける。
旧generatorの修復・再利用は前提にせず、由来と入出力のみ参考調査する。

## 固定した制約

- 独立した新規実装は[MIT方針](decisions/0001-new-component-license.md)を適用する。
- 外部取得は累計10 GiB、保存corpusと派生物は合計20 GiB。追加課金なし。
- 大きなdataはGit管理外の作業ディスクへ保存する。`/tmp`のRAM filesystemは使わない。
- 権利確認前のdataを組み込まない。Common Crawl raw contentを再配布しない。
- 元文書単位でtraining/tuning/validation/独立評価を分離する。派生物も分割を跨がせない。
- 試作は非デフォルトtargetとし、公開API・既存modelへ自動昇格させない。

## 検証と完了

候補数・順序・encoding・language・confidence・終了状態を比較する。
同一feedでの新旧比較とchunk間の差分は別に記録し、既存の不一致を隠さない。
ASan/UBSan、静的解析、時間上限付きfuzz、reset/reuse、異常入力を検証する。
生成物の決定性・べき等性・未使用data上の品質を別々に評価する。

native測定はI/Oを除外し、warm-up、affinity、compiler/flags、入力hashを記録する。
median性能5%超、p95/memory/allocation10%超の再現する悪化を調査する。
説明できない差分をmergeしない。Python競合比較ではrelease wheelとacceleratorの
実態を記録し、exact/compatible/decode-equivalentをcorpus別に公開する。

devはPR必須・削除/force-push保護とし、docs-onlyで省略するCIを必須checkにしない。
統合担当が該当するCIの成功を確認する。masterの必須checkは維持する。

判断待ちは影響する変更だけに限定し、[判断ログ](v3-decision-log.md)に根拠・選択肢・
推奨案・影響範囲・暫定措置を残す。独立作業を進めて終盤にまとめる。
権限・安全性・権利条件が不明な操作は実行しない。
独立作業が尽きた場合のみ、終盤前でも必要な判断をまとめて求める。

完了時は統合済み基盤、再現手順、baseline/比較結果、残る判断とIssueの実態を引き渡す。
#125/#126は試作だけで完了扱いにしない。

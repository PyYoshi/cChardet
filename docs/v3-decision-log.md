<!-- SPDX-License-Identifier: MIT -->
# v3 判断ログ

承認済みの権限・予算・license・並行数は[実行計画](v3-execution-plan.md)に記載する。
この一覧は「現在すべてがblockしている」という意味ではなく、判断が必要になる境界を示す。

| ID | 終盤の判断 | 必要な根拠 | 判断までの暫定措置 |
| --- | --- | --- | --- |
| D01 | 最低OS/runtime/Python条件の変更 | 配布matrixの失敗と代替案 | 既存条件を維持。非互換機能の採用のみ保留 |
| D02 | 公開API・既定値・候補順位/confidence変更 | corpus別差分、性能、移行案 | 現行semanticsを維持し非デフォルト試作で比較 |
| D03 | 試作modelと新規encodingの3.0採用 | 未使用data評価、coverage gap、性能 | 元の2件に固定block adapterを個別追加（下記）。標準modelを置換しない |
| D04 | 生成model等の権利条件 | source/generator/tableのprovenance | 未確認assetの取り込み・公開を保留 |
| D05 | 予算拡大 | 取得/保存の使用量と追加dataの価値 | 取得10 GiB・保存20 GiB・追加課金なし |
| D06 | masterへの反映とrelease | 受け入れ基準、CI、移行文書 | devまで。tag/public releaseを作らない |

新しい判断はID、発生条件、根拠、選択肢、推奨案、影響するIssue、暫定措置を追記する。
通常の実装選択は担当が検証して進める。未解決の権利や権限を推測して実行しない。

## D02/D03補足: 第3の非デフォルト試作（2026-09-22）

[Issue #125の提案](https://github.com/PyYoshi/cChardet/issues/125#issuecomment-5757938459)
に対する許可確認の後、maintainerから「再開して」と指示を受けた。
固定block native adapterを第3試作として追加する。既定動作・公開APIへの採用は別判断。
入力を同じ内部block列へ正規化するため、旧whole-inputの候補・confidenceが変わり得る。
同一内部blockでの外部chunk一貫性と、旧結果との差・精度・性能を別々に評価する。
P01保留・独立holdout未開封・既存2試作保存は維持する。
[初期結果と再開点](v3-fixed-block-pilot.md)。

## P01: 安全性検証の一部を保留（2026-09-20）

maintainer指示: 製品側の制限が繰り返される作業はpendingとしてskipし、独立作業を続行する。

- 対象: #118の追加fuzz/再現調査、#119の関連する安全性修正・検証。
- 理由: 安全性担当の応答が製品側の自動チェックで繰り返し停止した。
- 保存: local native `v3/safety-integration`の検証基盤と整数型修正は未push・未merge。
  元担当worktreeの未commit変更も削除せず保持する。
- 既存のsanitizer CIの成功と、追加fuzzの検証完了は別扱い。後者を成功と報告しない。
- 影響: 通常入力で停止が報告された大きなUTF-8入力の原因調査も保留する。
  この問題に依存するBOM試作の性能比較・採用判断は進めず、未測定とする。
- 続行: corpus/schema/generator、既存の小規模fixtureの分析、文書、検証済みPR統合。
- 再開条件: 対応可能な承認済み環境または人手での検証が用意され、maintainerが再開を指示する。

回避目的で別agent/modelへ同じ作業を振り替えない。#118/#119全体の完了条件は維持する。

<!-- SPDX-License-Identifier: MIT -->
# ADR 0001: 独立した新規componentはMITとする

状態: 承認済み（2026-09-20、maintainerの実行計画への回答）。

## 判断

独立して新規実装するtool、model generator、test、schema、開発文書にはMITを採用する。
file先頭に`SPDX-License-Identifier: MIT`を付け、適用するrepositoryにMIT全文を置く。
新規contributionも対象fileの条件を明示する。外部から転用したcodeを独立実装扱いにしない。

MIT、Apache-2.0、LGPLを候補としたうえで、独立した新規componentの利用と開発参加を
簡潔な条件に揃えるというmaintainerの選択を採用する。ライブラリ全体の再ライセンスではない。

| 対象 | 適用と確認 |
| --- | --- |
| 独立した新規tool/generator/test/schema/文書 | MIT。新規fileでも派生であれば以下を優先 |
| 既存code・改修・派生実装 | 元のlicenseとcopyright noticeを維持 |
| 既存model/state machine/table | 由来を維持。不明事項を新しいlicenseで上書きしない |
| Corpus | sourceごとの取得・加工・再配布条件を記録 |
| Generated model | corpus/generator/再利用tableの条件を別途確認。自動的にMITとしない |

rootのCOPYINGとPython packageの既存license metadataは変更しない。
MIT全文は[LICENSES/MIT.txt](../../LICENSES/MIT.txt)を参照する。
生成modelの配布条件が未確定なら当該modelの公開・標準採用だけを保留し、基盤開発を続ける。

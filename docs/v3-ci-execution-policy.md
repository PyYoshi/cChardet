<!-- SPDX-License-Identifier: MIT -->
# devのwheel CI重複実行を避ける方針

## 背景と変更

PRとmerge後のdev pushで、同じ3 OSのwheel matrixを繰り返していた。
たとえばPR #142のwheel runは35526469811、merge後は35527522837。
Actionsの実行量を減らし、同じ変更を短い間隔で再buildしないようにする。

`build-dev.yml`のpush triggerを削除する。
PRでは原則としてLinux/macOS/Windowsの全wheel matrixを実行する。
Python/ABI/architecture、smoke、共有build actionを縮小しない。
merge後も`test-dev.yml`のPython matrix、native sanitizer、distribution検証は残す。

| event | wheel | test |
| --- | --- | --- |
| dev向けcode PR | 全matrix | 従来どおり |
| dev向け`[skip-build]`付きPR | wheel jobをskip | 従来どおり |
| devへのmerge/push | 自動実行しない | 従来どおり |
| dev向けdocs-only PR/push | 自動実行しない | 自動実行しない |
| master・release tag | 変更なし | 変更なし |

devはPR必須・削除/force-push禁止のruleset
`Protect dev integration`（23727562）がactiveであることを確認した。
必須status check自体はdocs-only省略のため設定せず、統合担当が該当PRのCI成功を確認する。
rulesetやmasterの必須checkは変更しない。

PR対象headと実際のmerge結果が異なる変更を含む場合や、PRを経ない例外的なpushでは、
必要に応じてmerge後の明示wheel buildを実行する。PR成功が任意の将来commitの
wheel互換性を保証するわけではない。

## PRタイトルでの明示的な省略

dev向けPRタイトルに`[skip-build]`を含めると、wheel jobをmatrix展開前に省略する。
例: `[skip-build] ci: workflowの実行条件を整理`。
GitHub Actionsの`contains`は大文字小文字を区別しない。角括弧を含むmarkerを使い、
通常の文章にある`skip-build`だけでは省略しない。

Python test、native sanitizer、distribution検証は省略しない。
master向けPR、release tag、手動buildにはこの条件を適用しない。
workflow自体は起動し、wheel jobの結果は`skipped`となる。成功したwheel検証とは扱わない。

タイトルはPR作成前に設定するのが基本。判定はPRのopened/synchronize/reopened event時に行う。
タイトルや本文の編集だけでは新しいCIを起動せず、実行中のbuildも停止しない。
後からmarkerを変更した場合は次のpushまたはreopenで反映する。
これにより本文の追記や通常のタイトル修正による重い再buildを避ける。

build設定、native/Cythonコード、依存関係、配布対象の変更では原則markerを使わない。
CI運用や非配布tool等、wheel検証を省略する理由を説明できる場合に限定し、
PR本文に省略理由を残す。markerはレビューやdev保護ruleを迂回するものではない。

## 明示的なdev再build

既存のdefault branchにもある`build.yaml`のworkflow_dispatchを使う。
dev専用workflowをdefault branchへ追加する必要はない。

```sh
gh workflow run build.yaml --ref dev --repo PyYoshi/cChardet
```

これは利用者が必要と判断して実行するコマンド例であり、
この変更のために追加の手動buildを起動したわけではない。
明示dispatchは自動docs-only省略とは別である。
tag refではなくdevを指定し、release処理は起動しない。

## 検証範囲

構造testで、dev wheelのPR event、docs除外、3 OS matrix、共有action、
dev pushのtest維持、master/tag/manual eventの維持を確認する。
workflow構造の検証とGitHub上での実イベントの検証は別であり、
PR/merge後の実行状況も統合時に確認する。

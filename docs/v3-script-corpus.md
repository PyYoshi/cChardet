<!-- SPDX-License-Identifier: MIT -->
# Tatoeba追加script pilotと不足量

2026-09-21。既存の仏語・露語CC0 adapterに日本語・アラビア語・ヘブライ語の
公式CC0 exportを追加した。独立MIT toolの拡張であり、本文のCC0とは分けて扱う。

## 結果

| 言語 | available / selected | encoding | generated / skipped |
| --- | ---: | --- | ---: |
| 日本語 | 2 / 2 | UTF-8 / CP932 | 12 / 0 |
| アラビア語 | 2 / 2 | UTF-8 / CP1256 | 12 / 0 |
| ヘブライ語 | 27 / 27 | UTF-8 / CP1255 | 162 / 0 |

各言語200文を要求したが、snapshot全体がこの件数だった。
取得成功を十分なcoverageと扱わず、特に日本語・アラビア語の各2文は
モデル学習・代表的な精度評価には使えない。ヘブライ語27文も小規模pilotに留まる。
変換できた例だけを選んだわけではなく、全31文をID順で採用した結果である。

3 snapshotの圧縮転送量は合計1,783 bytes。本文はGitへ追加せず作業ディスクに保存。
別出力のingest/generateは全ファイルbyte一致し、従来fra/rusの再ingestも以前の出力と一致した。
5 manifest・431 source recordsの横断split監査が成功した。
翻訳関係を解決したわけではないため、全言語を共通origin `tatoeba:cc0-pilot` のvalidationへ保持する。

native予測・新しいmodel学習・独立holdout評価は行っていない。
候補出力、既定API、既存model、codec対応は変更していない。

## 再現

許可した5言語以外のexport、通常ライセンスのexport、任意URL、redirectは受け付けない。
新規取得だけがnetworkを使用する。取得済みsnapshotは再取得せずofflineで検証する。

```sh
uv run --no-project python src/ext/uchardet/corpus/sources/tatoeba.py \
  validate /disk/tatoeba-jpn-snapshot-1
uv run --no-project python src/ext/uchardet/corpus/sources/tatoeba.py \
  ingest /disk/tatoeba-jpn-snapshot-1 /disk/tatoeba-jpn-input-1 --limit 200
uv run --no-project python src/ext/uchardet/corpus/framework.py generate \
  /disk/tatoeba-jpn-input-1/config.json /disk/tatoeba-jpn-generated-1 \
  --failure-policy record-and-continue
```

snapshot hash、manifest content hash、件数はnative側の
[結果JSON](../src/ext/uchardet/corpus/sources/tatoeba-script-pilot-2026-09-21.json)、
取得と分割の契約は[日本語説明](../src/ext/uchardet/corpus/sources/TATOEBA.md)を参照する。
週次更新URLを固定revision扱いせず、実際の取得byteのhashで区別する。

## 次のsource選定への制約

- 今回のCC0 subsetだけで対象言語の評価を完了しない。
- 文書・著者・genreの多様性を持つ、別の権利確認済みsourceが必要。
- 通常exportへ無断で切り替えてライセンス条件を変えない。
- 採用順をnative予測やlegacy codecでの表現可否に依存させない。
- variant数と独立した元文章数を別に記録する。

この不足は #124 に残し、データ取得toolの完成だけで精度評価を完了扱いにしない。

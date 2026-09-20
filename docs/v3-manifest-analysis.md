<!-- SPDX-License-Identifier: MIT -->
# V3: manifestに基づくcorpus分析

`benchmarks.manifest_analysis`は生成corpusの内訳と評価対象の選択を記録する。
既定は棚卸しのみで、detectorは起動しない。リポジトリrootで実行する。

```sh
uv run python -m benchmarks.manifest_analysis \
  --manifest /path/to/corpus/manifest.json --max-input-bytes 1024
```

複数corpusは`--manifest`を繰り返す。schema・hash・実byteと再生成結果を検証し、
manifestをまたぐorigin/hashのsplit漏洩と重複manifestを拒否する。
この検証はholdoutを含むファイルを読み、再encodingするが、予測や精度評価はしない。
本文を読まないsplit監査だけが必要なら、uchardetの`corpus/framework.py audit-splits`を使う。

既定splitは`validation`、boundaryは`complete`のみ。
件数はcorpus・split・言語・encoding・encoding family・source kind・サイズ・形式別に出し、
対象外のsampleも除外理由付きで残す。予測結果を使って対象を選ぶ機能はない。
生成前にskipしたvariantはmanifestの`generation_report.counts`を別途掲載する。
旧manifestで記録がなければ`null`であり、skipゼロを意味しない。

## 評価の明示的な有効化

native conformance toolを使用する評価には`--native-tool`、
`--native-revision`、`--max-input-bytes`の3指定が必要。
`--split independent`の評価はさらに`--allow-independent-evaluation`が必要。
実行直前にも入力hashを確認し、実行失敗や不正な出力は評価全体をエラーにする。
失敗を誤判定やskipに変換して集計しない。

encodingのexact / compatible / decode-equivalent、language、両者の一致、
top-1/3/5を分ける。decode-equivalentは評価可能件数を別途出す。
判定基準は既存の`failure_analysis`を共有し、利用したchardetのversionを記録する。
candidate不在からmodel不在を断定することはできない。

## 観測分類と原因の分離

既存の `category` は互換維持し、新しい `cause_status` を別fieldで記録する。

| 観測 | `category` | `cause_status` |
| --- | --- | --- |
| 先頭候補がexact | `EXACT_MATCH` | `NOT_APPLICABLE` |
| compatibleまたはdecode-equivalent | `COMPATIBLE_OR_DECODE_EQUIVALENT` | `NOT_APPLICABLE` |
| 下位にexact候補がある | `RANKING_FAILURE` | `UNRESOLVED` |
| exact候補がない／候補ゼロ | `EXPECTED_CANDIDATE_ABSENT` / `NO_CANDIDATE` | `UNRESOLVED` |
| evaluator codec不在／入力・ラベル要確認 | 既存の対応category | `UNRESOLVED` |

上表の `NOT_APPLICABLE` は `expected_decodes: true` かつ
`evaluator_codec_available: true` の場合に限る。exactなencoding名が返っていても、
そのcodecで入力をstrict decodeできない／検証codecが利用できない／検証情報がない場合は
`UNRESOLVED` を維持する。既存のexact booleanやcategoryは変更しない。

`NOT_APPLICABLE` はこのencoding観測で原因分類を要求しないという意味であり、
language判定の正しさや一意なcodecの推定を保証しない。
`UNRESOLVED` は原因未確定であり、未対応encoding、model不在、confidence calibration失敗を意味しない。
たとえば下位候補の存在だけでは、重み・前処理・evidence不足のどれが原因かは決まらない。
根拠付きの原因確定を扱う別の機能は今回導入しない。observerが提供した原因statusもそのまま採用しない。

各評価済みinputの `samples[].prediction` に従来のcategory・candidate・top-kに加え、
原因statusと `expected_family` / `predicted_family` / `family_relation` を残す。
corpus hash・sample ID・source origin・サイズ・形式と結び付けて個別の観測を追跡できる。
評価しなかったinputにはpredictionを作らない。

## Encoding familyの定義と集計分母

mappingは `benchmarks/encoding_families.py` の明示表を正本とし、reportに
`family_mapping_version` を記録する。現行は `codec-family-v2`。
v1との違いと保存観測の再分析は[family mapping記録](v3-family-mapping.md)を参照する。
Python codec registryでaliasを正規化するため、`Windows-1251` と `cp1251` は同じcodecの集計になる。
reportには元encodingも保持し、正規化後は `canonical_encoding` に記録する。

familyは分析用の整理単位であり、文字集合の包含、decode互換性、detector対応状況ではない。
代表例は次の通り。完全な対応表は上記moduleに固定されている。

- UTF-8／UTF-16／UTF-32／UTF-7／ASCIIは別family。
- Shift_JIS・CP932・EUC-JP・ISO-2022-JPは `japanese`。
- GB2312・GBK・GB18030・HZと、Big5・Big5-HKSCS・CP950は別family。
- ISO-8859-5・Windows-1251等は `cyrillic`、ISO-8859-7・Windows-1253等は `greek`。
- Latin系もwestern・central-european・turkish等に明示分離する。
- 有効なPython codecでも表に未登録なら `unknown`。未知のラベルや候補不在も `unknown`。

`ISO` / `Windows` 等の名前prefixだけでfamilyを推測しない。
`SAME_FAMILY` は互換または正解ではなく、`DIFFERENT_FAMILY` も失敗原因ではない。
片側でもunknownなら `family_relation` は `UNKNOWN` とし、unknown同士の一致を正解扱いしない。

`groups` に `family:*`、`source_kind:*` と
`workload:<corpus_hash>:<source_kind>:<format>` の内訳を追加する。
各groupの分母は既存と同じ `available`（生成済みsample数）、`selected`（選択条件内）、
評価時のみ `evaluated`（実際に評価した数）を分ける。schema 1を維持した追加fieldである。
予測の集計には `cause_status:*` と `family_relation:*` の件数を追加するが、family accuracyは計算しない。
decode-equivalentは引き続き `decode_equivalent_evaluable` を分母とし、評価不能を誤判定にしない。
生成できなかったvariant数はcorpus単位の `generation_counts` に別掲し、sampleの分母へ混ぜない。

legacy fixtureの分析でも同じmappingと原因statusを使用する。
由来が不明なsource kindや形式は `unknown` とし、自然文・HTMLであると推測しない。
mappingや件数の追加はdetectorを変更せず、既存の正解判定にも影響しない。

## 保存済みlegacy観測の再分類（native実行なし）

既存の `failure_analysis` JSONを新しい集計形式へ再分類する場合は、次を使用できる。

```sh
uv run python -m benchmarks.failure_analysis \
  --observations /path/to/saved-legacy-report.json \
  --uchardet-corpus src/ext/uchardet/test
```

`--observations` と `--native-tool` は排他的。保存済み観測モードではsubprocessを起動せず、
native executableも読み込まない。`--native-revision` の上書き指定は禁止する。
従来のnative実行モードは `--native-tool` と `--native-revision` を引き続き使用する。

保存済みreportはschema 1の `uchardet-legacy` のみを受け付ける。
指定corpusの全fixtureと、sample数・相対pathの辞書順・byte長・SHA-256を照合する。
expected encoding／languageは従来と同じfixture path由来であり、保存済みlabelと一致すること、
`expected_label_source` が既存のlegacy由来記述であること、splitが `legacy-validation` であることも確認する。
不足・追加・並べ替え・別corpus・label変更・byte変更は停止し、合うsampleだけの部分集計は行わない。
holdoutやmanifest評価reportをこの経路へ混ぜない。

candidate順序とconfidence bitsを保存観測から引き継ぎ、現在のevaluatorでexact／compatible／
decode-equivalentと観測分類を再計算する。これは新しいnative性能・精度測定ではない。
入力reportに記録された `native_revision` と `tool_sha256` はそのまま保持する。
`observation_source` に元reportのhashと元evaluator情報（未記録ならnull）、
report直下に現在のevaluator versionとsample順序を明記する。
元reportのhashは追跡用であり、署名やnative toolの真正性を保証するものではない。
出力には再分類結果のみを含め、元の観測ファイルは変更しない。

入力上限は評価対象を選ぶ条件であり、長いsampleをその場で切断しない。
上限内であることはnative実装の安全性を証明しない。
[P01](v3-decision-log.md)の大入力native評価は保留のままとし、
今回のpilot集計は棚卸しのみ。独立holdoutの予測結果は取得しない。

### 2026-09-20のpilot棚卸し

Rust book翻訳由来の既存6manifest（仏・日・露、UTF-8と各legacy codec）を検証した。
全96sampleのうち、validationかつ1 KiB以下のcomplete variantは12件。
split対象外が72件、validationのサイズ対象外が12件。native評価は0件。
independent holdout 24件はすべて評価対象外であり、精度値は取得・公開していない。
この旧manifestには生成attemptの記録がないため、生成前skip件数は不明として扱う。

## 集計の限界

- 生成元のstrict再encodingはbyteの由来を説明するが、一意に推定できるcodecとは限らない。
- 同一書籍の翻訳・章分割は、独立著者や独立domainのcorpusではない。
- 選んだ小入力の成績を、対象外のサイズやsplitへ一般化しない。
- reportはcorpus本文を含まないが、manifest由来のpath・origin・hashを含む。公開前に確認する。
- metadataやsampleの改変を検出するための検証であり、未信頼corpusを実行するsandboxではない。

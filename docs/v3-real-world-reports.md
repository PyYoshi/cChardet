<!-- SPDX-License-Identifier: MIT -->
# 既存利用者報告から見た精度分析の入口

2026-09-21に既存Issue本文を確認した。これは現行devでの再現結果ではない。
添付fileの取得・corpusへの同梱・native予測はまだ行っていない。
French tuningの改善だけでreal-world全体の改善を主張しないため、別の分析対象を整理する。

| 報告 | workload / 申告 | 現時点で不足する根拠 | 次の検証 |
| --- | --- | --- | --- |
| [#101](https://github.com/PyYoshi/cChardet/issues/101) | text、期待Windows-1250、観測ISO-8859-2 | 本文にversionなし。元file bytes・文字列期待値の照合未実施 | 特に文字ごとのdecode差、source encoding根拠、現行候補一覧を確認 |
| [#102](https://github.com/PyYoshi/cChardet/issues/102) | CSV、2.1.7でBig5・confidence約0.99 | 期待値はWindows-1250/1251/1252のいずれかで、正解codec自体が未確定 | 作成元・言語・期待Unicodeを確定し、strict decodeと候補競合を分けて確認 |
| [#103](https://github.com/PyYoshi/cChardet/issues/103) | HTML、2.1.7でISO-8859-1、期待ISO-8859-15 | 添付HTMLのdeclaration・元bytes・現行再現未確認 | declarationを含む証拠、通貨記号のdecode差、候補内存在を確認 |

これら3件を発生頻度の推定やaccuracyの分母に使わない。古いversionの報告を
現行devの失敗件数へ加えたり、推測で解決済みにしたりしない。
候補不在だけでMODEL_MISSING、候補存在だけでRANKING_FAILUREとも判定しない。

## codec名の差と利用者の実害

Python codecで文字単位の対応を確認した。添付fileを再現したという意味ではない。

- `Ś`はcp1250では`8c`、ISO-8859-2では`a6`。両codecの名前を単純なaliasとして扱えない。
- `€`のISO-8859-15と`¤`のISO-8859-1は、どちらも`a4`。
  同じbyteがどちらでもdecode可能でも、結果のUnicode文字列は異なる。

したがって「decodeに成功した」を「正解」と同一視しない。
一方、byte `a4`だけから意図した文字を確定することもできない。
自然文の証拠、作成元、declaration等を分けて扱い、HTTP/HTMLの申告も無条件に正とはしない。
この区別は新model追加、ranking変更、将来のcontent hintのどれが必要か判断する前提になる。

再現例:

```python
assert "Ś".encode("cp1250") == bytes.fromhex("8c")
assert "Ś".encode("iso8859-2") == bytes.fromhex("a6")
assert "€".encode("iso8859-15") == "¤".encode("iso8859-1") == bytes.fromhex("a4")
assert bytes.fromhex("a4").decode("iso8859-15") != bytes.fromhex("a4").decode("iso8859-1")
```

## 取込前の条件

添付fileはIssueに公開されているだけで、corpusの再配布・training利用条件まで確認したとは
扱わない。取込前に許諾・provenanceとデータ範囲を確認し、本文をrepositoryへ転記しない。
許諾条件が不明な間はIssue URLと観測済みmetadataだけを参照する。
必要なら権利条件を明示できる独立fixtureを別に用意するが、元報告の再現とは呼ばない。

元bytesを検証できた場合も、期待Unicode、exact codec、compatible関係、decode-equivalentを
別fieldで記録する。#102のような未確定期待値を、都合のよいWindows codecへ決め打ちしない。
これらは分析の入口であって、追加model・heuristic・公開API変更の採用承認ではない。

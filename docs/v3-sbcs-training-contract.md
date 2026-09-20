<!-- SPDX-License-Identifier: MIT -->
# SBCS engineとtraining profileの接続前調査

調査対象はuchardet `1056e6018b6a785bb8bb4576c79255f3594b11cc`。
sourceの読み取りによる整理であり、新たなnative実行・filter移植・挙動変更は行っていない。
P01で保留した検証を再開するものではない。

## 結論

`SequenceModel`の構造に適合するtableを生成できても、そのtableが既存engineへ
適切に入力されるとは限らない。次の三点を分けて検証する必要がある。

1. **入力の同一性**: trainingで数えるbyte列と、proberへ渡るfilter後のbyte列。
2. **統計の同一性**: pairの分母、低頻度文字、記号・制御文字、文書/feed境界。
3. **評価の同一性**: confidenceの式、早期終了、他候補との順位。

現行Python profileは`identity-unfiltered-v1`、`NOT_ENGINE_CALIBRATED`であり、
この三点を満たしたとは主張しない。`keep_english_letters=true`だけで差を解消できない。

## 読み取った処理の流れ

参照先は固定revisionのsourceであり、下記は原文実装の転載ではなく観測対象の整理である。

- [SBCS groupのfeed](https://github.com/PyYoshi/uchardet/blob/1056e6018b6a785bb8bb4576c79255f3594b11cc/src/nsSBCSGroupProber.cpp#L310):
  各modelのkeepEnglishLetterにかかわらず、共通の`FilterWithoutEnglishLettersToBuffer`を使う。
  filter結果が空ならchildへfeedしない。activeなchildへ順に渡し、foundでgroupの処理を打ち切る。
- [filter](https://github.com/PyYoshi/uchardet/blob/1056e6018b6a785bb8bb4576c79255f3594b11cc/src/nsCharSetProber.cpp#L53):
  ASCII letter以外のASCII byteを区切りとし、高位bitを持つbyteを含む区間を残す。
  残した区間の終端delimiterは空白へ置換する。ASCII-onlyの区間は残さない。
  Unicodeの単語分割や言語判定をしているわけではない。
- [単一byte proberのfeed](https://github.com/PyYoshi/uchardet/blob/1056e6018b6a785bb8bb4576c79255f3594b11cc/src/nsSBCharSetProber.cpp#L41):
  filter後のbyteをorderへ写し、頻出文字同士はmatrixを参照する。
  低頻度文字を含むletter領域のpairはnegativeへ加算される。
  特殊orderは通常の頻出文字pairと同じ扱いではない。
- [resetとconfidence](https://github.com/PyYoshi/uchardet/blob/1056e6018b6a785bb8bb4576c79255f3594b11cc/src/nsSBCharSetProber.cpp#L107):
  resetは直前orderと累積統計を初期化する。通常のfeed間では直前orderを保持する。
  confidenceはpositiveだけでなくprobable・negative・低頻度文字・制御文字の統計も使用する。
  これをtraining時のpositive比率一つで較正できるとは限らない。

## 境界で区別するもの

| 境界 | sourceから読み取れる性質 | 接続時の確認事項 |
| --- | --- | --- |
| filter呼び出し | 区間先頭と高位bit遭遇flagは呼び出しごとのlocal変数 | 全文filterと分割filterを同一視しない |
| proberのfeed | 直前orderを次のfeedへ保持 | chunk境界が自動的な文書境界になるとは扱わない |
| 文書/reset | resetで直前order・累積統計を初期化 | corpus集計で文書間pairを作らない |
| 判定終了 | 一定量のpair後にconfidenceによるfound/reject判定がある | 全文統計と実際に消費したevidenceを分ける |

この表は実行結果ではない。とくにchunkによる差分量、最終candidateへの影響、
精度・速度への影響は未測定。chunking方針を暗黙に修正した互換trainerを作らない。

## profileと既存engineを比較するための次のgate

- まずone-shotの入力契約を固定し、全文をfilterしたtrainingとidentity trainingを別profileにする。
- filter済みbyteのhash、文字数、頻出/低頻度/特殊order、pair分母を独立して比較する。
- filter互換を必要とする実装は既存sourceの由来・licenseを保持する。Pythonへ移しただけで
  独立MIT実装と主張しない。移植と新しいfilter仕様は別変更にする。
- `mTypicalPositiveRatio`の分子・分母、probable/negativeの重み、早期終了時の状態を記録する。
- native接続後に同じ入力/同じfeedで既存modelと比較する。chunk間比較は別reportにする。
- 未使用dataの評価と性能比較を通すまで、生成modelを標準登録しない。

実装やnative検証の着手条件は[P01と判断ログ](v3-decision-log.md)、
採用条件は[採用gate](v3-adoption-gates.md)に従う。ここでは較正方法や公開API変更を決定しない。

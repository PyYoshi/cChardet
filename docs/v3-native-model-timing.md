<!-- SPDX-License-Identifier: MIT -->
# 単一モデルの native 処理コスト

2026-09-21。[uchardet #35](https://github.com/PyYoshi/uchardet/pull/35) の
[計測tool](../src/ext/uchardet/models/experimental/MODEL_TIMING.ja.md)を使用した。
全detectorやPython APIではなく、同じ入力を繰り返す単一proberのreuse処理を測る。

native PR #35は11件のCI成功を確認してdevへ統合済み
（commit `61930cc23e9dd04434ad784dd73923e3775ae804`）。
cChardet側の参照更新後、native library/filter toolを指定したローカルpytestは
304 passed、27 skipped、76 subtests passed。skipを検証済みとは扱わない。

## 条件

- Paris Stories validationのfull cp1252 16文書（raw合計40,777 bytes、各1〜4 KiB未満）
- 前回と同じlegacy/identity/filteredモデル。再学習やthreshold調整なし
- CPU2に固定、各文書20,000反復 × 7試行、独立した3 run
- C++ steady_clock、128 warm-up、モデル実行順を文書・試行ごとに循環
- 区間内: reset + filter + feed + confidence + checksum
- 区間外: 入力I/O、Python、process起動、コンパイル、入力/scratch/prober確保、JSON出力
- 各試行の最終観測は非計測時と一致。checksumもconfidence bits × 反復数と一致

host実測: AMD Ryzen 7 8845HS、Linux `7.2.4-202.nobara.fc44.x86_64`、
governorは前後ともpowersave。affinityはCPU占有や周波数固定を保証しない。
測定中にこちらから別のbuild/testは実行していないが、host全体のbackground負荷やSMT相方は
制御していない。これらを固定条件と偽らない。

## 結果

下表は、独立した文書別の試行時間を合計し、反復数で割った値のmedian（µs）。
16文書を交互に処理するcorpus passの実測値ではなく、cacheが温まった文書別計時の合計。

| run | legacy | identity | filtered |
| --- | ---: | ---: | ---: |
| 1 | 49.748 | 49.357 | 49.463 |
| 2 | 49.776 | 49.260 | 49.413 |
| 3 | 49.687 | 49.311 | 49.417 |

差は約1%以内（最大でidentityの−1.04%）で、意味のある高速化とは主張しない。
全3 run・全16文書で、文書別medianにlegacy比5%超の悪化はなかった。

### 末尾側の変動

run2のsource `paris-fr-485411558ce4ace208c63bad29a00f16ad06b158701da4f53ee86da243a6acfc` は、
identityの試行平均p95がlegacyより12.12%高かった。7試行のため、このp95は最大試行に相当する。
identityの他6試行は約52.2〜52.5 ms、該当試行だけ58.962 ms（各20,000反復）。
このデータは除外していない。run1/3では同じ10%超の悪化は再現しなかった。
原因をOS scheduling等へ断定できる観測はなく、「不具合なし」の証明とも扱わない。

ここでのp95は**試行平均のp95**であり、個々のリクエストのp95 latencyではない。
したがって実行計画のtail-latency/memory/allocation gateを全て通過したとは主張しない。

## 再現

native commit `d78550f`、wrapper GCC 16.2.1 C++11/O2、Python 3.14.2。
libraryは既存GCC Release buildで、SHA-256:
`cbfafc66f7aeb38952991b0fe3a621b6abf47aedf12bbc8eda3541908f28649a`。
input/modelの由来は[既存モデル比較](v3-legacy-model-comparison.md)と同じ。

```sh
taskset -c 2 uv run --no-project python models/experimental/model_timing.py \
  /disk/filter-comparison-identity-fr-v1.json /disk/filtered-training-fr-v1.json \
  /disk/paris-stories-generated-1/manifest.json /disk/native-build/src/libuchardet.a \
  /disk/timing-run1.json --iterations 20000 --repeats 7
```

同じcommandで出力名を変えてrun2/3を測る。時間は変動するため、reportの全byte一致を
再現性条件にはしない。生の全試行と環境・compiler/model/inputのhashを残す。

| run | content hash | file SHA-256 |
| --- | --- | --- |
| 1 | `808b892e31d78b27d0f6c9da96c4952851e8631f5d970858decdbbb35fe07a6b` | `d34f1734505ecf8c3ddf88ce7bcebbd143c5dc3b36c3ff2b1e4d701eddb4bbea` |
| 2 | `eedd3f436c6f2c589826a08909faec7030d4b0bbdd4972f576c6702ea9c3e327` | `65bfa7519173febc1d9128ef35e876eac2ec4eb56826b812e977c383747b495e` |
| 3 | `e8f10549bf63b190fc8860768f5fc5f4ce01f5757179df454767b328f3a643a4` | `71f5ef2bab8faf8ea1250041a6d7467d220ee8ba0d100bc4dd29539ec210e930` |

生reportはGit管理外に保持する。allocation数・memory・異なる文書の連続処理・並列性能・
全detectorのthroughputは未測定。結果は新規modelの品質や採用を保証せず、P01も再開しない。

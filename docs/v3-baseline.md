<!-- SPDX-License-Identifier: MIT -->
# v3 開発開始時baseline

確認日: 2026-09-20。native `7993e0afe3b6c64f0ea3b43c7d4987118f6c5c12`、
cChardet `44792642a96490e464b922d3d868a63cabc2707c`。これは改善前の再測定であり、
過去releaseとの高速化率を新たに主張するものではない。

## 環境・再現

Linux x86_64、GCC 16.2.1、CMake 4.3.0、Clang 22.1.8、uv 0.9.26。
Release、static library、`-O3 -DNDEBUG -msse2 -mfpmath=sse`、CPU affinityは論理CPU 2。
並行担当の重い処理を停止して測定した。専用物理hostの独占やfrequency固定は保証していない。

```sh
cmake -S src/ext/uchardet -B /tmp/cchardet-v3-reference \
  -DCMAKE_POLICY_VERSION_MINIMUM=3.5 -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_SHARED_LIBS=OFF -DBUILD_BINARY=OFF -DBUILD_BENCHMARK=ON
cmake --build /tmp/cchardet-v3-reference --parallel 4
ctest --test-dir /tmp/cchardet-v3-reference --output-on-failure
uv run --locked python tools/v3_baseline.py \
  --build /tmp/cchardet-v3-reference --cpu 2 --benchmark --iterations 100
```

記録toolはfixture/modelごとのhash、CMake cache、native commit/dirty状態、binary hash、
affinityと全timingをJSONで出力する。比較時は実際に使うcompilerのversionも別途記録する。
fixture一覧は固定native commitから再生成できる。集約manifest SHA-256:
`08440bc828ded1dfa11121c731abef1d174b7da4f53c20640bab03cf00704896`。

## 結果

158 fixture、合計91,581 bytesの一巡あたりmedian。各100回、I/O除外、native C API直接呼出し。
tool内warm-up 3回に加えて測定前processを1回実行した。

| detector | whole-input | 64-byte chunk |
| --- | ---: | ---: |
| fresh | 30.2730 ms | 33.5110 ms |
| reuse | 25.7865 ms | 28.8542 ms |

[全sampleとbinary hash](benchmarks/v3-reference-2026-09-20.json)。
これは小さな既存fixtureの結果であり、数KiB〜数百KiBの実運用分布や独立精度評価を代表しない。

CTestは153/153成功。ただし登録対象から次の5組が除外されている。
除外理由は既存CMakeの「未対応または精度不足」という記述であり、今回原因を再分類したものではない。

- `ja:utf-16le`、`ja:utf-16be`
- `es:iso-8859-15`、`da:iso-8859-1`、`he:iso-8859-8`

全158 fixtureをbenchmarkへ含め、除外5組を測定母数から落としていない。

## modelと旧generatorの棚卸し

`src/LangModels`には38個のC++ model fileがある。この数は対応codec数や言語精度を意味しない。
既存のlicense headerを維持し、元corpus revision/hash不明は不明のまま扱う。
たとえばFrench modelにはgenerator名と2022-12-14の生成時刻があるが、corpusを再構成する情報ではない。

旧`script/README`はWikipediaからsingle-byte language/charset組のmodel生成を説明する。
`BuildLangModel.py`はonline取得、`random.shuffle`、生成source内の現在時刻を使用する。
これらは固定入力・固定出力pipelineから切り離すべき要素である。
maintainerが過去に確認したべき等性・品質問題は過去の観測として記録し、今回再現済みとはしない。
旧scriptの修復やWikipedia再取得を新generator着手の条件にしない。

## GitHub運用

両devへPR必須・削除/force-push禁止を設定済み。
cChardet Rules ID `23727562`、uchardet `23727563`。bypassなし。
docs-only省略と両立するため必須status checkは設定せず、統合担当が該当CIを確認する。
masterの既存Rules `23382292`は変更していない。

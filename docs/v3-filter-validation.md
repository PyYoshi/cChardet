<!-- SPDX-License-Identifier: MIT -->
# 会話validationでのSBCS filter入力差

2026-09-21。[開発用filter診断](v3-filter-profile.md)を既存Paris Stories validationへ適用した。
detectorの候補生成・精度評価・model再学習・独立holdout予測ではない。

## 対象と固定点

- [既存corpusの出典・license・取得手順](v3-spoken-corpus.md)を維持。新規取得なし。
- validationのフランス語16録音を元にした、完全版cp1252 textだけを選択。
- 各文書は1,024以上4,096未満のbytes。HTML/サイズvariantを重複計上しない。
- manifest content hash: `6340aff3b3d424fced87b782d75036c64152b4840eec98a05dc9a5b4f90216aa`
- native revision: `17f0cf4508e9c60f96c5ce9c02de69e4b1d118a6`
- GCC16 Release診断binary SHA-256: `b69fedd1aca1c89d32e8e5b6387f3375920d828468afcd2c91917951ffd2c42a`
- 下記script SHA-256: `499b5e1f1792ee5abd88332e58e6051f9c2c1b9a4977a691698ca04159d4ef0e`
- report SHA-256: `3327de29d166334b414935bb59edac52e7c29cb78df8ec47fe2e11e612f91f73`
- Python: uv管理のCPython 3.14.2

manifestのsourceがすべてvalidation/frであることを本文アクセス前に確認した。
frameworkでsource/sample本文とhashを再検証し、source hash/origin重複も拒否した。
元byteの頻度と隣接pairはPythonでも数え、各native出力のraw側と一致を確認した。

## 集計結果

元入力は全chunk条件で合計40,777 bytes、文書内の隣接byte pairは40,761組。

| feed chunk | filter後bytes | filter後pair数 | 全文filterと統計が異なる文書 |
| --- | ---: | ---: | ---: |
| 全文（0） | 5,876 | 5,860 | 0 / 16 |
| 1 byte | 1,076 | 1,060 | 16 / 16 |
| 7 bytes | 4,150 | 4,134 | 16 / 16 |
| 64 bytes | 5,684 | 5,668 | 16 / 16 |
| 1,024 bytes | 5,869 | 5,853 | 4 / 16 |

各文書でfilter出力を連結した列の統計を求め、そのcountsを足した。
文書を跨ぐpairは含めない。統計の一致はbyte順序の完全一致を証明しない。
「異なる文書」はbytes/symbols/pairsの比較であり、候補やencodingが異なる件数ではない。

別出力先へ再実行したreportもbyte一致し、同じSHA-256だった。
文書別の詳細な頻度tableは入力由来の情報を含むためGitへ同梱せず、
`archives/v3-corpus/paris-filter-profile-v1{,-repeat}.json`に保持した。
公開するのはこの集計と再現scriptであり、新しい配布modelではない。

## 解釈

identity trainingとSBCS filter後の入力は、このcorpusでは証拠量が大きく異なる。
また、chunkによる差は短い人工例だけでなく文書単位でも観測された。
そのため、元byteのcountsから生成したratioをそのままengineのconfidenceに対応づけない。

ただしfilter後のbyte pairはmodelの文字orderやsequence分母ではない。
proberのactive状態や早期終了も実行していないので、実detectorが実際に消費した統計とは
断定しない。chunk不一致の修正、filter仕様変更、較正方法の採用は行っていない。
単一domain・言語の16文書から一般的な精度やWeb分布を推定しない。

## 再現

既存corpusを指定hashで生成し、固定native revisionで診断targetをbuildする。
以下を `/disk/paris-filter-profile.py` として保存し、sourceとbinary hashを確認する。
scriptは今回の固定manifest専用で、任意corpusを受け入れる汎用評価toolではない。
assertを有効にして実行し、`python -O`は使わない。

```sh
uv run --locked --offline --no-sync python /disk/paris-filter-profile.py \
  /path/to/cChardet /path/to/uchardet-filter-profile \
  /disk/paris-filter-profile-v1.json
```

binary hashもreportへ含むため、別buildでbinaryのbyteが変わる場合はreport hashも変わる。
その場合は上の集計・文書別countsを比較し、同一binaryでの再実行と混同しない。

```python
# SPDX-License-Identifier: MIT
"""Fixed validation-only input statistics; no detector/model execution."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys

root, executable, output = map(Path, sys.argv[1:])
sys.path.insert(0, str(root / "src/ext/uchardet/corpus"))
import framework
from artifact import write_idempotent

manifest_path = root / "archives/v3-corpus/paris-stories-generated-1/manifest.json"
manifest = json.loads(manifest_path.read_text())
assert manifest["content_hash"] == "6340aff3b3d424fced87b782d75036c64152b4840eec98a05dc9a5b4f90216aa"
assert all(s["split"] == "validation" and s["language"] == "fr" for s in manifest["sources"])
framework.validate(manifest, manifest_path.parent)
samples = [s for s in manifest["samples"] if s["encoding"] == "cp1252"
           and s["format"] == "text" and s["boundary"] == "complete" and s["byte_limit"] is None]
assert len(samples) == 16 and len({s["source_id"] for s in samples}) == 16
assert len({s["sha256"] for s in manifest["sources"]}) == 16
assert len({s["origin"] for s in manifest["sources"]}) == 16
documents = []
for sample in sorted(samples, key=lambda s: s["id"]):
    path = framework.safe_path(manifest_path.parent, sample["path"])
    data = path.read_bytes()
    assert 1024 <= len(data) < 4096
    pairs = Counter(zip(data, data[1:]))
    expected = dict(bytes=len(data), symbols=[data.count(i) for i in range(256)],
                    pairs=[[a, b, n] for (a, b), n in sorted(pairs.items())])
    observations = {}
    for chunk in (0, 1, 7, 64, 1024):
        result = subprocess.run([str(executable), str(chunk), str(path)],
                                capture_output=True, text=True, check=True, timeout=10)
        observed = json.loads(result.stdout)
        assert observed["schema"] == "sbcs-filter-profile-v1"
        assert observed["chunk_size"] == chunk and observed["raw"] == expected
        filtered = observed["filtered"]
        assert sum(filtered["symbols"]) == filtered["bytes"] <= len(data)
        assert sum(n for _, _, n in filtered["pairs"]) == max(0, filtered["bytes"] - 1)
        assert sum(a for a, _ in observed["calls"]) == len(data)
        assert sum(b for _, b in observed["calls"]) == filtered["bytes"]
        observations[str(chunk)] = observed
    documents.append(dict(sample_id=sample["id"], sample_sha256=sample["sha256"], observations=observations))
summary = {}
for chunk in (0, 1, 7, 64, 1024):
    records = [d["observations"][str(chunk)] for d in documents]
    summary[str(chunk)] = dict(
        documents=len(records), raw_bytes=sum(r["raw"]["bytes"] for r in records),
        filtered_bytes=sum(r["filtered"]["bytes"] for r in records),
        raw_pairs=sum(sum(n for _, _, n in r["raw"]["pairs"]) for r in records),
        filtered_pairs=sum(sum(n for _, _, n in r["filtered"]["pairs"]) for r in records),
        different_from_whole=sum(d["observations"][str(chunk)]["filtered"] != d["observations"]["0"]["filtered"] for d in documents),
    )
report = dict(schema="paris-filter-profile-observation-v1", manifest_hash=manifest["content_hash"],
              binary_sha256=hashlib.sha256(executable.read_bytes()).hexdigest(),
              script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              native_revision="17f0cf4508e9c60f96c5ce9c02de69e4b1d118a6",
              documents=documents, summary=summary)
encoded = (json.dumps(report, sort_keys=True, indent=2) + "\n").encode()
write_idempotent(output, encoded)
print(json.dumps(dict(summary=summary, report_sha256=hashlib.sha256(encoded).hexdigest()), sort_keys=True))
```

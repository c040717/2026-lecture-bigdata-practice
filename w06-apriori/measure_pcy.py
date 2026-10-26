"""버킷 수와 데이터 크기를 바꾸어 실제 추가 할당량을 비교한다."""
import gc
import json
from pathlib import Path
import time
import tracemalloc
from datetime import datetime

import bench
from task3_pcy import PlainApriori, YourAlgorithm


def measure(algo, baskets):
    gc.collect()
    tracemalloc.start()
    start = time.perf_counter()
    pairs = algo.run(baskets)
    elapsed = time.perf_counter() - start
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    result = {"baskets": len(baskets), "support": algo.support,
              "pairs": len(pairs), "peak_counters": algo.peak_counters,
              "peak_bytes": peak_bytes, "seconds": elapsed}
    if isinstance(algo, YourAlgorithm):
        result.update({"bucket_count": algo.bucket_count, "bucket_bytes": algo.bucket_bytes,
                       "bitmap_bytes": algo.bitmap_bytes, "frequent_buckets": algo.frequent_buckets})
    return pairs, result


def main():
    path = Path(__file__).parent / "out" / "pcy_memory.json"
    if path.exists():
        raise FileExistsError("Keep the previous pcy_memory.json separately before rerunning.")
    baskets = bench.build()
    report = {"config": {"items": bench.ITEMS, "baskets": bench.BASKETS,
                         "avg": bench.AVG, "seed": bench.SEED, "support": bench.SUPPORT},
              "measured_at": datetime.now().astimezone().isoformat(timespec="seconds"),
              "memory_scope": "tracemalloc peak during run, including output; input baskets excluded",
              "crossover": [], "bucket_comparison": []}
    for size in (500, 1000, 2000, 4000, 8000, 20000):
        sample = baskets[:size]
        base_pairs, baseline = measure(PlainApriori(bench.SUPPORT), sample)
        pcy_pairs, pcy = measure(YourAlgorithm(bench.SUPPORT), sample)
        assert pcy_pairs == base_pairs
        row = {"baseline": baseline, "pcy": pcy, "counts_equal": True}
        report["crossover"].append(row)
        if size == 20000:
            report["bucket_comparison"].append(pcy)
            for buckets in (65536, 4096):
                smaller_pairs, smaller = measure(YourAlgorithm(bench.SUPPORT, buckets), sample)
                assert smaller_pairs == base_pairs
                smaller["counts_equal"] = True
                report["bucket_comparison"].append(smaller)
                del smaller_pairs
        del base_pairs, pcy_pairs
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"{size} baskets: baseline {baseline['peak_bytes']} bytes, PCY {pcy['peak_bytes']} bytes", flush=True)


if __name__ == "__main__":
    main()

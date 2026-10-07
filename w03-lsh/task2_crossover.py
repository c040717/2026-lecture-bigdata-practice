#!/usr/bin/env python3
"""Week 3 · Task 2 — Find the crossover on your own machine.

Textbook §3.4.

Everybody knows brute force is quadratic and LSH is not. That is not the
interesting question. The interesting question is **where, on the machine in
front of you, does it start to matter** - and that answer is yours alone. It
depends on your CPU, your memory, and how big your shingle sets are.

This script gives you the timing loop. The two methods are yours: import them
from Task 1 and Task 3.

    python3 task2_crossover.py --sizes 500,1000,2000,4000
    python3 task2_crossover.py --sizes 8000,16000          # keep going

Write down where it hurts. That is the deliverable.
"""
import argparse, json, os, platform, random, time, tracemalloc
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")


def machine(background):
    info = {
        "platform": platform.platform(),
        "processor": platform.processor() or platform.machine(),
        "python": platform.python_version(),
        "background_workload": background,
    }
    if os.name == "nt":
        import ctypes
        import winreg

        class MemoryStatus(ctypes.Structure):
            _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong)] + [
                (field, ctypes.c_ulonglong) for field in
                ("total_physical", "available_physical", "total_pagefile",
                 "available_pagefile", "total_virtual", "available_virtual",
                 "available_extended")]

        status = MemoryStatus()
        status.length = ctypes.sizeof(status)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            info["ram_bytes"] = status.total_physical
            info["ram_gib"] = round(status.total_physical / 1024 ** 3, 2)
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                            r"HARDWARE\DESCRIPTION\System\CentralProcessor\0") as key:
            info["processor"] = winreg.QueryValueEx(key, "ProcessorNameString")[0].strip()
    elif hasattr(os, "sysconf"):
        try:
            info["ram_bytes"] = os.sysconf("SC_PHYS_PAGES") * os.sysconf("SC_PAGE_SIZE")
            info["ram_gib"] = round(info["ram_bytes"] / 1024 ** 3, 2)
        except (ValueError, OSError):
            pass
    return info


def build_documents(n, seed=246):
    """기존 벤치마크의 생성 방식을 사용해 실험에 필요한 n개 문서를 만든다.

    bench.build()는 항상 2,120개만 반환하므로 여기서 데이터를 생성한다.
    Task 3의 bench.py는 수정하지 않는다.
    """
    import bench
    if n <= 0:
        raise ValueError("document counts must be positive")
    rng = random.Random(seed)
    planted = min(bench.PLANTED, n // 10)
    base_count = n - planted
    docs = [set(rng.sample(range(bench.VOCAB), bench.SHINGLES))
            for _ in range(base_count)]
    for _ in range(planted):
        clone = set(docs[rng.randrange(base_count)])
        for _ in range(rng.randint(4, 14)):
            clone.discard(rng.choice(list(clone)))
            clone.add(rng.randrange(bench.VOCAB))
        docs.append(clone)
    rng.shuffle(docs)
    return docs


def timed(fn, *args):
    """Wall time and peak memory of one call."""
    tracemalloc.start()
    t0 = time.perf_counter()
    cpu0 = time.process_time()
    result = fn(*args)
    elapsed = time.perf_counter() - t0
    cpu_elapsed = time.process_time() - cpu0
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return result, elapsed, peak, cpu_elapsed


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sizes", default="250,500,1000,2000",
                   help="comma-separated document counts to try")
    p.add_argument("--threshold", type=float, default=0.6)
    p.add_argument("--background", default="not recorded",
                   help="other applications running during the measurement")
    a = p.parse_args()
    os.makedirs(OUT, exist_ok=True)

    import bench
    from task3_scale import BruteForce, YourFinder
    path = os.path.join(OUT, "crossover.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as handle:
            prior = json.load(handle)
    else:
        prior = {"runs": []}
    prior["machine"] = machine(a.background)
    prior["measurement"] = {
        "seed": bench.SEED, "shingles": bench.SHINGLES,
        "vocabulary": bench.VOCAB, "threshold": a.threshold,
        "peak_memory_scope": "tracemalloc allocations inside find; input data excluded",
        "dataset": "exact n; random base documents plus min(120, n//10) clones",
    }
    for n in [int(x) for x in a.sizes.split(",")]:
        docs = build_documents(n, bench.SEED)
        assert len(docs) == n
        print(f"  measuring n={n:,} ...", flush=True)
        sim = bench.Counter()
        _, t_brute, m_brute, cpu_brute = timed(BruteForce(a.threshold).find, docs, sim)
        c_brute = sim.calls
        assert c_brute == n * (n - 1) // 2

        row = {"n": n, "actual_n": len(docs), "brute_s": t_brute,
               "brute_calls": c_brute, "brute_peak_bytes": m_brute,
               "brute_cpu_s": cpu_brute,
               "measured_at": datetime.now().astimezone().isoformat()}
        sim2 = bench.Counter()
        _, t_lsh, m_lsh, cpu_lsh = timed(YourFinder(a.threshold).find, docs, sim2)
        row.update({"lsh_s": t_lsh, "lsh_calls": sim2.calls,
                    "lsh_peak_bytes": m_lsh, "lsh_cpu_s": cpu_lsh})
        prior["runs"].append(row)
        # 다음 측정이 오래 걸려도 완료한 결과가 남도록 매번 저장한다.
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(prior, handle, indent=2)
        line = f"  n={n:>6}  brute {t_brute:>8.2f}s  {c_brute:>12,} cmp"
        if "lsh_s" in row:
            line += f"   |  lsh {row['lsh_s']:>7.2f}s  {row['lsh_calls']:>9,} cmp"
        print(line, flush=True)
    print(f"\n  -> out/crossover.json  ({len(prior['runs'])} measurement(s))")
    print("  Keep raising --sizes until something becomes unpleasant. Record where.")


if __name__ == "__main__":
    main()

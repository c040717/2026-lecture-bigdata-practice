#!/usr/bin/env python3
"""Week 4 · Task 2 — Find the size where exact stops being possible.

Textbook §4.1 (the stream model), §4.4, §4.5.

Sketches exist because the exact answer does not fit. That sentence is easy to
agree with and hard to feel, so this task makes you watch it happen on your own
machine: hold every distinct item in a set, keep raising the stream size, and
record where your laptop stops coping.

    python3 task2_limits.py --sizes 100000,400000,1600000
    python3 task2_limits.py --sizes 6400000            # keep going

Your numbers will not match anybody else's. That is the point.
"""
import argparse, json, os, platform, time, tracemalloc
from datetime import datetime


HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")


def machine(background):
    info = {"platform": platform.platform(),
            "processor": platform.processor() or platform.machine(),
            "python": platform.python_version(),
            "background_workload": background}
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
            info["available_ram_bytes"] = status.available_physical
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                            r"HARDWARE\DESCRIPTION\System\CentralProcessor\0") as key:
            info["processor"] = winreg.QueryValueEx(key, "ProcessorNameString")[0].strip()
    return info


def stream(n, distinct_ratio=0.4, seed=246):
    """A stream of n items with about n*distinct_ratio distinct values."""
    import random
    rng = random.Random(seed)
    span = max(1, int(n * distinct_ratio))
    for _ in range(n):
        yield f"key-{rng.randrange(span)}"


def exact_distinct(n):
    """The honest answer: hold every distinct item."""
    tracemalloc.start()
    t0 = time.perf_counter()
    seen = set()
    for x in stream(n):
        seen.add(x)
    elapsed = time.perf_counter() - t0
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return len(seen), elapsed, peak


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sizes", default="100000,400000,1600000")
    p.add_argument("--hashes", type=int, default=64)
    p.add_argument("--background", default="기록하지 않음")
    a = p.parse_args()
    os.makedirs(OUT, exist_ok=True)

    try:
        from task1_sketches import flajolet_martin
    except Exception:
        flajolet_martin = None

    path = os.path.join(OUT, "limits.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as handle:
            prior = json.load(handle)
    else:
        prior = {"runs": []}
    prior["machine"] = machine(a.background)
    prior["measurement"] = {
        "seed": 246, "distinct_ratio": 0.4,
        "scope": "tracemalloc allocations during each complete stream pass",
        "fm_hashes": a.hashes, "fm_combining_rule": "median of 2**R",
    }
    for n in [int(x) for x in a.sizes.split(",")]:
        if n <= 0:
            raise ValueError("스트림 길이는 양수여야 합니다")
        print(f"  시작 n={n:,}, 전체 원소 저장", flush=True)
        true, t_exact, m_exact = exact_distinct(n)
        row = {"n": n, "true_distinct": true, "exact_s": t_exact,
               "exact_peak_bytes": m_exact,
               "measured_at": datetime.now().astimezone().isoformat(),
               "fm_hashes": a.hashes}
        # FM 측정에 오래 걸릴 수 있으므로 집합 결과부터 저장한다.
        prior["runs"].append(row)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(prior, handle, indent=2, ensure_ascii=False)
        print(f"  정확한 결과 완료: {true:,}개, {t_exact:.2f}초, "
              f"{m_exact / 1e6:.2f} MB; FM 시작", flush=True)

        if flajolet_martin is not None:
            try:
                tracemalloc.start()
                t0 = time.perf_counter()
                est = flajolet_martin(stream(n), n_hashes=a.hashes)
                t_fm = time.perf_counter() - t0
                _, m_fm = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                row.update({"fm_estimate": est, "fm_s": t_fm,
                            "fm_peak_bytes": m_fm,
                            "fm_ratio": est / true if true else None})
            except NotImplementedError:
                tracemalloc.stop()

        with open(path, "w", encoding="utf-8") as handle:
            json.dump(prior, handle, indent=2, ensure_ascii=False)
        line = (f"  n={n:>10,}  distinct {true:>9,}   exact {t_exact:>7.2f}s "
                f"{m_exact / 1e6:>8.1f} MB")
        if "fm_s" in row:
            line += (f"   |  fm {row['fm_s']:>7.2f}s {row['fm_peak_bytes'] / 1e6:>6.2f} MB"
                     f"  {row['fm_ratio']:.2f}x")
        print(line, flush=True)

    print(f"\n  -> out/limits.json  ({len(prior['runs'])} measurement(s))")
    print("  Keep raising --sizes until the exact version is unbearable. "
          "Record where, and what ran out.")


if __name__ == "__main__":
    main()

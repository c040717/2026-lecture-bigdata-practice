#!/usr/bin/env python3
"""Week 6 · Task 2 — Lower the threshold until your machine says no.

Textbook §6.1, §6.2.

Support is a knob, and turning it down is how you find the interesting rules.
It is also how you run out of memory, and where that happens is a fact about
your laptop rather than about the algorithm.

    python3 task2_explosion.py --supports 400,200,100,50,25
    python3 task2_explosion.py --supports 12,6            # careful

Lower the threshold until something gives. Write down where and what.
"""
import argparse, json, os, platform, time, tracemalloc
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")


def machine(background="Not recorded"):
    info = {"platform": platform.platform(),
            "processor": platform.processor() or platform.machine(),
            "python": platform.python_version(),
            "logical_cpus": os.cpu_count(),
            "ram_bytes": None, "background": background}
    if os.name == "nt":
        import ctypes
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                               r"HARDWARE\DESCRIPTION\System\CentralProcessor\0") as key:
                info["processor"] = winreg.QueryValueEx(key, "ProcessorNameString")[0].strip()
            ram_kb = ctypes.c_ulonglong()
            if ctypes.windll.kernel32.GetPhysicallyInstalledSystemMemory(ctypes.byref(ram_kb)):
                info["ram_bytes"] = ram_kb.value * 1024
        except OSError:
            pass
    return info


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--supports", default="400,200,100,50,25")
    p.add_argument("--items", type=int, default=2000)
    p.add_argument("--baskets", type=int, default=20000)
    p.add_argument("--avg", type=int, default=20)
    p.add_argument("--background", default="Not recorded")
    p.add_argument("--output", default="explosion.json")
    a = p.parse_args()
    supports = [int(x) for x in a.supports.split(",")]
    if any(s < 1 for s in supports) or a.items < 300 or a.baskets < 1 or a.avg < 2:
        p.error("use positive supports/baskets, items >= 300 and avg >= 2")
    os.makedirs(OUT, exist_ok=True)

    import bench
    from task3_pcy import PlainApriori
    from collections import Counter
    bench.ITEMS, bench.BASKETS, bench.AVG = a.items, a.baskets, a.avg
    baskets = bench.build()
    single_counts = Counter(item for basket in baskets for item in basket)
    config = {"items": a.items, "baskets": a.baskets, "avg": a.avg, "seed": bench.SEED}
    path = os.path.join(OUT, a.output)
    current_machine = machine(a.background)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            prior = json.load(f)
        if prior["config"] != config or prior["machine"] != current_machine:
            raise ValueError("Use a separate output file for a different experiment environment.")
    else:
        prior = {"runs": [], "config": config, "machine": current_machine,
                 "memory_scope": "tracemalloc peak during run; input baskets excluded"}

    for support in supports:
        if any(row["support"] == support for row in prior["runs"]):
            raise ValueError(f"support {support} is already recorded in {a.output}")
        algo = PlainApriori(support)
        measured_at = datetime.now().astimezone().isoformat(timespec="seconds")
        print(f"  measuring support {support}", flush=True)
        tracemalloc.start()
        t0 = time.perf_counter()
        pairs = algo.run(baskets)
        elapsed = time.perf_counter() - t0
        _, peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        row = {"support": support, "frequent_pairs": len(pairs),
               "peak_counters": algo.peak_counters, "seconds": elapsed,
               "peak_bytes": peak_bytes, "measured_at": measured_at,
               "frequent_singletons": sum(c >= support for c in single_counts.values())}
        prior["runs"].append(row)
        # 중간에 멈추더라도 이미 끝난 조건의 결과는 남긴다.
        with open(path, "w", encoding="utf-8") as f:
            json.dump(prior, f, indent=2)
            f.write("\n")
        print(f"  support {support:>5}   pairs {len(pairs):>7,}   "
              f"counters {algo.peak_counters:>10,}   "
              f"{elapsed:>7.2f}s   {peak_bytes / 1e6:>8.1f} MB", flush=True)
        del pairs, algo

    print(f"\n  -> out/{a.output}  ({len(prior['runs'])} run(s))")
    print("  Keep halving the support until it is unbearable. Record where.")


if __name__ == "__main__":
    main()

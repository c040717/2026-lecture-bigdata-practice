#!/usr/bin/env python3
"""Week 7 · does your work pass?"""
import argparse, importlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
sys.path.insert(0, HERE)
PASS, FAIL, SKIP = "PASS", "FAIL", "SKIP"
results = []


def record(task, name, status, detail=""):
    results.append((task, name, status, detail))
    print({PASS: "  ok  ", FAIL: " FAIL ", SKIP: " skip "}[status]
          + f" [{task}] {name}" + (f"  - {detail}" if detail else ""))


def test_task1():
    try:
        m = importlib.import_module("task1_kmeans")
    except Exception as e:
        return record(1, "task1_kmeans.py imports", FAIL, repr(e))
    try:
        rc = m.verify()
    except Exception as e:
        return record(1, "verify runs", FAIL, repr(e))
    record(1, "all seven checks", PASS if rc == 0 else FAIL)


def test_task2():
    path = os.path.join(OUT, "curse.json")
    if not os.path.exists(path):
        return record(2, "out/curse.json exists", FAIL, "run task2_curse.py")
    data = json.load(open(path))
    dims = sorted({r["dim"] for r in data.get("runs", [])})
    record(2, "A1 six or more dimensions", PASS if len(dims) >= 6 else FAIL, str(dims))
    record(2, "A1 reaches 200 or more", PASS if dims and max(dims) >= 200 else FAIL)
    ns = sorted({r.get("points") for r in data.get("runs", [])})
    record(2, "A6 more than one point count", PASS if len(ns) >= 2 else FAIL, str(ns))
    record(2, "A7 machine recorded",
           PASS if data.get("machine", {}).get("platform") else FAIL)
    record(2, "out/curse.md exists",
           PASS if os.path.exists(os.path.join(OUT, "curse.md")) else FAIL)


def test_task3():
    try:
        bench = importlib.import_module("bench")
        mod = importlib.import_module("task3_fewer")
    except Exception as e:
        return record(3, "modules import", FAIL, repr(e))
    points, initial = bench.build()
    base = bench.run(mod.NaiveKMeans, "baseline", points, initial)
    try:
        mine = bench.run(mod.YourKMeans, "yours", points, initial)
    except NotImplementedError:
        return record(3, "YourKMeans implemented", FAIL, "still a stub")
    except Exception as e:
        return record(3, "YourKMeans runs", FAIL, repr(e))
    drift = abs(mine["sse"] - base["sse"]) / base["sse"]
    record(3, "R3 sse within 0.1%", PASS if drift <= 0.001 else FAIL, f"{drift:.4%}")
    cut = 1 - mine["calls"] / base["calls"]
    record(3, "R4 fewer distance computations", PASS if cut > 0.05 else FAIL,
           f"{cut:.1%} cut")
    record(3, "R5 bound argument in observation.md", SKIP, "graded by a human")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--task", type=int, choices=[1, 2, 3])
    a = p.parse_args()
    os.makedirs(OUT, exist_ok=True)
    for n, fn in [(1, test_task1), (2, test_task2), (3, test_task3)]:
        if a.task in (None, n):
            print(f"\n=== Task {n}")
            fn()
    print()
    failed = sum(1 for *_, s, _ in results if s == FAIL)
    skipped = sum(1 for *_, s, _ in results if s == SKIP)
    print(f"  {len(results) - failed - skipped} passed, {failed} failed, {skipped} skipped")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()

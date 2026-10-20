#!/usr/bin/env python3
"""Week 5 · Task 2 — How long does it take to converge, and on what?

Textbook §5.1, §5.2.

The textbook says PageRank converges. It does not say in how many iterations,
because the answer depends on beta, on the graph, and on what you are willing
to call "converged". Those three knobs are yours to turn, on your machine,
with a graph big enough that you can feel the cost.

    python3 task2_convergence.py --betas 0.5,0.7,0.85,0.95,0.99
    python3 task2_convergence.py --nodes 20000 --betas 0.85,0.95

Your timings are about your hardware. The iteration counts are not - those are
about the mathematics, and everybody should get the same ones.
"""
import argparse, json, os, platform, time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")


def machine(background=None):
    info = {"platform": platform.platform(),
            "processor": platform.processor() or platform.machine(),
            "python": platform.python_version(),
            "logical_cpus": os.cpu_count(),
            "ram_bytes": None,
            "background": background or "Not recorded"}
    if platform.system() == "Windows":
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
            pass  # Leave unavailable hardware fields unknown, never guessed.
    return info


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--betas", default="0.5,0.7,0.85,0.95,0.99")
    p.add_argument("--nodes", type=int, default=None,
                   help="graph size; default is the harness graph")
    p.add_argument("--tol", type=float, default=1e-10)
    p.add_argument("--max-iter", type=int, default=5000,
                   help="iteration limit; near-one beta may need more than 500")
    p.add_argument("--background", help="observed applications running during measurement")
    a = p.parse_args()
    betas = [float(x) for x in a.betas.split(",")]
    if any(not 0 <= beta < 1 for beta in betas):
        p.error("each beta must be at least 0 and less than 1")
    if a.tol <= 0 or a.max_iter < 1:
        p.error("tol and max-iter must be positive")
    if a.nodes is not None and a.nodes < 50:
        p.error("the harness graph generator needs at least 50 nodes")
    os.makedirs(OUT, exist_ok=True)

    import bench
    if a.nodes:
        bench.NODES = a.nodes
    graph = bench.build()

    from task1_pagerank import pagerank

    rows = []
    for beta in betas:
        t0 = time.perf_counter()
        ranks = pagerank(graph, beta=beta, iterations=a.max_iter, tol=a.tol)
        elapsed = time.perf_counter() - t0
        iters = getattr(pagerank, "iterations", None)
        top = sorted(ranks.items(), key=lambda kv: -kv[1])[:10]
        # One extra update verifies the stopping condition outside the timed run.
        n = len(graph)
        dangling = sum(ranks[v] for v, outs in graph.items() if not outs)
        base = (1 - beta + beta * dangling) / n
        updated = dict.fromkeys(graph, base)
        for v, outs in graph.items():
            if outs:
                share = beta * ranks[v] / len(outs)
                for w in outs:
                    updated[w] += share
        residual = sum(abs(updated[v] - ranks[v]) for v in graph)
        rows.append({"beta": beta, "nodes": len(graph), "tol": a.tol,
                     "iterations": iters, "seconds": elapsed,
                     "max_iterations": a.max_iter,
                     "converged": residual < a.tol,
                     "l1_residual": residual,
                     "rank_sum": sum(ranks.values()),
                     "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
                     "top10": [k for k, _ in top]})
        print(f"  beta {beta:<5}  {str(iters):>4} iterations  {elapsed:>7.3f}s   "
              f"top: {', '.join(k for k, _ in top[:3])}")

    path = os.path.join(OUT, "convergence.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            prior = json.load(f)
    else:
        prior = {"runs": []}
    prior["machine"] = machine(a.background)
    prior["runs"].extend(rows)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(prior, f, indent=2)
    print(f"\n  -> out/convergence.json  ({len(prior['runs'])} run(s))")


if __name__ == "__main__":
    main()

"""확장 데이터에서 실행 시간과 메모리 중단 기준을 확인한다."""
import argparse
import ctypes
import json
import multiprocessing as mp
import os
from pathlib import Path
import queue
import time
import tracemalloc
from datetime import datetime

from task2_explosion import machine


def working_set(pid):
    class MemoryCounters(ctypes.Structure):
        _fields_ = [("cb", ctypes.c_ulong), ("PageFaultCount", ctypes.c_ulong),
                    ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]
    kernel = ctypes.windll.kernel32
    kernel.OpenProcess.restype = ctypes.c_void_p
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    query = ctypes.windll.psapi.GetProcessMemoryInfo
    query.argtypes = [ctypes.c_void_p, ctypes.POINTER(MemoryCounters), ctypes.c_ulong]
    handle = kernel.OpenProcess(0x0400 | 0x0010, False, pid)
    if not handle:
        return None
    try:
        counters = MemoryCounters()
        counters.cb = ctypes.sizeof(counters)
        if query(handle, ctypes.byref(counters), counters.cb):
            return counters.WorkingSetSize
    finally:
        kernel.CloseHandle(handle)
    return None


def worker(messages, support):
    import bench
    from task3_pcy import PlainApriori
    bench.ITEMS, bench.BASKETS, bench.AVG = 10000, 40000, 40
    baskets = bench.build()
    messages.put({"status": "ready"})
    algo = PlainApriori(support)
    tracemalloc.start()
    start = time.perf_counter()
    pairs = algo.run(baskets)
    elapsed = time.perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    messages.put({"status": "completed", "seconds": elapsed,
                  "peak_bytes": peak, "peak_counters": algo.peak_counters,
                  "frequent_pairs": len(pairs)})


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--supports", default="400,200,100,50,25,12,6,3,1")
    p.add_argument("--seconds", type=float, default=30)
    p.add_argument("--memory-mib", type=int, default=1024)
    p.add_argument("--background", default="Not recorded")
    args = p.parse_args()
    if os.name != "nt":
        p.error("working-set monitoring in this script requires Windows")
    report = {"config": {"items": 10000, "baskets": 40000, "avg": 40, "seed": 246},
              "limits": {"algorithm_seconds": args.seconds, "working_set_bytes": args.memory_mib * 2**20},
              "machine": machine(args.background), "runs": []}
    path = Path(__file__).parent / "out" / "boundary.json"
    if path.exists():
        p.error("boundary.json already exists; keep the earlier record separately")
    for support in map(int, args.supports.split(",")):
        messages = mp.Queue()
        process = mp.Process(target=worker, args=(messages, support))
        process.start()
        start, observed_peak, result = None, 0, None
        measured_at = datetime.now().astimezone().isoformat(timespec="seconds")
        while result is None:
            try:
                message = messages.get(timeout=0.1)
                if message["status"] == "ready":
                    start = time.perf_counter()
                    print(f"support {support}: algorithm started", flush=True)
                else:
                    result = message
            except queue.Empty:
                if not process.is_alive():
                    result = {"status": "worker_exited", "exitcode": process.exitcode}
            memory = working_set(process.pid)
            if memory is not None:
                observed_peak = max(observed_peak, memory)
            elapsed = time.perf_counter() - start if start is not None else None
            if result is None and (observed_peak >= args.memory_mib * 2**20 or
                                   (elapsed is not None and elapsed >= args.seconds)):
                reason = "working_set_limit" if observed_peak >= args.memory_mib * 2**20 else "time_limit"
                result = {"status": "stopped", "reason": reason, "seconds": elapsed,
                          "phase": "algorithm" if start is not None else "input_generation",
                          "peak_bytes": None, "peak_counters": None, "frequent_pairs": None}
                process.terminate()
        process.join()
        messages.close()
        result.update({"support": support, "observed_peak_working_set_bytes": observed_peak,
                       "measured_at": measured_at})
        report["runs"].append(result)
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result), flush=True)
        if result["status"] != "completed":
            break


if __name__ == "__main__":
    main()

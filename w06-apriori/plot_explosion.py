"""저장된 측정값으로 support별 카운터와 정답 수를 그린다."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


out = Path(__file__).parent / "out"
runs = json.loads((out / "explosion.json").read_text(encoding="utf-8"))["runs"]
supports = [row["support"] for row in runs]
fig, ax = plt.subplots(figsize=(9, 5.4), layout="constrained")
ax.plot(supports, [r["peak_counters"] for r in runs], "o-", label="Peak pair counters", color="#2362a2")
ax.plot(supports, [r["frequent_pairs"] for r in runs], "s-", label="Frequent pairs (answers)", color="#b55c16")
ax.set(xscale="log", yscale="log", xlabel="Support count (lower to the right)", ylabel="Number of pairs",
       title="A-Priori: counters and answers\n20,000 baskets, 2,000 items, seed 246")
ax.set_xticks(supports, [str(s) for s in supports])
ax.invert_xaxis()
ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:,.0f}"))
ax.grid(True, which="major", alpha=0.25)
ax.legend(loc="lower right")
fig.savefig(out / "explosion.png", dpi=180)
plt.close(fig)

# Week 7 Lab · Clustering

**Theory** — 7-1 clustering, the curse of dimensionality (§7.1) · 7-2 hierarchical and k-means (§7.2 – §7.3)
**Submit to** — `w07-kmeans/out/`

Clustering asks which points belong together, which requires "near" to mean
something. This week: build the standard method, watch what decides its answer,
measure the dimension at which "near" stops meaning anything, and then do the
same clustering for a tenth of the work.

```bash
cd w07-kmeans
```

| | Task | You build |
|---|---|---|
| 1 | k-means and its initialisation | the method, and k-means++ |
| 2 | Watch distance stop meaning anything | a contrast curve across dimensions |
| 3 | The same clustering, fewer distances | bounds that prune, without approximating |

Details and requirements are in **`task1.md`**, **`task2.md`**, **`task3.md`**.

## Running everything

```bash
python3 task1_kmeans.py --verify
python3 task2_curse.py --dims 2,5,10,20,50,100,200
python3 bench.py --yours
python3 test_tasks.py
```

## What to submit

| File | From |
|---|---|
| `task1_kmeans.py` | your k-means and k-means++ |
| `out/curse.json` · `out/curse.md` | the contrast curve |
| `task3_fewer.py` · `out/bench.txt` | your pruned k-means and its numbers |
| `out/observation.md` | 2–3 lines per task |

```bash
python3 ../check.py w07
```

## No download needed

Everything is generated with a fixed seed. Task 2's numbers are about your data
size and your machine, so they are not supposed to match anybody else's exactly.

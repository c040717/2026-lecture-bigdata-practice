# Task 1 · k-means, and the Thing That Decides the Answer

**File** — `task1_kmeans.py`
**Theory** — §7.3 k-means, §7.3.2 initialisation
**Kind** — implementation · runs anywhere

---

## What you are building

k-means is four lines. Pick centroids, assign each point to the nearest, move
each centroid to the mean of its points, repeat. It always converges.

It converges to a **local** optimum, and which one depends entirely on where you
started. That is not a footnote — it is the difference between a clustering that
means something and one that does not, and you can watch it happen on nine points.

## Requirements

| # | Requirement |
|---|---|
| R1 | `euclidean` works in any number of dimensions |
| R2 | `assign` breaks ties toward the **lower index**, so answers are comparable |
| R3 | `update` handles an **empty cluster**. Decide what you do and say so |
| R4 | `kmeans(..., init="random")` picks k starting points at random |
| R5 | `kmeans(..., init="++")` implements k-means++ from §7.3.2 |
| R6 | `sse_of` returns the sum of squared distances to each point's own centroid |
| R7 | Sets `kmeans.iterations` |

R3 is the one with no single right answer. A cluster can lose all its points, and
the mean of nothing is undefined. Keep the old centroid? Move it to the furthest
point? Both are defensible and they give different clusterings.

## Pass condition

```bash
python3 task1_kmeans.py --verify
```

Seven checks. Two of them are about initialisation, across 40 seeds:

```
  ok    random init sometimes lands badly        sse from 0.120 to 96.105
  ok    k-means++ is more reliable than random   mean sse: ++ 0.120 vs random 38.511
```

Nine points in three obvious blobs, and random initialisation gets it wrong most
of the time. That is the result to sit with.

## What to write in `observation.md`

- Your R3 choice for empty clusters, and what the alternative would have done
- Over 40 seeds, how often did random initialisation find the blobs? And ++?
- k-means++ spends distance computations before the first iteration. What does
  it buy, and when would you rather not pay?
- SSE always goes down as k goes up. So why can you not choose k by minimising it?

# Task 3 · The Same Clustering, With Far Fewer Distances

**Files** — `task3_fewer.py` · harness `bench.py` (**do not edit the harness**)
**Theory** — §7.3, §7.1.3
**Kind** — improvement · runs anywhere

---

## What you are given

`NaiveKMeans` does what the definition says: every iteration, compare every point
with every centroid. n × k distance computations per pass, and on real data the
distance computation is almost the entire cost.

```bash
python3 bench.py            # baseline, about 14 seconds
python3 bench.py --yours
```

```
  20,000 points in 20 dimensions  ·  k = 12
```

**Where the baseline lands:**

```
  baseline   distances   10,320,000   sse  10,737,882.94    43 iters   13.33s
```

Ten million distance computations. Most of them are wasted: after the first
couple of iterations, most points do not change cluster and most centroids barely
move — and the naive version measures all of it anyway.

## Requirements

| # | Requirement |
|---|---|
| R1 | `YourKMeans(k, max_iter)` with `run(points, initial_centroids, distance)` |
| R2 | `bench.py` unmodified |
| R3 | **Final SSE within 0.1% of the baseline** |
| R4 | Fewer distance computations |
| R5 | In `observation.md`: which bound does the work, and what it costs to maintain |

R3 is strict on purpose. A correct implementation of this gets SSE identical to
the last decimal, because it does not approximate anything — it only avoids
measuring things it can prove.

## Grading

| | Requirement |
|---|---|
| pass | R1–R4, more than 5% cut |
| good | ≥ **40%** cut |
| **strong** | ≥ **70%** cut |

A textbook bounds-based version gets about 88% with SSE identical to the last
digit. If your SSE drifts, you are approximating rather than pruning, and R3
will catch it.

## The idea

The triangle inequality:

> if a point is much closer to its own centroid than that centroid moved, and
> than any other centroid could have come, then it **cannot** have changed
> cluster, and you do not have to measure anything

You need two things to use that: an upper bound on the distance from each point
to its own centroid, and something that bounds how close any other centroid could
be. Both can be updated from how far the centroids moved, which is k distance
computations per iteration rather than n × k.

That asymmetry — **k is small and n is large** — is the whole opening.

Calls on two centroids are counted too. That is the correct accounting, since it
is real work, and it is what makes the trade-off honest.

## What to write in `observation.md`

- What you store per point, and how many extra numbers that is
- R5: which bound eliminates the most work, and what maintaining it costs
- Your SSE difference from the baseline. If it is exactly zero, say why it had to be
- The first iteration cannot prune anything. What fraction of your total
  distance computations happened in it?

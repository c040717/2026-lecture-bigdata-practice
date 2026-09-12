# Task 2 · Watch Distance Stop Meaning Anything

**File** — `task2_curse.py`
**Theory** — §7.1.3 the curse of dimensionality
**Kind** — **measurement. The dimension where it bites depends on your data size.**

---

## Why this task exists

In two dimensions "nearest" is obvious. In two hundred, every point is roughly
the same distance from every other point, and everything built on "nearest" —
k-means, k-NN, LSH from week 3 — has nothing left to stand on.

That is usually stated as a fact to accept. Measure it instead.

## What to do

```bash
python3 task2_curse.py --dims 2,5,10,20,50,100,200
python3 task2_curse.py --dims 500,1000 --points 2000
```

Each run samples 20,000 random pairs of uniform points and reports the minimum,
maximum, mean and spread of the distances between them.

| # | Requirement |
|---|---|
| A1 | At least **six** dimensions, from single digits to 200 or more |
| A2 | Tabulate **contrast** = (max − min) / min against dimension → `out/curse.md` |
| A3 | Describe what happens to contrast. At roughly what dimension does it drop below 1? Below 0.5? |
| A4 | The **mean** distance grows with dimension. Say roughly how — is it linear in d, or something else? Check against your numbers |
| A5 | Relative standard deviation (spread ÷ mean) also falls. Report it, and say which of A3 and A5 better captures "distance stopped meaning anything" |
| A6 | Vary the **point count** at one fixed dimension. Does contrast depend on n as well as d? |
| A7 | Your machine, and how long the largest run took |

A4 has an answer you can predict before measuring: for uniform points in the
unit cube, mean distance grows like the square root of d. Check whether your
numbers agree, and if they do not, work out why before writing it down.

A6 is the question most people never ask. Contrast is about the gap between the
nearest and furthest of **n** points, so n is in the answer too.

## Connect it back

| # | Requirement |
|---|---|
| A8 | Week 3 was LSH on Jaccard similarity. Does this result threaten it? Say why or why not |

A8 is worth thinking about properly. Jaccard is not Euclidean, and shingle sets
are not uniform points in a cube. Deciding whether the curse applies is more
useful than assuming it does.

## Pass condition

`out/curse.json` has six or more dimensions with your machine recorded, and
`out/curse.md` answers A3–A8.

```bash
python3 test_tasks.py --task 2
```

## What to write in `observation.md`

- The dimension where contrast dropped below 1, at your data size
- A6: whether n mattered, and what that means
- A8: your answer about LSH, with the reason

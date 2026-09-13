# Task 4 · Build MapReduce, Then Watch Spark Lose — **optional**

**File** — `task4_mapreduce.py`
**Theory** — §2.2 MapReduce, §2.2.4 combiners, §2.3 algorithms using MapReduce
**Status** — **optional.** Not part of the assignment, not graded. Effort is noted.

---

## Part A · Build the engine  *(needs only `python3`)*

`mapreduce(pairs, mapper, reducer, combiner=None)` is the whole model from §2.2
in one function: map, shuffle, reduce. About twenty lines.

| # | Requirement |
|---|---|
| A1 | The mapper runs over every input pair, producing `(k2, v2)` |
| A2 | The shuffle groups by `k2`, and you **count what crosses it** |
| A3 | A combiner, when given, runs **per mapper** — not globally |
| A4 | Word count with and without a combiner gives the **same answer** |
| A5 | The combiner **reduces the shuffled count**. If it does not, A3 is wrong |

**A3 is the requirement that carries the task.** If you apply the combiner to all
mapper output at once you have written the reducer twice, the answer will still
be right, and the shuffled count will not move. The combiner exists because each
mapper can collapse *its own* output before anything goes over the network.

Reference numbers on 200,000 words over 8 mappers:

```
  your MapReduce     shuffled   200,000   correct
  + combiner         shuffled   114,226   correct     ← cut by 42.9%
```

If your combiner run shuffles 200,000 as well, re-read A3.

## Part B · Matrix-vector multiplication  *(needs only `python3`)*

§2.3.1. Express `M · v` as a mapper and a reducer and run it on your engine.

| # | Requirement |
|---|---|
| B1 | `matrix_vector(matrix, vector)` returns `{i: value}` and is correct |
| B2 | In `observation.md`: §2.3.2 asks what changes **when v does not fit in memory**. Answer it. You do not have to implement it |

B2 is the question chapter 2 is really about. The mapper needs `v[j]` for every
element it touches, and the chapter's answer is a specific thing you do to the
matrix, not to the vector.

## Part C · The same job in Spark  *(needs Java 17 and PySpark)*

```bash
python3 task4_mapreduce.py --spark
```

| # | Requirement |
|---|---|
| C1 | Spark produces the same counts as the plain `Counter` |
| C2 | Report **startup** and **compute** separately. They are very different numbers |
| C3 | **Spark will be slower. Report the ratio, and explain why in observation.md** |
| C4 | Say at what point it would stop being slower. Be specific about what changes |

Measured on one laptop, 200,000 words:

```
  plain Counter          0.008s
  spark startup          1.962s
  spark compute          1.035s
  spark total            2.998s   ->  369x the plain Counter
```

**369 times slower, for the same answer.** That is not a misconfiguration and you
are not expected to fix it. C3 asks you to explain it — there are at least three
separate costs in that 3 seconds and only one of them is the computation.

C4 is the one worth thinking about. Something has to change for Spark to win, and
it is not the number of cores on your laptop. Name it.

> If you conclude from this that Spark is useless, you have learned half of it.
> The other half is that a `dict` holding 875 million distinct keys does not exist,
> and the thing that is 369 times slower is still running when the `dict` is gone.

## If Spark will not start

The script catches the failure and tells you. Record it in `observation.md` and
answer C4 from the chapter instead — that is a complete submission for an
optional task. Java version mismatches are the usual cause: Spark 3.5 wants
Java 8, 11 or 17, and a newer JDK will fail with a gateway error.

## What to write in `observation.md`

- Your shuffled counts with and without the combiner, and the percentage cut
- B2: what §2.3.2 does when the vector does not fit
- C3: the ratio you measured, and the three costs inside it
- C4: what has to change for Spark to be the faster choice

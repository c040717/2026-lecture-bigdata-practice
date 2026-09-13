# Task 4 · SON — A-Priori That Survives Being Split Up — **optional**

**File** — `task4_son.py`
**Theory** — §6.4.3 the SON algorithm, §6.4.4 SON and MapReduce
**Status** — **optional.** Not part of the assignment, not graded. Effort is noted.

---

## Why this one is worth doing

Tasks 1 and 3 assume the baskets fit on one machine. SON does not, and it is the
**textbook's own** answer — §6.4.3 and §6.4.4, algorithm included.

It also has a guarantee that most sampling schemes do not:

> an itemset that is frequent overall is frequent in **at least one chunk**

which is why pass one can look at chunks independently, in parallel, with no
communication between them, and still miss nothing. Proving that to yourself is
worth more than the code.

## Requirements

| # | Requirement |
|---|---|
| A1 | `son_pass_one` returns every pair frequent **in at least one chunk**, using the **scaled** threshold from §6.4.3 |
| A2 | `son_pass_two` counts only those candidates over all baskets and keeps the real ones |
| A3 | **Zero false negatives** against task 3's answer. Not "almost zero" |
| A4 | Report the candidate count. It is much larger than the answer — say why that is acceptable |
| A5 | Change `--chunks` and report what moves. **One number changes and one does not** |
| A6 | In `observation.md`: prove A3 to yourself. Why can a globally frequent pair not be missed by every chunk? |

**A1 is where it goes wrong.** A chunk holding a tenth of the baskets needs a
tenth of the threshold. Use the full threshold on a chunk and you lose the
guarantee immediately — quietly, on real data, with no error message.

**A6 is the point of the task.** The argument is short and it is a proof by
contradiction. If you can write it in three lines, you understand SON.

## Measured numbers

```
  task 3 baseline      0.57s   pairs  6,397
  your SON            12.19s   pairs  6,397   candidates  14,201   missing 0, extra 0
  spark SON            5.85s   pairs  6,397   candidates  14,695   missing 0
```

Three things in that table are worth stopping on.

**SON is 21× slower than task 3.** On one machine, with baskets that fit, SON is
a bad choice — and it is still the right algorithm, because task 3 does not exist
at all when the baskets do not fit.

**Spark made SON about twice as fast**, not 21× — it parallelised pass two across
your cores. So Spark did help, and it helped the *algorithm you gave it*.
Distributing a worse algorithm is not progress, and that sentence is most of what
people get wrong about this.

**The candidate counts differ (14,201 vs 14,695) and the answers do not.** The
chunking is different, so what is "frequent somewhere" is different — and pass two
removes the difference. That is A5, and it is the guarantee working in front of you.

## Pass two is slower than it needs to be

The obvious pass two checks every candidate against every basket. On this data
that is 20,000 × 14,000 subset tests, which is where your 12 seconds went.

There is a much better way and it uses something you already built in task 1.
Not a requirement — but if you find it, put the number in `observation.md`.

## If Spark will not start

The script catches it. Everything except the last row runs without Spark, and
A1 – A6 are all answerable single-process. Record what stopped you.

## What to write in `observation.md`

- A6: the three-line argument for no false negatives
- A5: which number moved when you changed `--chunks`, and which did not
- Why is SON the right algorithm even though it is 21× slower here?
- If you sped up pass two: what you did and the new number

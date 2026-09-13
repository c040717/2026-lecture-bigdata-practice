# Week 2 · MapReduce and Spark — **optional**

**Theory** — 2-1 · 2-2 Distributed file systems, MapReduce, Spark (§2.1 – §2.4)
**Status** — **optional. Not part of the assignment. No grade attached.**

Week 2's session is the coding agent, so chapter 2 is the one chapter in this
course you are taught and never run. This folder closes that, for anyone who
wants it and whose machine will run Spark.

```bash
cd w02-mapreduce
python3 task4_mapreduce.py              # the first half needs nothing but python3
python3 task4_mapreduce.py --spark      # the second half needs Java and PySpark
```

| | Task | Needs |
|---|---|---|
| 4 | Build MapReduce, then watch Spark lose | python3 · (Spark half: Java 17 + PySpark) |

Requirements are in **`task4.md`**.

## Why this is optional

Two honest reasons.

**It does not fit in a session.** Week 2's third session is the coding agent,
and that is 79 slides on its own.

**You have one machine.** Spark on one laptop is slower than a `dict` — measurably,
by a lot — and this task will show you exactly how much. What it teaches is the
*model* and the point at which one machine stops being enough, not speed.

## If Spark will not install

Do the first half. It needs nothing but `python3`, and it is the half where you
build the engine. Then write in `observation.md` what stopped you. "Java 17 would
not install on my machine" is a complete answer, and it is also the reason this
whole folder is optional.

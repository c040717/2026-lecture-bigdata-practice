# Introduction to Big Data · Labs

2026-2 · Korea University Sejong · **Weeks 3 – 7**

This is the lab repository. Clone it and work inside it.

```bash
git clone https://github.com/codingchild2424/2026-lecture-bigdata-practice.git
cd 2026-lecture-bigdata-practice
```

The slides live separately and link here week by week.

---

## The weeks

| Week | Folder | Subject |
|---|---|---|
| 2 | `w02-mapreduce/` | **optional** — MapReduce and Spark |
| 3 | `w03-lsh/` | finding similar items |
| 4 | `w04-stream/` | mining data streams |
| 5 | `w05-pagerank/` | link analysis |
| 6 | `w06-apriori/` | frequent itemsets |
| 7 | `w07-kmeans/` | clustering |

Week 2's session is the coding agent, so `w02-mapreduce/` is **optional** — it
exists because chapter 2 is otherwise the one chapter you are taught and never
run. Weeks 9 – 15 are the project.

## How a week works

Every folder holds the same things:

```
wNN-topic/
├── README.md        what the week is about, and the three tasks
├── task1.md         one task, its requirements, its pass condition
├── task2.md
├── task3.md
├── task1_*.py       the code you write
├── task2_*.py
├── task3_*.py       the baseline you have to beat lives here too
├── bench.py         the measuring harness for task 3 - do not edit it
└── test_tasks.py    run this before you submit
```

**Three tasks a week**, and they are different in kind:

| | |
|---|---|
| **Task 1 · implementation** | build the method yourself, checked against the textbook's own worked example where there is one |
| **Task 2 · measurement** | on **your** machine. Find where it runs out of memory, where the curve bends, where the method stops working. Your numbers are not supposed to match anybody else's |
| **Task 3 · improvement** | a deliberately naive implementation is committed here. Beat it, measured by `bench.py`, without changing the answer |

There is no separate assignment. **The three tasks are the assignment.**

### Optional task 4 — Spark

Three weeks have a fourth task that uses **Spark**: `w02-mapreduce`,
`w05-pagerank` and `w06-apriori`.

**They are optional, not graded, and not part of the assignment.** Do them if
your machine will run Spark; effort is noted, absence is not penalised.

They exist because the course teaches MapReduce and Spark and never makes you run
one. What they will show you is not what you expect: **on a single laptop Spark is
slower**, by 369× on a word count and 3× on PageRank. That is the measured result
and it is the point. What changes at scale — and what does not — is what these
tasks ask you to explain.

Spark needs **Java 8, 11 or 17** and `pip install pyspark`. A newer JDK fails with
a gateway error. If it will not install, each task has a half that does not need
it, and "it would not install" is an acceptable submission for an optional task.

## Submitting

Put everything under that week's `out/`. Then:

```bash
python3 test_tasks.py         # does it pass?
python3 ../check.py w03       # is anything missing?
```

`test_tasks.py` runs your code and checks it against a reference. `check.py`
only looks for files. Neither can tell whether you understood anything, which is
what `out/observation.md` is for — **2 to 3 lines per task**, and it is the
centre of the grade.

---

## Running environment

Everything here is plain Python 3 with no third-party packages required. It runs
on your laptop as it is.

### If you want the same environment as everyone else

```bash
make image          # build the Ubuntu 24.04 image, once
make shell          # a shell inside it, with /work mounted
```

The image has **Java 17 and PySpark**, which is the easiest way to do the
optional task 4s. `requirements.txt` also adds `numpy`, `pandas`, `matplotlib`,
`scipy` and `scikit-learn`. **Tasks 1 to 3 need none of it**, and task 1 each week
is explicitly about writing the method rather than calling a library that has it.

### GitHub Codespaces

`Code → Codespaces → Create codespace` reads `.devcontainer/` and gives you the
same Ubuntu environment in a browser. Useful if Docker will not install.

### No download needed

Every task generates its data from a fixed seed. Nothing here needs a dataset
downloaded, which also means your Task 3 numbers are directly comparable with
the baseline figures quoted in each `task3.md`.

Task 2 is the exception in spirit rather than in data: it measures **your
machine**, so its numbers are personal to you.

## Grading

Part of the 10% participation score. Each week is small, which makes it easy to
skip. The observation write-up is the centre of it.

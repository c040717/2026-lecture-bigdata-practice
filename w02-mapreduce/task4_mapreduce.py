#!/usr/bin/env python3
"""Week 2 · Task 4 (optional) — Build MapReduce, then watch Spark lose.

Textbook §2.2 (MapReduce), §2.2.4 (combiners), §2.3 (algorithms using MapReduce).

Chapter 2 is the only chapter in this course you are taught and never run. This
task closes that, and the result is not the one the chapter leads you to expect.

    python3 task4_mapreduce.py              # your engine only
    python3 task4_mapreduce.py --spark      # and the same job in PySpark

Optional. It is not part of the assignment. Do it if your machine will run
Spark; if it will not, say so and move on - the first half needs nothing.
"""
import argparse, itertools, random, time
from collections import defaultdict


# --------------------------------------------------------------------- engine
def mapreduce(pairs, mapper, reducer, combiner=None):
    """The model from §2.2, in one function, on one machine.

    pairs      the input, as (key, value)
    mapper     (k, v) -> iterable of (k2, v2)
    combiner   optional, §2.2.4 - reduces a mapper's own output before shuffling
    reducer    (k2, [v2, ...]) -> iterable of (k3, v3)

    Return (results, stats) where stats counts the intermediate pairs that
    crossed the shuffle. That count is the thing MapReduce actually cares about,
    because it is what goes over the network.

    TASK 4a - implement this. Roughly twenty lines.
      1. run the mapper over every input pair, collecting (k2, v2)
      2. if a combiner was given, apply it per mapper output, not globally.
         Split the mapper output into `N_MAPPERS` groups first, so that the
         combiner has something local to work on - otherwise you have written
         the reducer twice and the count will not change
      3. group by k2  (this is the shuffle - count what crosses it)
      4. run the reducer on each group
    """
    raise NotImplementedError("TASK 4a - build the engine")


N_MAPPERS = 8


# ---------------------------------------------------------------------- jobs
def word_count(words):
    """§2.2, the canonical example. Returns {word: count}."""
    mapper = lambda k, v: [(v, 1)]
    reducer = lambda k, vs: [(k, sum(vs))]
    return mapreduce([(i, w) for i, w in enumerate(words)], mapper, reducer)


def word_count_combined(words):
    """The same job with a combiner. Same answer, far less shuffled."""
    mapper = lambda k, v: [(v, 1)]
    combiner = lambda k, vs: [(k, sum(vs))]
    reducer = lambda k, vs: [(k, sum(vs))]
    return mapreduce([(i, w) for i, w in enumerate(words)], mapper, reducer,
                     combiner=combiner)


def matrix_vector(matrix, vector):
    """§2.3.1 - matrix-vector multiplication as MapReduce.

    `matrix` is [(i, j, m_ij), ...] sparse. `vector` is a list.
    The product's element i is the sum over j of m_ij * v_j.

    TASK 4b - express this as a mapper and a reducer and run it on your engine.
    Return {i: value}.

    The question §2.3.2 asks is what changes when v does not fit in memory.
    Answer it in observation.md - you do not have to implement it.
    """
    raise NotImplementedError("TASK 4b - matrix-vector as MapReduce")


# ------------------------------------------------------------------- harness
def make_words(n=200_000, vocab=20_000, seed=246):
    rng = random.Random(seed)
    return [f"w{rng.randrange(vocab)}" for _ in range(n)]


def spark_word_count(words):
    """The same job in PySpark. Times the startup separately, because it is
    most of the cost and pretending otherwise would be dishonest."""
    t0 = time.perf_counter()
    from pyspark.sql import SparkSession
    spark = (SparkSession.builder.master("local[*]").appName("w02")
             .config("spark.ui.enabled", "false").getOrCreate())
    spark.sparkContext.setLogLevel("ERROR")
    startup = time.perf_counter() - t0

    t0 = time.perf_counter()
    counts = (spark.sparkContext.parallelize(words, N_MAPPERS)
              .map(lambda w: (w, 1))
              .reduceByKey(lambda a, b: a + b)
              .collectAsMap())
    compute = time.perf_counter() - t0
    spark.stop()
    return counts, startup, compute


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--spark", action="store_true")
    p.add_argument("--words", type=int, default=200_000)
    a = p.parse_args()

    words = make_words(a.words)
    print(f"\n  {len(words):,} words, {len(set(words)):,} distinct, "
          f"{N_MAPPERS} mappers\n")

    from collections import Counter
    t0 = time.perf_counter()
    truth = Counter(words)
    t_plain = time.perf_counter() - t0
    print(f"  plain Counter        {t_plain:7.3f}s")

    t0 = time.perf_counter()
    got, stats = word_count(words)
    t_mr = time.perf_counter() - t0
    ok = dict(got) == dict(truth)
    print(f"  your MapReduce       {t_mr:7.3f}s   shuffled "
          f"{stats['shuffled']:>9,}   {'correct' if ok else 'WRONG'}")

    got_c, stats_c = word_count_combined(words)
    ok_c = dict(got_c) == dict(truth)
    print(f"  + combiner           {'':7}    shuffled "
          f"{stats_c['shuffled']:>9,}   {'correct' if ok_c else 'WRONG'}")
    if stats["shuffled"]:
        cut = 1 - stats_c["shuffled"] / stats["shuffled"]
        print(f"  combiner cut the shuffle by {cut:.1%}")

    if a.spark:
        try:
            sp, startup, compute = spark_word_count(words)
        except Exception as e:
            print(f"\n  Spark did not start: {type(e).__name__}")
            print("  That is a valid outcome - record it in observation.md.")
            return
        print(f"\n  spark startup        {startup:7.3f}s")
        print(f"  spark compute        {compute:7.3f}s")
        print(f"  spark total          {startup + compute:7.3f}s   "
              f"-> {(startup + compute) / t_plain:.0f}x the plain Counter")
        print(f"  same answer: {dict(sp) == dict(truth)}")
        print("\n  Spark is slower here, and that is the finding. "
              "observation.md asks why,\n  and at what point it would stop being slower.")
    print()


if __name__ == "__main__":
    main()

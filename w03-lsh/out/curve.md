# Task 2: measured crossover and scaling

## Machine and procedure (A1, A2, A6)

Measured on 7 October 2026: 11th Gen Intel(R) Core(TM) i7-1165G7 @ 2.80GHz; 15.68 GiB usable RAM (nominally 16 GB); Windows-11-10.0.26200-SP0; Python 3.12.6.

Whale browser, ChatGPT/Codex, Windows Defender and normal Windows services running; no other benchmark launched concurrently. The machine was not an isolated benchmark environment.

There are 7 distinct sizes from 64 to 4096 (64x). Documents are generated with seed 246, 60 shingles and a vocabulary of 5,000. Both methods receive the same input and threshold 0.6. Generation occurs before timing; LSH signature construction and candidate filtering are inside timing. No benchmark was run concurrently.

The provided measurement script used `bench.build()[:n]`, which could never generate more than 2,120 documents. Task 2 now has its own fixed-seed generator that makes exactly n documents with min(120, n//10) planted clones. `actual_n` and the assertion `brute_calls == n*(n-1)//2` verify the size; the Task 3 `bench.py` is unchanged.

## Time and peak allocation table (A3, A5)

These are the first measurements at each size; repeats are retained below and in the JSON, rather than replaced with more convenient numbers.

| n | Brute seconds | LSH seconds | Brute comparisons | LSH comparisons | Brute peak KiB | LSH peak MiB |
|---:|---:|---:|---:|---:|---:|---:|
| 64 | 0.0216 | 1.1485 | 2,016 | 6 | 7.73 | 0.81 |
| 128 | 0.1055 | 1.4355 | 8,128 | 12 | 7.73 | 1.43 |
| 256 | 0.2729 | 1.9931 | 32,640 | 29 | 9.23 | 2.14 |
| 512 | 1.1372 | 2.2394 | 130,816 | 52 | 10.82 | 3.34 |
| 1,024 | 4.7486 | 2.6999 | 523,776 | 119 | 19.79 | 5.43 |
| 2,048 | 41.8052 | 12.8580 | 2,096,128 | 133 | 21.95 | 9.37 |
| 4,096 | 192.4830 | 19.0974 | 8,386,560 | 157 | 22.29 | 17.07 |

At the largest completed size n=4,096, peak traced allocation was 22,824 bytes for brute force and 17,904,120 bytes for LSH. These peaks cover allocations inside `find`, including its result, and exclude the already-built input documents. They are not total process RAM or peak system memory. `tracemalloc` was enabled for both methods, so the reported times include profiling overhead; brute force holds little scratch state, while LSH stores row IDs, memberships, signatures and buckets.

## Check the quadratic claim with the measurements (A4)

| Size doubled | Brute time ratio | Brute comparison ratio |
|---|---:|---:|
| 64 -> 128 | 4.89x | 4.032x |
| 128 -> 256 | 2.59x | 4.016x |
| 256 -> 512 | 4.17x | 4.008x |
| 512 -> 1,024 | 4.18x | 4.004x |
| 1,024 -> 2,048 | 8.80x | 4.002x |
| 2,048 -> 4,096 | 4.60x | 4.001x |

The 256->512 and 512->1,024 time ratios are 4.17x and 4.18x, close to the expected 4x. Other timings do not all fit that constant-factor model. The comparison counts do: each is exactly n(n-1)/2. Doubling work therefore approaches 4x, but the wall-clock constants were unstable in this session.

To investigate, the same fixed-seed 1,024 and 2,048 inputs were measured again, with process CPU time added to distinguish computation from time spent waiting for scheduling. Both repeats and their peaks are preserved:

| Follow-up n | Brute wall s | Brute CPU s | LSH wall s | LSH CPU s |
|---:|---:|---:|---:|---:|
| 1,024 | 10.5025 | 10.1094 | 12.1272 | 11.3438 |
| 2,048 | 61.6137 | 59.1875 | 4.6580 | 4.3906 |
| 4,096 | 192.4830 | 182.1719 | 19.0974 | 16.2969 |

The repeated 1,024->2,048 brute time ratio was 5.87x. CPU time was close to wall time, so off-CPU scheduling delay alone does not explain the variation. The actual document counts and comparison counts rule out the original truncation bug. Power/frequency changes, cache/allocation effects, profiling overhead and background applications are plausible contributors; their individual contributions were not isolated. These measurements support quadratic comparison growth, not an assertion that every observed time quadrupled. A precise timing threshold would need controlled repeated trials.

## Crossover and startup cost (A7, A8)

In the first sweep, brute force won at n=512 (1.14s versus 2.24s); LSH first won at the sampled n=1,024 (2.70s versus 4.75s). That sweep brackets a crossing between 512 and 1,024. On repeating n=1,024, brute force won again, while LSH won at repeated n=2,048. Thus the observed crossing region across trials is 512-2,048; n=1,024 is the first sweep's sampled crossover, not a stable hardware constant.

For small n, LSH pays to map shingles into row IDs, build the row membership index, evaluate 120 hashes for each occupied row, update document signatures, form 30 band keys per document, and allocate bucket/candidate sets. Brute force can immediately compare its few pairs. The LSH preprocessing is roughly linear in document count for fixed signature/shingle lengths, but its constant and its traced allocation cost are substantial.

## Where the machine became unpleasant (A2)

The first recorded one-minute wait occurred at n=2,048: brute force took 61.61s, versus 4.66s for LSH. Time became unpleasant before memory; no out-of-memory error was observed. The largest completed measurement was n=4,096, taking 192.48s for brute force and 19.10s for LSH. No RAM exhaustion limit is claimed.

## Reproduce

From `w03-lsh/`, using the installed Windows Python launcher:

```powershell
py -3 task2_crossover.py --sizes 64,128,256,512,1024,2048 --background 'Describe other running apps'
py -3 task2_crossover.py --sizes 1024,2048,4096 --background 'Describe other running apps'
```

The script appends new measurements; older measurements are preserved.

# Week 3 observations

## Task 1
The textbook example passed: each row's hashes are computed once and shared across its present columns, instead of rescanning per column; the supplied column sets are indexed by row using O(nnz) extra space, which a row-stream input could avoid.
If signature length is not divisible by bands, I raise ValueError instead of dropping leftover rows; empty-set Jaccard is 0.
S1/S4 have a two-hash estimate of 1.0 but true Jaccard 2/3: increasing the hash count reduces sampling variation (approximately 1/sqrt(k)), at the cost of O(kD) signatures and more updates.

## Task 2
On an i7-1165G7 with 15.68 GiB RAM, Windows 11/Python 3.12.6 and browser/Codex/background services running, 7 sizes spanned 64-4096 (64x); LSH first won at sampled n=1,024, but repeat timing moved the crossing into a wider 512-2,048 region.
Brute comparisons followed n(n-1)/2 exactly; the 256->512 and 512->1,024 time ratios were 4.17x and 4.18x, whereas repeats varied, so I do not claim every measured time quadrupled (details in curve.md).
Time became unpleasant first at n=2,048 (61.61s brute); at largest n=4,096, traced peaks were 22,824 bytes brute/17,904,120 bytes LSH, excluding input data, with no RAM exhaustion observed.

## Task 3
With k=120, b=30, r=4, the S-curve step is (1/30)^(1/4)=0.4273 and P(candidate|s=0.6)=1-(1-0.6^4)^30=0.9845; placing the step below 0.6 favors recall and permits some extra candidates.
The unchanged benchmark found all 121 true pairs with 125 comparisons versus 2,246,140 (100% recall/precision, 99.9944% avoided); moving to b=6, r=20 put the step at 0.9143 and reduced recall to 7/121=5.79%, showing the price of overly strict bands.
Comparison-only scoring hides hashing/index/signature costs: they already dominate at small n in Task 2, and at millions of documents O(nk) signature/index memory and memory bandwidth can become limiting even with few final comparisons.

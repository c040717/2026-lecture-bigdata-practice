#!/usr/bin/env python3
"""Week 3 · Task 1 — Minhash and LSH, built from the matrix up.

Textbook §3.2 - §3.4.

Comparing every pair is quadratic, so it stops being possible somewhere around
a hundred thousand documents. The way out is two ideas stacked:

    minhash   replace a set with a short signature, such that the chance two
              signatures agree in a position equals their Jaccard similarity
    LSH       hash bands of those signatures so that similar pairs collide and
              you only ever compare the ones that did

You build both. The textbook's §3.3.5 example is small enough to check by hand,
and the harness checks you against it.

    python3 task1_minhash.py --verify
"""
import argparse
from itertools import combinations

# §3.3.5. Rows are elements 0..4, columns are the sets S1..S4.
BOOK = [[1, 0, 0, 1],
        [0, 0, 1, 0],
        [0, 1, 0, 1],
        [1, 0, 1, 1],
        [0, 0, 1, 0]]
# The two hash functions the textbook uses on the row numbers.
BOOK_HASHES = [lambda r: (r + 1) % 5, lambda r: (3 * r + 1) % 5]


def jaccard(a, b):
    """|a and b| / |a or b|. Empty union is 0, not an error."""
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def minhash_signatures(columns, hashes, n_rows):
    """Build the signature matrix, one pass over the rows.

    `columns` is [set_of_row_numbers, ...], one entry per document.
    Return [[sig for each hash] for each column].

    The algorithm in §3.3.5 walks each row **once** and updates the signature
    of every column that has a 1 in it:

        sig[h][c] = min(sig[h][c], h(r))

    Doing it that way is the point. If you sort or re-scan per column you have
    written something correct that does not survive a dataset that does not fit
    in memory, and not fitting in memory is what this course is about.
    """
    if n_rows < 0:
        raise ValueError("n_rows must be non-negative")
    hashes = list(hashes)
    signatures = [[float("inf")] * len(hashes) for _ in columns]

    # 각 행의 원소가 들어 있는 열 목록을 만든다.
    # 행별 해시값을 한 번 계산해서 해당 열들의 최솟값을 갱신한다.
    row_columns = {}
    for column, rows in enumerate(columns):
        for row in rows:
            if not isinstance(row, int) or not 0 <= row < n_rows:
                raise ValueError("row numbers must be in [0, n_rows)")
            row_columns.setdefault(row, []).append(column)
    for row in range(n_rows):
        present = row_columns.get(row)
        if not present:
            continue
        values = [h(row) for h in hashes]
        for column in present:
            signature = signatures[column]
            for position, value in enumerate(values):
                if value < signature[position]:
                    signature[position] = value
    return signatures


def lsh_candidates(signatures, bands):
    """Split each signature into `bands` bands and hash each band.

    Two columns are candidates if they land in the same bucket for **at least
    one** band. Return {(i, j), ...} with i < j.

    The signature length must divide evenly by `bands`, or you have to decide
    what to do with the remainder. Say what you decided.
    """
    if not isinstance(bands, int) or bands <= 0:
        raise ValueError("bands must be a positive integer")
    if not signatures:
        return set()
    length = len(signatures[0])
    if not length or length % bands:
        # 남는 행을 버리지 않고 잘못된 band 수를 오류로 처리한다.
        raise ValueError("signature length must be positive and divisible by bands")
    if any(len(signature) != length for signature in signatures):
        raise ValueError("all signatures must have the same length")
    rows_per_band = length // bands
    candidates = set()
    for band in range(bands):
        start = band * rows_per_band
        buckets = {}
        for column, signature in enumerate(signatures):
            key = tuple(signature[start:start + rows_per_band])
            buckets.setdefault(key, []).append(column)
        for bucket in buckets.values():
            candidates.update(combinations(bucket, 2))
    return candidates


# ------------------------------------------------------------------- harness
def columns_from_matrix(matrix):
    n_rows, n_cols = len(matrix), len(matrix[0])
    return [{r for r in range(n_rows) if matrix[r][c]} for c in range(n_cols)]


def verify():
    fails = 0

    def check(label, got, want):
        nonlocal fails
        ok = got == want
        print(f"  {'ok  ' if ok else 'FAIL'}  {label:<44} {got}"
              + ("" if ok else f"\n{'':>54}want {want}"))
        fails += not ok

    cols = columns_from_matrix(BOOK)
    try:
        # S1 = {0,3}, S4 = {0,2,3}: intersection 2, union 3
        check("jaccard(S1, S4)", round(jaccard(cols[0], cols[3]), 4), round(2 / 3, 4))
        check("jaccard(S1, S2)", jaccard(cols[0], cols[1]), 0.0)
        check("jaccard on empty sets", jaccard(set(), set()), 0)
    except NotImplementedError:
        print("  jaccard is still a stub"); return 1

    try:
        sig = minhash_signatures(cols, BOOK_HASHES, len(BOOK))
    except NotImplementedError:
        print("  minhash_signatures is still a stub"); return 1

    # Figure 3.4 in the textbook.
    check("signature of S1", sig[0], [1, 0])
    check("signature of S2", sig[1], [3, 2])
    check("signature of S3", sig[2], [0, 0])
    check("signature of S4", sig[3], [1, 0])

    try:
        cands = lsh_candidates([[1, 0], [3, 2], [0, 0], [1, 0]], bands=2)
    except NotImplementedError:
        print("  lsh_candidates is still a stub"); return 1
    # With one row per band, S1 and S4 are identical, so they must collide.
    check("S1 and S4 are candidates", (0, 3) in cands, True)
    check("S1 and S2 are not", (0, 1) in cands, False)

    print(f"\n  {'all ok' if not fails else str(fails) + ' failed'}")
    if not fails:
        print("  Note that S1 and S4 agree in both signature positions, which "
              "estimates\n  their similarity as 1.0 when it is actually 2/3. "
              "Two hashes is not many.")
    return 1 if fails else 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--verify", action="store_true")
    a = p.parse_args()
    raise SystemExit(verify() if a.verify else p.print_help())

#!/usr/bin/env python3
"""Week 6 · Task 3 — Make pass two fit.

Textbook §6.3 (PCY), §6.3.2 - §6.3.4.

`PlainApriori` does what Task 1 asked: use pass one to drop infrequent items,
then count every pair of surviving items. That is already much better than
counting all pairs. It is still not enough, because the surviving items are the
common ones, and the common ones appear together constantly.

The harness measures **the peak number of pair counters you held**, because
that is the thing that decides whether the algorithm runs at all. §6.3 is about
spending pass one's spare memory to shrink it.

    python3 bench.py
    python3 bench.py --yours

Correctness first: you must find exactly the same frequent pairs. Finding fewer
is not an optimisation.
"""
from collections import Counter
from itertools import combinations
from array import array


class PlainApriori:
    """Pass one drops infrequent items. Pass two counts every surviving pair."""

    def __init__(self, support):
        self.support = support
        self.peak_counters = 0

    def run(self, baskets):
        counts = Counter()
        for basket in baskets:
            counts.update(basket)
        frequent = {i for i, c in counts.items() if c >= self.support}

        pair_counts = Counter()
        for basket in baskets:
            items = sorted(basket & frequent)
            for pair in combinations(items, 2):
                pair_counts[pair] += 1
            self.peak_counters = max(self.peak_counters, len(pair_counts))

        return {frozenset(p): c for p, c in pair_counts.items()
                if c >= self.support}


class YourAlgorithm:
    """Your frequent-pair finder.

        __init__(support)
        run(baskets) -> {frozenset({a, b}): count}
        .peak_counters -> the most pair counters you ever held at once

    Same pairs as the baseline. Fewer counters.

    Pass one only needs one integer per item, and there are not many items. The
    rest of your memory is sitting idle while you do it. §6.3 spends it: hash
    every pair you see in pass one into a fixed array of buckets, and count the
    buckets rather than the pairs.

    A bucket whose total is below the support threshold cannot contain a
    frequent pair. In pass two you skip every pair landing in such a bucket -
    and the bucket array collapses to a bitmap, one bit each, before you need
    the memory for counters.

    Two things to be careful of:

      * a bucket being frequent does not make its pairs frequent. It is a
        filter, not an answer
      * `peak_counters` is on your honour. Count the pair counters you hold at
        the same time. The bitmap is not a pair counter, but if you keep the
        full bucket counts alive into pass two, that is not free either -
        observation.md asks about it
    """

    def __init__(self, support, bucket_count=1 << 20):
        if support < 1 or support > 0xffffffff or bucket_count < 1:
            raise ValueError("support and bucket_count must be positive; support must fit uint32")
        self.support = support
        self.bucket_count = bucket_count
        self.peak_counters = 0
        self.pass2_peak_counters = 0
        self.bucket_bytes = 0
        self.bitmap_bytes = 0
        self.frequent_buckets = 0

    def run(self, baskets):
        self.peak_counters = self.pass2_peak_counters = 0
        ids, labels = {}, []
        counts = Counter()
        buckets = array("I", [0]) * self.bucket_count
        self.bucket_bytes = len(buckets) * buckets.itemsize

        # 항목 이름 대신 정수 번호로 해싱해 실행마다 같은 버킷을 사용한다.
        for basket in baskets:
            items = []
            for item in sorted(set(basket)):
                if item not in ids:
                    ids[item] = len(labels)
                    labels.append(item)
                items.append(ids[item])
            items.sort()
            counts.update(items)
            for a, b in combinations(items, 2):
                bucket = ((a * 1000003) ^ (b * 9176)) % self.bucket_count
                # 임계값 이상인지 여부만 필요하므로 그 이상은 올리지 않는다.
                if buckets[bucket] < self.support:
                    buckets[bucket] += 1

        frequent = {item for item, count in counts.items() if count >= self.support}
        bitmap = bytearray((self.bucket_count + 7) // 8)
        self.bitmap_bytes = len(bitmap)
        self.frequent_buckets = 0
        for bucket, count in enumerate(buckets):
            if count >= self.support:
                bitmap[bucket >> 3] |= 1 << (bucket & 7)
                self.frequent_buckets += 1
        # 2패스에서는 정수 버킷 배열을 보관하지 않고 비트맵만 남긴다.
        del buckets, counts

        pair_counts = Counter()
        for basket in baskets:
            items = sorted(ids[item] for item in set(basket) if ids[item] in frequent)
            for a, b in combinations(items, 2):
                bucket = ((a * 1000003) ^ (b * 9176)) % self.bucket_count
                if bitmap[bucket >> 3] & (1 << (bucket & 7)):
                    pair_counts[(a, b)] += 1
        self.pass2_peak_counters = self.peak_counters = len(pair_counts)

        result = {}
        # 기존 카운터를 꺼내 옮겨 후보 사전과 결과 사전에 중복 보관하지 않는다.
        while pair_counts:
            (a, b), count = pair_counts.popitem()
            if count >= self.support:
                result[frozenset((labels[a], labels[b]))] = count
        return result

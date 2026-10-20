#!/usr/bin/env python3
"""Week 5 · Task 3 — PageRank on a graph that will not fit as a matrix.

Textbook §5.2 (efficient PageRank), §5.2.1 - §5.2.3.

`DenseMatrix` is PageRank written the way the equations are written: build the
transition matrix M, multiply. It is correct, it is easy to read, and it stores
n^2 numbers for a graph with almost no edges.

The web's matrix is about 99.9999% zeros. Storing them is the problem, and
§5.2 is the chapter about not doing that.

    python3 bench.py
    python3 bench.py --yours

Correctness first: the harness compares your ranks against the dense version
element by element. A fast PageRank that ranks pages differently is a different
algorithm, not a faster one.
"""


class DenseMatrix:
    """PageRank as written in the equations. Stores n^2 floats."""

    def __init__(self, beta=0.85, tol=1e-10, max_iter=100):
        self.beta, self.tol, self.max_iter = beta, tol, max_iter

    def run(self, graph):
        nodes = list(graph)
        n = len(nodes)
        index = {v: i for i, v in enumerate(nodes)}

        # the full transition matrix, zeros and all
        M = [[0.0] * n for _ in range(n)]
        for v, outs in graph.items():
            if outs:
                share = 1.0 / len(outs)
                for w in outs:
                    M[index[w]][index[v]] = share
            else:
                for i in range(n):           # dead end: spread it everywhere
                    M[i][index[v]] = 1.0 / n

        r = [1.0 / n] * n
        for self.iterations in range(1, self.max_iter + 1):
            nr = [0.0] * n
            for i in range(n):
                row = M[i]
                s = 0.0
                for j in range(n):
                    if row[j]:
                        s += row[j] * r[j]
                nr[i] = self.beta * s + (1 - self.beta) / n
            delta = sum(abs(a - b) for a, b in zip(nr, r))
            r = nr
            if delta < self.tol:
                break
        return {v: r[index[v]] for v in nodes}

    def memory_floats(self):
        return getattr(self, "_n", 0) ** 2


class YourPageRank:
    """Your PageRank.

        __init__(beta=0.85, tol=1e-10, max_iter=100)
        run(graph) -> {node: rank}
        memory_floats() -> the largest number of floats you held at once

    Same ranks, to within 1e-9 per node. Far less memory.

    `graph` is {node: [out-neighbours]}. Note what that already is: an adjacency
    list, which is the sparse representation. The dense version throws that
    structure away and then pays to get it back.

    Two things to be careful about, and they are the same two as Task 1:

      * dead ends, whose rank has to go somewhere
      * the teleport term, which touches every node and is therefore the one
        part that looks like it needs a dense operation - it does not, and
        working out why is the point of §5.2.3

    `memory_floats()` is on your honour and the harness reads it. Count the
    numbers you actually hold at once.
    """

    def __init__(self, beta=0.85, tol=1e-10, max_iter=100):
        self.beta, self.tol, self.max_iter = beta, tol, max_iter
        self.iterations = 0
        self._peak_floats = 2  # beta and tol; no graph workspace yet

    def run(self, graph):
        n = len(graph)
        self.iterations = 0
        self._peak_floats = 2
        if not n:
            return {}

        # Keep the input adjacency list and two rank vectors, never an n x n
        # matrix. Dictionaries also support the graph's original node labels.
        ranks = dict.fromkeys(graph, 1.0 / n)
        next_ranks = dict.fromkeys(graph, 0.0)
        self._peak_floats = 2 * n + 8

        for self.iterations in range(1, self.max_iter + 1):
            dangling = sum(ranks[v] for v, outs in graph.items() if not outs)
            base = (1.0 - self.beta + self.beta * dangling) / n
            for v in next_ranks:
                next_ranks[v] = base

            # Follow only existing edges. The common teleport/dead-end term
            # above needs one scalar and an O(n) fill, not n squared entries.
            for v, outs in graph.items():
                if outs:
                    share = self.beta * ranks[v] / len(outs)
                    for w in outs:
                        next_ranks[w] += share

            delta = sum(abs(next_ranks[v] - ranks[v]) for v in graph)
            ranks, next_ranks = next_ranks, ranks
            if delta < self.tol:
                break

        return ranks

    def memory_floats(self):
        # Count numeric storage slots, not Python object bytes: 2n rank values
        # plus a conservative eight scalar slots (parameters, dangling mass,
        # base, share, delta and two temporary/reduction values). Adjacency
        # already belongs to the caller and contains no transition floats.
        return self._peak_floats

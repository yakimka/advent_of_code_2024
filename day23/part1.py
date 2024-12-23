#!/usr/bin/env python3
from __future__ import annotations

import sys
import timeit
from pathlib import Path

import pytest

import support as sup

INPUT_TXT = Path(__file__).parent / "input.txt"


def compute(s: str) -> int:
    graph = {}
    for line in s.splitlines():
        copm1, comp2 = line.split("-")
        graph.setdefault(copm1, set()).add(comp2)
        graph.setdefault(comp2, set()).add(copm1)

    union_find = UnionFind(graph)
    cycles = union_find.find_n_cycles(3)
    return sum(int(any(key.startswith("t") for key in cycle)) for cycle in cycles)


class UnionFind:
    def __init__(self, graph):
        self.parent = {}
        self.rank = {}
        self.graph = graph
        self.cycles = set()

        for node in graph:
            self.parent[node] = node
            self.rank[node] = 0

    def find(self, node):
        if self.parent[node] != node:
            self.parent[node] = self.find(self.parent[node])  # Path compression
        return self.parent[node]

    def union(self, node1, node2):
        root1 = self.find(node1)
        root2 = self.find(node2)

        if root1 != root2:
            if self.rank[root1] > self.rank[root2]:
                self.parent[root2] = root1
            elif self.rank[root1] < self.rank[root2]:
                self.parent[root1] = root2
            else:
                self.parent[root2] = root1
                self.rank[root1] += 1

    def dfs(self, path, start_node, n):
        if len(path) == n:
            if start_node in self.graph[path[-1]]:
                self.cycles.add(tuple(sorted(path)))
            return

        for neighbor in self.graph[path[-1]]:
            if neighbor not in path:
                self.dfs(path + [neighbor], start_node, n)

    def find_n_cycles(self, n):
        visited_edges = set()

        for node in self.graph:
            for neighbor in self.graph[node]:
                if (node, neighbor) not in visited_edges and (
                    neighbor,
                    node,
                ) not in visited_edges:
                    visited_edges.add((node, neighbor))
                    self.union(node, neighbor)

        for node in self.graph:
            self.dfs([node], node, n)

        return self.cycles


INPUT_S = """\
kh-tc
qp-kh
de-cg
ka-co
yn-aq
qp-ub
cg-tb
vc-aq
tb-ka
wh-tc
yn-cg
kh-ub
ta-co
de-co
tc-td
tb-wq
wh-td
ta-ka
td-qp
aq-cg
wq-ub
ub-vc
de-ta
wq-aq
wq-vc
wh-yn
ka-de
kh-ta
co-tc
wh-qp
tb-vc
td-yn
"""
EXPECTED = 7


@pytest.mark.parametrize(
    "input_s,expected",
    [
        (INPUT_S, EXPECTED),
    ],
)
def test_debug(input_s: str, expected: int) -> None:
    assert compute(input_s) == expected


def test_input() -> None:
    result = compute(read_input())

    assert result == 1419


def read_input() -> str:
    with open(INPUT_TXT) as f:
        return f.read()


if __name__ == "__main__":
    input_data = read_input()
    print("Answer is:     ", compute(input_data))

    if "-b" in sys.argv:
        number_of_runs = 100
        bench_time = timeit.timeit(
            "compute(data)",
            setup="from __main__ import compute",
            globals={"data": input_data},
            number=number_of_runs,
        )
        print(f"{number_of_runs} runs took: {bench_time}s")
        one_run = sup.humanized_seconds(bench_time / number_of_runs)
        print(f"Average time:   {one_run}")

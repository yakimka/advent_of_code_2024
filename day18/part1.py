#!/usr/bin/env python3
from __future__ import annotations

import sys
import timeit
from pathlib import Path

import pytest

import support as sup

INPUT_TXT = Path(__file__).parent / "input.txt"


def compute(s: str, max_coord: int = 70, bytes_count: int = 1024) -> int:
    coords = []
    for line in s.splitlines():
        coords.append(tuple(map(int, line.split(","))))

    start = (0, 0)
    end = (max_coord, max_coord)

    grid = [["." for _ in range(max_coord + 1)] for _ in range(max_coord + 1)]
    for m, n in coords[:bytes_count]:
        grid[m][n] = "#"
    matrix = sup.Matrix(grid)

    graph = {}
    for i, row in enumerate(matrix):
        for j, cell in enumerate(row):
            for n_i, n_j in matrix.neighbors_cross(i, j):
                if matrix[n_i][n_j] == "#":
                    continue
                graph.setdefault((i, j), {})[(n_i, n_j)] = 1

    dest, _ = sup.dijkstra(graph, start)
    return dest[end]


INPUT_S = """\
5,4
4,2
4,5
3,0
2,1
6,3
2,4
1,5
0,6
3,3
2,6
5,1
1,2
5,5
2,5
6,5
1,4
0,4
6,4
1,1
6,1
1,0
0,5
1,6
2,0
"""
EXPECTED = 22


@pytest.mark.parametrize(
    "input_s,expected",
    [
        (INPUT_S, EXPECTED),
    ],
)
def test_debug(input_s: str, expected: int) -> None:
    assert compute(input_s, 6, 12) == expected


def test_input() -> None:
    result = compute(read_input())

    assert result == 296


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

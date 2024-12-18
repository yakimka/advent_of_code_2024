#!/usr/bin/env python3
from __future__ import annotations

import sys
import timeit
from pathlib import Path

import pytest

import support as sup

INPUT_TXT = Path(__file__).parent / "input.txt"


def compute(s: str, max_coord: int = 70, bytes_count: int = 1024) -> str:
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

    for byte in coords[bytes_count:]:
        add_new_byte(byte, matrix, graph)
        _, prev = sup.dijkstra(graph, start)
        if prev.get(end) is None:
            return f"{byte[0]},{byte[1]}"

    raise ValueError("No solution found")


def add_new_byte(byte: tuple[int, int], matrix: sup.Matrix, graph: dict):
    m, n = byte
    matrix[m][n] = "#"
    # remove paths from this byte
    del graph[(m, n)]
    # remove paths to this byte
    for neighbor in matrix.neighbors_cross(m, n):
        if neighbor in graph:
            graph[neighbor].pop((m, n), None)


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
EXPECTED = "6,1"


@pytest.mark.parametrize(
    "input_s,expected",
    [
        (INPUT_S, EXPECTED),
    ],
)
def test_debug(input_s: str, expected: str) -> None:
    assert compute(input_s, 6, 12) == expected


def test_input() -> None:
    result = compute(read_input())

    assert result == "28,44"


def read_input() -> str:
    with open(INPUT_TXT) as f:
        return f.read()


if __name__ == "__main__":
    input_data = read_input()
    print("Answer is:     ", compute(input_data))

    if "-b" in sys.argv:
        number_of_runs = 10
        bench_time = timeit.timeit(
            "compute(data)",
            setup="from __main__ import compute",
            globals={"data": input_data},
            number=number_of_runs,
        )
        print(f"{number_of_runs} runs took: {bench_time}s")
        one_run = sup.humanized_seconds(bench_time / number_of_runs)
        print(f"Average time:   {one_run}")

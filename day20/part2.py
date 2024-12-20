#!/usr/bin/env python3
from __future__ import annotations

import sys
import timeit
from pathlib import Path

import pytest

import support as sup

INPUT_TXT = Path(__file__).parent / "input.txt"


def compute(s: str, min_save: int = 100) -> int:
    matrix_data = []
    start = end = None
    for m, line in enumerate(s.splitlines()):
        for n, char in enumerate(line):
            if char == "S":
                start = (m, n)
            elif char == "E":
                end = (m, n)
        matrix_data.append(list(line))

    matrix = sup.Matrix(matrix_data)
    graph = make_graph(matrix, start)

    dist, prev = sup.dijkstra(graph, start)
    path = parse_path(prev, end)

    cheats = 0
    for node in path:
        m, n = node
        for cheat_idx in range(21):
            for neighbor in neighbors(matrix, m, n, cheat_idx):
                if neighbor not in dist or node not in dist:
                    continue
                cartesian_dist = sup.cartesian_shortest_path(node, neighbor)
                if (dist[neighbor] - dist[node]) - cartesian_dist >= min_save:
                    cheats += 1
    return cheats


def neighbors(matrix: sup.Matrix, m, n, size):
    points = set()
    for dx in range(-size, size + 1):
        dy = size - abs(dx)
        points.add((m + dx, n + dy))
        points.add((m + dx, n - dy))
    return list(sup.filter_neighbors(points, max_bounds=matrix.bounds))


def parse_path(prev, end) -> list[tuple[int, int]]:
    path = []
    while end:
        path.append(end)
        end = prev[end]
    return path[::-1]


def make_graph(
    matrix: sup.Matrix, start: tuple[int, int]
) -> dict[tuple[int, int], dict[tuple[int, int], int]]:
    graph = {}
    stack = [start]
    while stack:
        m, n = stack.pop()
        for n_m, n_n in matrix.neighbors_cross(m, n):
            if matrix[n_m][n_n] == "#":
                continue
            graph.setdefault((m, n), {})[(n_m, n_n)] = 1
            if (n_m, n_n) not in graph:
                stack.append((n_m, n_n))
    return graph


INPUT_S = """\
###############
#...#...#.....#
#.#.#.#.#.###.#
#S#...#.#.#...#
#######.#.#.###
#######.#.#...#
#######.#.###.#
###..E#...#...#
###.#######.###
#...###...#...#
#.#####.#.###.#
#.#...#.#.#...#
#.#.#.#.#.#.###
#...#...#...###
###############
"""
EXPECTED = 285


@pytest.mark.parametrize(
    "input_s,expected",
    [
        (INPUT_S, EXPECTED),
    ],
)
def test_debug(input_s: str, expected: int) -> None:
    assert compute(input_s, 50) == expected


def test_input() -> None:
    result = compute(read_input())

    assert result == 989316


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

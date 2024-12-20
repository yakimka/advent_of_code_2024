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

    from_start_dist, from_start_prev = sup.dijkstra(graph, start)
    to_end_dist, to_end_prev = sup.dijkstra(graph, end)
    candidates = get_candidates(matrix)
    optimal_path_len = from_start_dist[end]

    cheats = set()
    for from_start, obstacle, to_end in candidates:
        from_start_val = from_start_dist.get(from_start)
        to_end_val = to_end_dist.get(to_end)
        if from_start_val is None or to_end_val is None:
            continue

        new_path_len = from_start_val + to_end_val + 1
        if new_path_len < optimal_path_len - min_save:
            cheats.add((obstacle, to_end))

    return len(cheats)


DIRECTION_PAIRS = [
    (sup.Direction.UP, sup.Direction.DOWN),
    (sup.Direction.DOWN, sup.Direction.UP),
    (sup.Direction.LEFT, sup.Direction.RIGHT),
    (sup.Direction.RIGHT, sup.Direction.LEFT),
]


def get_candidates(
    matrix: sup.Matrix,
) -> list[tuple[tuple[int, int], tuple[int, int], tuple[int, int]]]:
    candidates = []
    for m, line in enumerate(matrix):
        for n, char in enumerate(line):
            if matrix[m][n] != "#":
                continue
            for d1, d2 in DIRECTION_PAIRS:
                from_start = matrix.next_coords(m, n, d1)
                to_end = matrix.next_coords(m, n, d2)
                if not from_start or not to_end:
                    continue
                from_start_val = matrix[from_start[0]][from_start[1]]
                to_end_val = matrix[to_end[0]][to_end[1]]
                if from_start_val == "#" or to_end_val == "#":
                    continue
                candidates.append((from_start, (m, n), to_end))
    return candidates


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
EXPECTED = 30


@pytest.mark.parametrize(
    "input_s,expected",
    [
        (INPUT_S, EXPECTED),
    ],
)
def test_debug(input_s: str, expected: int) -> None:
    assert compute(input_s, 4) == expected


def test_input() -> None:
    result = compute(read_input())

    assert result == 1286


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

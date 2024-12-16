#!/usr/bin/env python3
from __future__ import annotations

import heapq
import sys
import timeit
from pathlib import Path

import pytest

import support as sup

INPUT_TXT = Path(__file__).parent / "input.txt"


def compute(s: str) -> int:
    matrix_data = []
    start = None
    end = None
    for m, line in enumerate(s.splitlines()):
        matrix_data.append([])
        for n, char in enumerate(line):
            matrix_data[m].append(char)
            if char == "S":
                start = (m, n)
            elif char == "E":
                end = (m, n)

    matrix = sup.Matrix(matrix_data)

    return search_shortest_path_score(matrix, start, end)


DIRECTIONS = [
    sup.Direction.UP,
    sup.Direction.RIGHT,
    sup.Direction.DOWN,
    sup.Direction.LEFT,
]


def search_shortest_path_score(
    matrix: sup.Matrix, start: tuple[int, int], end: tuple[int, int]
) -> int:
    dist = {start: 0}
    prev = {start: None}
    pq = [(0, start, sup.Direction.RIGHT)]
    while pq:
        _, u, direction = heapq.heappop(pq)
        neighbors = []
        for next_direction in DIRECTIONS:
            m, n = u
            next_m, next_n = matrix.next_coords(m, n, next_direction)
            if matrix[next_m][next_n] == "#":
                continue
            score = 1001
            if direction.x == next_direction.x or direction.y == next_direction.y:
                score = 1
            neighbors.append(((next_m, next_n), score, next_direction))

        for vertex, val, dir in neighbors:
            if vertex not in dist or dist[u] + val < dist[vertex]:
                dist[vertex] = dist[u] + val
                prev[vertex] = u
                heapq.heappush(pq, (dist[vertex], vertex, dir))

    return dist[end]


INPUT_S1 = """\
###############
#.......#....E#
#.#.###.#.###.#
#.....#.#...#.#
#.###.#####.#.#
#.#.#.......#.#
#.#.#####.###.#
#...........#.#
###.#.#####.#.#
#...#.....#.#.#
#.#.#.###.#.#.#
#.....#...#.#.#
#.###.#.#.#.#.#
#S..#.....#...#
###############
"""
EXPECTED1 = 7036
INPUT_S2 = """\
#################
#...#...#...#..E#
#.#.#.#.#.#.#.#.#
#.#.#.#...#...#.#
#.#.#.#.###.#.#.#
#...#.#.#.....#.#
#.#.#.#.#.#####.#
#.#...#.#.#.....#
#.#.#####.#.###.#
#.#.#.......#...#
#.#.###.#####.###
#.#.#...#.....#.#
#.#.#.#####.###.#
#.#.#.........#.#
#.#.#.#########.#
#S#.............#
#################
"""
EXPECTED2 = 11048


@pytest.mark.parametrize(
    "input_s,expected",
    [
        (INPUT_S1, EXPECTED1),
        (INPUT_S2, EXPECTED2),
    ],
)
def test_debug(input_s: str, expected: int) -> None:
    assert compute(input_s) == expected


def test_input() -> None:
    result = compute(read_input())

    assert result == 95444


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

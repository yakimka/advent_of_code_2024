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

    return search_shortest_path_score(matrix, (*start, sup.Direction.RIGHT), end)


DIRECTIONS = [
    sup.Direction.UP,
    sup.Direction.RIGHT,
    sup.Direction.DOWN,
    sup.Direction.LEFT,
]

SUBDIRECTIONS = {
    sup.Direction.UP: [sup.Direction.UP, sup.Direction.LEFT, sup.Direction.RIGHT],
    sup.Direction.RIGHT: [sup.Direction.RIGHT, sup.Direction.UP, sup.Direction.DOWN],
    sup.Direction.DOWN: [sup.Direction.DOWN, sup.Direction.LEFT, sup.Direction.RIGHT],
    sup.Direction.LEFT: [sup.Direction.LEFT, sup.Direction.UP, sup.Direction.DOWN],
}


def search_shortest_path_score(
    matrix: sup.Matrix, start: tuple[int, int, sup.Direction], end: tuple[int, int]
) -> int:
    dist = {start: 0}
    prev = {start: set()}
    pq = [(0, start)]
    while pq:
        _, u = heapq.heappop(pq)
        m, n, direction = u
        neighbors = []
        subd = SUBDIRECTIONS[direction]
        next_m = m + subd[0].x
        next_n = n + subd[0].y
        if matrix[next_m][next_n] != "#":
            neighbors.append(((next_m, next_n, subd[0]), 1))
        neighbors.append(((m, n, subd[1]), 1000))
        neighbors.append(((m, n, subd[2]), 1000))

        for vertex, val in neighbors:
            if vertex not in dist or dist[u] + val <= dist[vertex]:
                dist[vertex] = dist[u] + val
                prev.setdefault(vertex, set()).add(u)
                heapq.heappush(pq, (dist[vertex], vertex))

    return len(get_path(prev, dist, end))


def get_path(
    prev: dict[tuple[int, int], set[tuple[int, int]]], dist, end: tuple[int, int]
) -> set[tuple[int, int]]:
    seen = set()
    path = set()
    end_vertexes = [
        (*end, dir_)
        for dir_ in (
            sup.Direction.UP,
            sup.Direction.RIGHT,
            sup.Direction.DOWN,
            sup.Direction.LEFT,
        )
    ]
    min_path_len = min(dist.get(vertex, float("inf")) for vertex in end_vertexes)
    stack = []
    for vertex in end_vertexes:
        if dist.get(vertex, float("inf")) == min_path_len:
            stack.append(vertex)

    while stack:
        vertex = stack.pop()
        m, n, _ = vertex
        path.add((m, n))
        for prev_vertex in prev.get(vertex, []):
            if prev_vertex not in seen:
                stack.append(prev_vertex)
    return path


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
EXPECTED1 = 45
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
EXPECTED2 = 64


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

    assert result == 513


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

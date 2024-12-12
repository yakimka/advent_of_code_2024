#!/usr/bin/env python3
from __future__ import annotations

import sys
import timeit
from pathlib import Path

import pytest

import support as sup

INPUT_TXT = Path(__file__).parent / "input.txt"


def compute(s: str) -> int:
    matrix = sup.Matrix.create_from_input(s)
    seen = set()
    total = 0
    for m, row in enumerate(matrix):
        for n, cell in enumerate(row):
            area, corners = calculate_area_and_corners(matrix, seen, m, n)
            total += area * corners

    return total


def calculate_area_and_corners(
    matrix: sup.Matrix, seen: set[tuple[int, int]], m: int, n: int
) -> tuple[int, int]:
    coords = (m, n)
    if coords in seen:
        return 0, 0

    seen.add(coords)

    value = matrix[m][n]
    neighbors = []
    area = 1
    corners = 0
    for i, item in enumerate(matrix.neighbors_cross_diag_all(m, n)):
        if item is None:
            neighbors.append(None)
            continue

        n_m, n_n = item
        if matrix[n_m][n_n] == value:
            neighbors.append("X")
        else:
            neighbors.append(None)

        if i % 2 != 0:  # skip diagonals
            next_m, next_n = item
            next_value = matrix[next_m][next_n]
            if next_value == value:
                next_area, next_corners = calculate_area_and_corners(
                    matrix, seen, next_m, next_n
                )
                area += next_area
                corners += next_corners
    corners += _calc_corners(neighbors)

    return area, corners


def _calc_corners(neighbors: list[str | None]) -> int:
    corners = 0
    for one, two, three in [(7, 0, 1), (1, 2, 3), (3, 4, 5), (5, 6, 7)]:
        if neighbors[one] is None and neighbors[three] is None:
            corners += 1
        if neighbors[two] is None and neighbors[one] and neighbors[three]:
            corners += 1

    return corners


INPUT_S1 = """\
AAAA
BBCD
BBCC
EEEC
"""
EXPECTED1 = 80
INPUT_S2 = """\
OOOOO
OXOXO
OOOOO
OXOXO
OOOOO
"""
EXPECTED2 = 436
INPUT_S3 = """\
RRRRIICCFF
RRRRIICCCF
VVRRRCCFFF
VVRCCCJFFF
VVVVCJJCFE
VVIVCCJJEE
VVIIICJJEE
MIIIIIJJEE
MIIISIJEEE
MMMISSJEEE
"""
EXPECTED3 = 1206
INPUT_S4 = """\
AAAAAA
AAABBA
AAABBA
ABBAAA
ABBAAA
AAAAAA
"""
EXPECTED4 = 368
INPUT_S5 = """\
EEEEE
EXXXX
EEEEE
EXXXX
EEEEE
"""
EXPECTED5 = 236


@pytest.mark.parametrize(
    "input_s,expected",
    [
        (INPUT_S1, EXPECTED1),
        (INPUT_S2, EXPECTED2),
        (INPUT_S3, EXPECTED3),
        (INPUT_S4, EXPECTED4),
        (INPUT_S5, EXPECTED5),
    ],
)
def test_debug(input_s: str, expected: int) -> None:
    assert compute(input_s) == expected


def test_input() -> None:
    result = compute(read_input())

    assert result == 814302


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

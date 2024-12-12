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
            area, perimeter = calculate_area_and_perimeter(matrix, seen, m, n)
            total += area * perimeter

    return total


DIRECTIONS = [
    sup.Direction.UP,
    sup.Direction.DOWN,
    sup.Direction.LEFT,
    sup.Direction.RIGHT,
]


def calculate_area_and_perimeter(
    matrix: sup.Matrix, seen: set[tuple[int, int]], m: int, n: int
) -> tuple[int, int]:
    coords = (m, n)
    if coords in seen:
        return 0, 0

    seen.add(coords)

    area = 1
    perimeter = 0
    value = matrix[m][n]
    for direction in DIRECTIONS:
        next_coords = matrix.next_coords(m, n, direction)
        if next_coords is None:
            perimeter += 1
            continue
        next_m, next_n = next_coords
        next_value = matrix[next_m][next_n]
        if next_value == value:
            next_area, next_perimeter = calculate_area_and_perimeter(
                matrix, seen, next_m, next_n
            )
            area += next_area
            perimeter += next_perimeter
        else:
            perimeter += 1

    return area, perimeter


INPUT_S1 = """\
AAAA
BBCD
BBCC
EEEC
"""
EXPECTED1 = 140
INPUT_S2 = """\
OOOOO
OXOXO
OOOOO
OXOXO
OOOOO
"""
EXPECTED2 = 772
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
EXPECTED3 = 1930


@pytest.mark.parametrize(
    "input_s,expected",
    [
        (INPUT_S1, EXPECTED1),
        (INPUT_S2, EXPECTED2),
        (INPUT_S3, EXPECTED3),
    ],
)
def test_debug(input_s: str, expected: int) -> None:
    assert compute(input_s) == expected


def test_input() -> None:
    result = compute(read_input())

    assert result == 1344578


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

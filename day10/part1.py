from __future__ import annotations

import sys
import timeit
from pathlib import Path

import pytest

import support as sup

INPUT_TXT = Path(__file__).parent / "input.txt"


def compute(s: str) -> int:
    matrix = sup.Matrix.create_from_input(s, cast_func=int)

    total = 0
    for m, row in enumerate(matrix):
        for n, value in enumerate(row):
            if value == 0:
                total += len(search_trails(matrix, m, n))

    return total


def search_trails(matrix: sup.Matrix, m: int, n: int) -> set[tuple[int, int]]:
    val = matrix[m][n]
    if val == 9:
        return {(m, n)}

    results = set()
    for next_m, next_n in matrix.neighbors_cross(m, n):
        if matrix[next_m][next_n] == val + 1:
            results.update(search_trails(matrix, next_m, next_n))
    return results


INPUT_S = """\
89010123
78121874
87430965
96549874
45678903
32019012
01329801
10456732
"""
EXPECTED = 36


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

    assert result == 737


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

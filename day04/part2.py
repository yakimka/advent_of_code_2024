from __future__ import annotations

import sys
import timeit
from pathlib import Path

import pytest

import support as sup

INPUT_TXT = Path(__file__).parent / "input.txt"


MAS = [["M", "A", "S"], ["S", "A", "M"]]


def compute(s: str) -> int:
    total = 0
    matrix, m_len, n_len = sup.make_matrix_from_input(s)
    for m, line in enumerate(matrix):
        if m > m_len - 3:
            break
        for n, char in enumerate(line):
            if n > n_len - 3:
                break

            first = [
                matrix[m][n],
                matrix[m + 1][n + 1],
                matrix[m + 2][n + 2],
            ]
            second = [
                matrix[m][n + 2],
                matrix[m + 1][n + 1],
                matrix[m + 2][n],
            ]
            if all(val in MAS for val in (first, second)):
                total += 1

    return total


INPUT_S = """\
MMMSXXMASM
MSAMXMSMSA
AMXSXMAAMM
MSAMASMSMX
XMASAMXAMM
XXAMMXXAMA
SMSMSASXSS
SAXAMASAAA
MAMMMXMMMM
MXMXAXMASX
"""
EXPECTED = 9


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

    assert result == 1809


def read_input() -> str:
    with open(INPUT_TXT) as f:
        return f.read()


if __name__ == "__main__":
    input_data = read_input()
    print("Answer is:     ", compute(input_data))

    if "-b" in sys.argv:
        number_of_runs = 1000
        bench_time = timeit.timeit(
            "compute(data)",
            setup="from __main__ import compute",
            globals={"data": input_data},
            number=number_of_runs,
        )
        print(f"{number_of_runs} runs took: {bench_time}s")
        one_run = sup.humanized_seconds(bench_time / number_of_runs)
        print(f"Average time:   {one_run}")

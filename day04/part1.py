from __future__ import annotations

import sys
import timeit
from pathlib import Path

import pytest

import support as sup

INPUT_TXT = Path(__file__).parent / "input.txt"


XMAS = "XMAS"


def compute(s: str) -> int:
    total = 0
    matrix, m_len, n_len = sup.make_matrix_from_input(s)
    for m, line in enumerate(matrix):
        for n, char in enumerate(line):
            if char != "X":
                continue
            paths = _find_xmas(matrix, [(m, n)])
            for path in paths:
                if _is_diag_or_cross(path):
                    total += 1

    return total


def _find_xmas(
    matrix: list[list[str]], path: list[tuple[int, int]]
) -> list[list[tuple[int, int]]]:
    start_m, start_n = path[-1]
    val = matrix[start_m][start_n]
    if val not in XMAS:
        return []
    if val == XMAS[-1]:
        return [path]

    next_val = XMAS[len(path)]

    m_len = len(matrix)
    n_len = len(matrix[0])
    result = []
    for neighbor in sup.neighbors_cross_diag(
        start_m, start_n, max_bounds=(m_len - 1, n_len - 1)
    ):
        next_m, next_n = neighbor
        if matrix[next_m][next_n] != next_val:
            continue
        res = _find_xmas(matrix, path + [neighbor])
        result.extend(res)
    return result


def _is_diag_or_cross(path: list[tuple[int, int]]) -> bool:
    first = path[0]
    if all(m == first[0] for m, n in path):
        return True
    if all(n == first[1] for m, n in path):
        return True
    return all(abs(m - first[0]) == abs(n - first[1]) for m, n in path)


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
EXPECTED = 18


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

    assert result == 2390


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

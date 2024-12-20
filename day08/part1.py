from __future__ import annotations

import sys
import timeit
from pathlib import Path

import pytest

import support as sup

INPUT_TXT = Path(__file__).parent / "input.txt"


def compute(s: str) -> int:
    matrix = sup.Matrix.create_from_input(s)

    antennas_by_freq = {}
    rows = matrix.m_len
    cols = matrix.n_len

    for r in range(rows):
        for c in range(cols):
            ch = matrix[r][c]
            if ch != ".":
                antennas_by_freq.setdefault(ch, []).append((r, c))

    antinodes = set()

    for freq, positions in antennas_by_freq.items():
        n = len(positions)
        if n < 2:
            # Need at least two antennas for antinodes
            continue

        for i in range(n):
            for j in range(i + 1, n):
                r1, c1 = positions[i]
                r2, c2 = positions[j]

                ar = 2 * r1 - r2
                ac = 2 * c1 - c2
                if 0 <= ar < rows and 0 <= ac < cols:
                    antinodes.add((ar, ac))

                br = 2 * r2 - r1
                bc = 2 * c2 - c1
                if 0 <= br < rows and 0 <= bc < cols:
                    antinodes.add((br, bc))

    return len(antinodes)


INPUT_S = """\
............
........0...
.....0......
.......0....
....0.......
......A.....
............
............
........A...
.........A..
............
............
"""
EXPECTED = 14


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

    assert result == 390


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

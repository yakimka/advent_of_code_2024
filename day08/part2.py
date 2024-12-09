from __future__ import annotations

import sys
import timeit
from math import gcd
from pathlib import Path

import pytest

import support as sup

INPUT_TXT = Path(__file__).parent / "input.txt"


def compute(s: str) -> int:
    matrix = sup.Matrix.create_from_input(s)

    rows = matrix.m_len
    cols = matrix.n_len

    antennas_by_freq = {}
    for r in range(rows):
        for c in range(cols):
            ch = matrix[r][c]
            if ch != ".":
                antennas_by_freq.setdefault(ch, []).append((r, c))

    antinodes = set()

    for freq, positions in antennas_by_freq.items():
        if len(positions) < 2:
            continue

        lines = {}

        n = len(positions)
        for i in range(n):
            r1, c1 = positions[i]
            for j in range(i + 1, n):
                r2, c2 = positions[j]

                A = c2 - c1
                B = r1 - r2
                C = r2 * c1 - r1 * c2

                g = gcd(A, gcd(B, C))
                if g != 0:
                    A //= g
                    B //= g
                    C //= g
                if A < 0 or (A == 0 and B < 0) or (A == 0 and B == 0 and C < 0):
                    A, B, C = -A, -B, -C

                lines.setdefault((A, B, C), []).append((r1, c1))
                lines[(A, B, C)].append((r2, c2))

        for (A, B, C), pts in lines.items():
            for r in range(rows):
                val = -B * r - C
                if val % A == 0:
                    c = val // A
                    if 0 <= c < cols:
                        antinodes.add((r, c))

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
EXPECTED = 34


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

    assert result == 1246


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

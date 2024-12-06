from __future__ import annotations

import sys
import timeit
from itertools import cycle
from pathlib import Path

import pytest

import support as sup

INPUT_TXT = Path(__file__).parent / "input.txt"


def compute(s: str) -> int:
    data = []
    guard_pos = None
    directions = cycle(
        [sup.Direction.UP, sup.Direction.RIGHT, sup.Direction.DOWN, sup.Direction.LEFT]
    )
    for m, line in enumerate(s.splitlines()):
        row = []
        for n, char in enumerate(line):
            if char == "^":
                guard_pos = (m, n)
            row.append(char)
        data.append(row)

    matrix = sup.Matrix(data)
    next_coords = guard_pos
    current_direction = next(directions)
    visited = {next_coords}
    while True:
        try_next = matrix.next_coords(*next_coords, direction=current_direction)
        if try_next is None:
            break

        next_m, next_n = try_next
        next_val = matrix[next_m][next_n]
        if next_val == "#":
            current_direction = next(directions)
            continue
        next_coords = (next_m, next_n)
        visited.add(next_coords)

    return len(visited)


INPUT_S = """\
....#.....
.........#
..........
..#.......
.......#..
..........
.#..^.....
........#.
#.........
......#...
"""
EXPECTED = 41


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

    assert result == 5239


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

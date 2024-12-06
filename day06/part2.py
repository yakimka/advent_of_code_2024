from __future__ import annotations

import sys
import timeit
from itertools import cycle
from pathlib import Path

import pytest

import support as sup

INPUT_TXT = Path(__file__).parent / "input.txt"


def compute(s: str) -> int:
    obstacles = []
    guard_pos = None
    directions = cycle(
        [sup.Direction.UP, sup.Direction.RIGHT, sup.Direction.DOWN, sup.Direction.LEFT]
    )
    bound_m = 0
    bound_n = 0
    for m, line in enumerate(s.splitlines()):
        for n, char in enumerate(line):
            if char == "^":
                guard_pos = (m, n)
            elif char == "#":
                obstacles.append((m, n))
        bound_n = len(line) - 1
        bound_m = m

    next_coords = guard_pos
    current_direction = next(directions)
    visited = {next_coords}
    while True:
        try_next = get_next_coords(
            *next_coords, direction=current_direction, m_bound=bound_m, n_bound=bound_n
        )
        if try_next is None:
            break

        if try_next in obstacles:
            current_direction = next(directions)
            continue
        next_coords = try_next
        visited.add(next_coords)

    return len(visited)


def get_next_coords(
    m: int, n: int, direction: sup.Vector2D, m_bound, n_bound
) -> tuple[int, int] | None:
    next_m, next_n = m + direction.x, n + direction.y
    if 0 > next_m or 0 > next_n or next_m > m_bound or next_n > n_bound:
        return None

    return next_m, next_n


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
EXPECTED = 6
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

from __future__ import annotations

import sys
import timeit
from itertools import cycle
from pathlib import Path
from typing import Iterator, NamedTuple

import pytest

import support as sup

INPUT_TXT = Path(__file__).parent / "input.txt"


class PuzzleData(NamedTuple):
    obstacles: set[tuple[int, int]]
    guard_pos: tuple[int, int]
    directions: Iterator[sup.Vector2D]
    m_bound: int
    n_bound: int


def compute(s: str) -> int:
    obstacles = set()
    guard_pos = None
    bound_m = 0
    bound_n = 0
    for m, line in enumerate(s.splitlines()):
        for n, char in enumerate(line):
            if char == "^":
                guard_pos = (m, n)
            elif char == "#":
                obstacles.add((m, n))
        bound_n = len(line) - 1
        bound_m = m

    directions = cycle(
        [sup.Direction.UP, sup.Direction.RIGHT, sup.Direction.DOWN, sup.Direction.LEFT]
    )
    visited = set()
    first_run_loop = find_loop(
        PuzzleData(obstacles, guard_pos, directions, bound_m, bound_n), visited
    )
    assert first_run_loop is False, "First run should not have a loop"

    variants = build_variants(
        original_path=visited,
        guard_pos=guard_pos,
        obstacles=obstacles,
        m_bound=bound_m,
        n_bound=bound_n,
    )
    total = 0
    for variant in variants:
        if find_loop(variant, None):
            total += 1

    return total


def build_variants(
    original_path: set[tuple[int, int, sup.Vector2D]],
    guard_pos: tuple[int, int],
    obstacles: set[tuple[int, int]],
    m_bound: int,
    n_bound: int,
) -> list[PuzzleData]:
    results = []
    added = set(guard_pos) | obstacles
    for pos_m, pos_n, pos_dir in original_path:
        new_obstacle = get_next_coords(
            pos_m, pos_n, direction=pos_dir, m_bound=m_bound, n_bound=n_bound
        )
        if new_obstacle is None or new_obstacle in added:
            continue

        results.append(
            PuzzleData(
                obstacles=obstacles | {new_obstacle},
                guard_pos=guard_pos,
                directions=cycle(
                    [
                        sup.Direction.UP,
                        sup.Direction.RIGHT,
                        sup.Direction.DOWN,
                        sup.Direction.LEFT,
                    ]
                ),
                m_bound=m_bound,
                n_bound=n_bound,
            )
        )
        added.add(new_obstacle)
    return results


def find_loop(
    data: PuzzleData, visited_container: set[tuple[int, int, sup.Vector2D]] | None
) -> bool:
    next_coords = data.guard_pos
    current_direction = next(data.directions)
    visited = {(*next_coords, current_direction)}

    while True:
        try_next = get_next_coords(
            *next_coords,
            direction=current_direction,
            m_bound=data.m_bound,
            n_bound=data.n_bound,
        )
        if try_next is None:
            break

        if try_next in data.obstacles:
            current_direction = next(data.directions)
            visited.add((*next_coords, current_direction))
            continue
        next_coords = try_next
        if (*next_coords, current_direction) in visited:
            return True
        visited.add((*next_coords, current_direction))

    if visited_container is not None:
        visited_container.update(visited)

    return False


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

    assert result == 1753


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

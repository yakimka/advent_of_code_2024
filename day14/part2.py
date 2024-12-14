#!/usr/bin/env python3
from __future__ import annotations

import sys
import timeit
from itertools import count
from pathlib import Path

import support as sup

INPUT_TXT = Path(__file__).parent / "input.txt"


def compute(s: str, width: int = 101, height: int = 103) -> int:
    robots = []
    for line in s.splitlines():
        first, second = line.split(" ")
        start_x, start_y = map(int, first[2:].split(","))
        velocity_x, velocity_y = map(int, second[2:].split(","))
        robots.append([start_x, start_y, velocity_x, velocity_y])

    for i in count(1):
        quadrants_counters = [0, 0, 0, 0]
        for robot in robots:
            start_x, start_y, velocity_x, velocity_y = robot
            end_x, end_y = simulate(
                start_x, start_y, velocity_x, velocity_y, 1, width, height
            )
            robot[0] = end_x
            robot[1] = end_y

            quadrant = calc_quadrant(end_x, end_y, width, height)
            if quadrant is not None:
                quadrants_counters[quadrant - 1] += 1

        # I have no f***ing idea how Christmas tree are supposed to look like
        # so I'm just going to check if all robots are in unique positions
        # and hope for the best.
        # P.S. I'm not a fan of this solution and this definitely is not a general
        # solution for this problem and will not work for all inputs.
        if unique_positions_heuristic(robots):
            # grid = [["." for _ in range(width)] for _ in range(height)]
            # for robot in robots:
            #     grid[robot[1]][robot[0]] = "#"
            # with open("output.txt", "w") as f:
            #     sup.print_matrix(grid, file=f)
            return i


def unique_positions_heuristic(robots: list[list[int]]) -> bool:
    return len({(robot[0], robot[1]) for robot in robots}) == len(robots)


def simulate(
    start_x: int,
    start_y: int,
    velocity_x: int,
    velocity_y: int,
    time: int,
    width: int,
    height: int,
) -> tuple[int, int]:
    for _ in range(time):
        start_x += velocity_x
        if start_x < 0:
            start_x = width + start_x
        elif start_x >= width:
            start_x = start_x - width

        start_y += velocity_y
        if start_y < 0:
            start_y = height + start_y
        elif start_y >= height:
            start_y = start_y - height

    return start_x, start_y


def calc_quadrant(x: int, y: int, width: int, height: int) -> int | None:
    middle_x = width // 2
    middle_y = height // 2
    if x == middle_x or y == middle_y:
        return None

    if x < middle_x:
        if y < middle_y:
            return 1
        else:
            return 3
    else:
        if y < middle_y:
            return 2
        else:
            return 4


def test_input() -> None:
    result = compute(read_input())

    assert result == 7753


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

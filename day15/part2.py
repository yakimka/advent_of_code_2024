#!/usr/bin/env python3
from __future__ import annotations

import sys
import timeit
from pathlib import Path

import pytest

import support as sup

INPUT_TXT = Path(__file__).parent / "input.txt"


instruction_to_direction = {
    "<": sup.Direction.LEFT,
    ">": sup.Direction.RIGHT,
    "^": sup.Direction.UP,
    "v": sup.Direction.DOWN,
}


def compute(s: str) -> int:
    matrix_data = []
    robot_pos = None
    field, instructions = s.split("\n\n")
    for m, line in enumerate(field.splitlines()):
        row = []
        for n, char in enumerate(line):
            if char == ".":
                row.extend("..")
            elif char == "#":
                row.extend("##")
            elif char == "O":
                row.extend("[]")
            if char == "@":
                row.extend("@.")
                robot_pos = [m, n * 2]
        matrix_data.append(row)
    matrix = sup.Matrix(matrix_data)

    for instruction in instructions:
        if instruction == "\n":
            continue
        direction = instruction_to_direction[instruction]
        simulate(matrix, robot_pos, direction)

    return sum(get_gps_coordinates(matrix))


def get_gps_coordinates(matrix: sup.Matrix) -> list[tuple[int, int]]:
    for m, row in enumerate(matrix):
        for n, char in enumerate(row):
            if char == "[":
                yield 100 * m + n


def simulate(matrix: sup.Matrix, robot_pos: list[int], direction: sup.Direction) -> int:
    robot_m, robot_n = robot_pos
    next_m, next_n = robot_m + direction.x, robot_n + direction.y
    next_char = matrix[next_m][next_n]
    if next_char == ".":
        move_robot(matrix, robot_pos, (next_m, next_n))
    elif next_char == "#":
        pass
    elif next_char == "O":
        box = detect_box(matrix, (next_m, next_n), direction)
        if is_box_movable(matrix, box, direction):
            move_box(matrix, box, direction)
            move_robot(matrix, robot_pos, (next_m, next_n))


def move_robot(
    matrix: sup.Matrix, robot_pos: list[int], next_pos: tuple[int, int]
) -> None:
    robot_m, robot_n = robot_pos
    next_m, next_n = next_pos
    matrix[next_m][next_n] = "@"
    matrix[robot_m][robot_n] = "."
    robot_pos[:] = [next_m, next_n]


def detect_box(
    matrix: sup.Matrix, start_pos: tuple[int, int], direction: sup.Direction
) -> list[tuple[int, int]]:
    result = [start_pos]
    m, n = start_pos
    while True:
        m, n = m + direction.x, n + direction.y
        if matrix[m][n] == "O":
            result.append((m, n))
        else:
            break
    return result


def is_box_movable(
    matrix: sup.Matrix, box: list[tuple[int, int]], direction: sup.Direction
) -> bool:
    m, n = box[-1]
    next_m, next_n = m + direction.x, n + direction.y
    return matrix[next_m][next_n] == "."


def move_box(
    matrix: sup.Matrix, box: list[tuple[int, int]], direction: sup.Direction
) -> None:
    for m, n in reversed(box):
        matrix[m][n] = "."
        matrix[m + direction.x][n + direction.y] = "O"


INPUT_S1 = """\
##########
#..O..O.O#
#......O.#
#.OO..O.O#
#..O@..O.#
#O#..O...#
#O..O..O.#
#.OO.O.OO#
#....O...#
##########

<vv>^<v^>v>^vv^v>v<>v^v<v<^vv<<<^><<><>>v<vvv<>^v^>^<<<><<v<<<v^vv^v>^
vvv<<^>^v^^><<>>><>^<<><^vv^^<>vvv<>><^^v>^>vv<>v<<<<v<^v>^<^^>>>^<v<v
><>vv>v^v^<>><>>>><^^>vv>v<^^^>>v^v^<^^>v^^>v^<^v>v<>>v^v^<v>v^^<^^vv<
<<v<^>>^^^^>>>v^<>vvv^><v<<<>^^^vv^<vvv>^>v<^^^^v<>^>vvvv><>>v^<<^^^^^
^><^><>>><>^^<<^^v>>><^<v>^<vv>>v>>>^v><>^v><<<<v>>v<v<v>vvv>^<><<>^><
^>><>^v<><^vvv<^^<><v<<<<<><^v<<<><<<^^<v<^^^><^>>^<v^><<<^>>^v<v^v<v^
>^>>^v>vv>^<<^v<>><<><<v<<v><>v<^vv<<<>^^v^>^^>>><<^v>>v^v><^^>>^<>vv^
<><^^>^^^<><vvvvv^v<v<<>^v<v>v<<^><<><<><<<^^<<<^<<>><<><^^^>^^<>^>v<>
^^>vv<^v^v<vv>^<><v<^v>^^^>>>^^vvv^>vvv<>>>^<^>>>>>^<<^v>^vvv<>^<><<v>
v^^>>><<^^<>>^v^<v^vv<>v^<<>^<^v^v><^<<<><<^<v><v<>vv>>v><v^<vv<>v^<<^
"""
EXPECTED1 = 9021
INPUT_S2 = """\
########
#..O.O.#
##@.O..#
#...O..#
#.#.O..#
#...O..#
#......#
########

<^^>>>vv<v>>v<<
"""
EXPECTED2 = 2028


@pytest.mark.parametrize(
    "input_s,expected",
    [
        (INPUT_S1, EXPECTED1),
        (INPUT_S2, EXPECTED2),
    ],
)
def test_debug(input_s: str, expected: int) -> None:
    assert compute(input_s) == expected


def test_input() -> None:
    result = compute(read_input())

    assert result > 0


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

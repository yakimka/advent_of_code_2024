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
    elif next_char in "[]":
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
    m, n = start_pos
    if direction in (sup.Direction.LEFT, sup.Direction.RIGHT):
        result = [start_pos]
        while True:
            m, n = m + direction.x, n + direction.y
            if matrix[m][n] in "[]":
                result.append((m, n))
            else:
                return result
    else:
        full_box = _find_full_box(matrix, start_pos)
        full_boxes = _detect_box_vertical(matrix, full_box, direction)
        box = []
        for full_box in full_boxes:
            for pos in full_box:
                if pos not in box:
                    box.append(pos)
        return box


def _detect_box_vertical(
    matrix: sup.Matrix,
    full_box: tuple[tuple[int, int], tuple[int, int]],
    direction: sup.Direction,
) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    result = [full_box]
    m1, n1 = full_box[0]
    m2, n2 = full_box[1]

    m1, n1 = m1 + direction.x, n1 + direction.y
    m2, n2 = m2 + direction.x, n2 + direction.y
    value1 = matrix[m1][n1]
    value2 = matrix[m2][n2]
    box1 = None
    box2 = None
    if value1 in "[]":
        box1 = _find_full_box(matrix, (m1, n1))
    if value2 in "[]":
        box2 = _find_full_box(matrix, (m2, n2))
    if box1 is None and box2 is None:
        return result
    if box1 == box2:
        result.extend(_detect_box_vertical(matrix, box1, direction))
        return result

    if box1 is not None:
        result.extend(_detect_box_vertical(matrix, box1, direction))
    if box2 is not None:
        result.extend(_detect_box_vertical(matrix, box2, direction))
    return result


def _find_full_box(
    matrix: sup.Matrix, start_pos: tuple[int, int]
) -> tuple[tuple[int, int], tuple[int, int]]:
    m1, n1 = start_pos
    value = matrix[m1][n1]
    if value == "[":
        return start_pos, (m1, n1 + 1)
    elif value == "]":
        return (m1, n1 - 1), start_pos
    else:
        raise ValueError("Invalid box start position")


def is_box_movable(
    matrix: sup.Matrix, box: list[tuple[int, int]], direction: sup.Direction
) -> bool:
    for m, n in box:
        next_m, next_n = m + direction.x, n + direction.y
        if matrix[next_m][next_n] not in "[].":
            return False
    return True


def move_box(
    matrix: sup.Matrix, box: list[tuple[int, int]], direction: sup.Direction
) -> None:
    old_values = {}
    for m, n in box:
        old_values[(m, n)] = matrix[m][n]
        matrix[m][n] = "."

    for m, n in box:
        matrix[m + direction.x][n + direction.y] = old_values[(m, n)]


def _calc_checksum(matrix: sup.Matrix):
    dots = 0
    box_left = 0
    box_right = 0
    obstacles = 0
    for m, row in enumerate(matrix):
        for n, char in enumerate(row):
            if char == ".":
                dots += 1
            elif char == "[":
                box_left += 1
            elif char == "]":
                box_right += 1
            elif char == "#":
                obstacles += 1
    return dots, box_left, box_right, obstacles


def _check_boxes(matrix: sup.Matrix) -> list[tuple[int, int]]:
    wrong_coordinates = []
    for m, row in enumerate(matrix):
        for n, char in enumerate(row):
            if char == "[" and matrix[m][n + 1] != "]":
                wrong_coordinates.append((m, n))
            elif char == "]" and matrix[m][n - 1] != "[":
                wrong_coordinates.append((m, n))
    return wrong_coordinates


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
#######
#...#.#
#.....#
#..OO@#
#..O..#
#.....#
#######

<vv<<^^<<^^
"""
EXPECTED2 = 618


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

    assert result == 1432898


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

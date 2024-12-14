#!/usr/bin/env python3
from __future__ import annotations

import sys
import timeit
from pathlib import Path

import pytest

import support as sup

INPUT_TXT = Path(__file__).parent / "input.txt"


def compute(s: str) -> int:
    button_a = None
    button_b = None
    prize = None
    for line in s.splitlines():
        if line.startswith("Button A:"):
            button_a = _parse_button(line)
        elif line.startswith("Button B:"):
            button_b = _parse_button(line)
        elif line.startswith("Prize:"):
            prize = _parse_prize(line)
        elif not line.strip():
            a = 1
        else:
            raise ValueError(f"Unknown line: {line}")

    return 0


def build_graph(button_a: tuple[int, int], button_b: tuple[int, int], prize: tuple[int, int]) -> dict[tuple[int, int], dict[tuple[int, int], int]]:
    pass


def _parse_button(line: str) -> tuple[int, int]:
    _, coords = line.split(": ")
    coords = coords.replace("X", "").replace("Y", "")
    return tuple(map(int, coords.split(", ")))


def _parse_prize(line: str) -> tuple[int, int]:
    _, coords = line.split(": ")
    coords = coords.replace("X=", "").replace("Y=", "")
    return tuple(map(int, coords.split(", ")))


INPUT_S = """\
Button A: X+94, Y+34
Button B: X+22, Y+67
Prize: X=8400, Y=5400

Button A: X+26, Y+66
Button B: X+67, Y+21
Prize: X=12748, Y=12176

Button A: X+17, Y+86
Button B: X+84, Y+37
Prize: X=7870, Y=6450

Button A: X+69, Y+23
Button B: X+27, Y+71
Prize: X=18641, Y=10279
"""
EXPECTED = 480


@pytest.mark.parametrize(
    "input_s,expected",
    [
        (INPUT_S, EXPECTED),
    ],
)
def test_debug(input_s: str, expected: int) -> None:
    assert compute(input_s) == expected


@pytest.mark.skip("Set answer for refactoring")
def test_input() -> None:
    result = compute(read_input())

    assert result == 0


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

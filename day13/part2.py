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
    total = 0
    for line in s.splitlines() + [""]:
        if line.startswith("Button A:"):
            button_a = _parse_button(line)
        elif line.startswith("Button B:"):
            button_b = _parse_button(line)
        elif line.startswith("Prize:"):
            prize = _parse_prize(line)
        elif not line.strip():
            res = solve_equation(button_a, button_b, prize)
            if res is None:
                continue
            a, b = res
            total += a * 3 + b
        else:
            raise ValueError(f"Unknown line: {line}")

    return int(total)


def solve_equation(button_a, button_b, prize) -> tuple[int, int] | None:
    ax, ay = button_a
    bx, by = button_b
    px, py = prize

    a = (px * -by + py * bx) / (ay * bx + ax * -by)
    if not a.is_integer():
        return None
    b = (px - ax * a) / bx
    return a, b


def _parse_button(line: str) -> tuple[int, int]:
    _, coords = line.split(": ")
    coords = coords.replace("X", "").replace("Y", "")
    return tuple(map(int, coords.split(", ")))


def _parse_prize(line: str) -> tuple[int, int]:
    _, coords = line.split(": ")
    coords = coords.replace("X=", "").replace("Y=", "")
    return tuple(map(lambda x: int(x) + 10000000000000, coords.split(", ")))


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
EXPECTED = 875318608908


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

    assert result == 108528956728655


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

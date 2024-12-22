#!/usr/bin/env python3
from __future__ import annotations

import sys
import timeit
from pathlib import Path

import pytest

import support as sup

INPUT_TXT = Path(__file__).parent / "input.txt"


def compute(s: str) -> int:
    total = 0
    for num in sup.iter_lines_as_numbers(s):
        total += resolve_secret(num, 2000)
    return total


def resolve_secret(secret: int, steps: int) -> int:
    for _ in range(steps):
        secret = mix_and_prune(secret, secret * 64)
        secret = mix_and_prune(secret, int(secret / 32))
        secret = mix_and_prune(secret, secret * 2048)
    return secret


def mix_and_prune(secret: int, value: int) -> int:
    return (secret ^ value) % 16777216


INPUT_S = """\
1
10
100
2024
"""
EXPECTED = 37327623


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

    assert result == 17612566393


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

#!/usr/bin/env python3
from __future__ import annotations

import sys
import timeit
from functools import lru_cache
from pathlib import Path

import pytest

import support as sup

INPUT_TXT = Path(__file__).parent / "input.txt"


def compute(s: str) -> int:
    stones = s.splitlines()[0].split()
    return sum(blink(stone, 75) for stone in stones)


@lru_cache(maxsize=None)
def blink(stone: str, depth: int) -> int:
    left, right = _blink_one(stone)
    if depth == 1:
        return 1 if right is None else 2

    count = blink(left, depth - 1)
    if right is not None:
        count += blink(right, depth - 1)
    return count


@lru_cache(maxsize=None)
def _blink_one(stone: str) -> tuple[str, str | None]:
    if stone == "0":
        return "1", None
    stone_len = len(stone)
    if stone_len % 2 == 0:
        middle = stone_len // 2
        first_half = stone[:middle]
        second_half = stone[middle:]
        if second_half.startswith("0"):
            second_half = second_half.lstrip("0") or "0"
        return first_half, second_half
    return str(int(stone) * 2024), None


INPUT_S = """\
125 17
"""
EXPECTED = 65601038650482


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

    assert result == 242090118578155


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

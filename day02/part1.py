from __future__ import annotations

import sys
import timeit
from pathlib import Path

import pytest

import support as sup

INPUT_TXT = Path(__file__).parent / "input.txt"


def compute(s: str) -> int:
    total = 0
    for line in s.splitlines():
        report = list(map(int, line.split()))
        if check_safe_report(report):
            total += 1

    return total


def check_safe_report(report: list[int]) -> bool:
    direction = None
    for i, num in enumerate(report[1:], start=1):
        delta = report[i - 1] - num
        if delta == 0 or abs(delta) > 3:
            return False
        if direction is None:
            direction = _get_direction(delta)
            continue
        if direction != _get_direction(delta):
            return False
    return True


def _get_direction(num: int) -> int:
    return -1 if num < 0 else 1


INPUT_S = """\
7 6 4 2 1
1 2 7 8 9
9 7 6 2 1
1 3 2 4 5
8 6 4 4 1
1 3 6 7 9
"""
EXPECTED = 2


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

    assert result == 299


def read_input() -> str:
    with open(INPUT_TXT) as f:
        return f.read()


if __name__ == "__main__":
    input_data = read_input()
    print("Answer is:     ", compute(input_data))

    if "-b" in sys.argv:
        number_of_runs = 1000
        bench_time = timeit.timeit(
            "compute(data)",
            setup="from __main__ import compute",
            globals={"data": input_data},
            number=number_of_runs,
        )
        print(f"{number_of_runs} runs took: {bench_time}s")
        one_run = sup.humanized_seconds(bench_time / number_of_runs)
        print(f"Average time:   {one_run}")

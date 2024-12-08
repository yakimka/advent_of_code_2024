from __future__ import annotations

import sys
import timeit
from pathlib import Path

import pytest

import support as sup

INPUT_TXT = Path(__file__).parent / "input.txt"


def compute(s: str) -> int:
    total = 0
    results = []
    for line in s.splitlines():
        split = line.split(": ")
        test_value = int(split[0])
        numbers = [int(item) for item in split[1].split()]

        if _check(test_value, numbers):
            total += test_value
            results.append(test_value)

    return total


def _check(test_value: int, numbers: list[int]) -> bool:
    if len(numbers) == 1:
        return numbers[0] == test_value

    first, second, *other = numbers
    return _check(test_value, [first * second, *other]) or _check(
        test_value, [first + second, *other]
    )


INPUT_S = """\
190: 10 19
3267: 81 40 27
83: 17 5
156: 15 6
7290: 6 8 6 15
161011: 16 10 13
192: 17 8 14
21037: 9 7 18 13
292: 11 6 16 20
"""
EXPECTED = 3749


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

    assert result == 7710205485870


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

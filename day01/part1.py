from __future__ import annotations

import heapq
import sys
import timeit
from collections.abc import Generator
from pathlib import Path

import pytest

import support as sup

INPUT_TXT = Path(__file__).parent / "input.txt"


def compute(s: str) -> int:
    left = []
    right = []
    for line in s.splitlines():
        if not line.strip():
            continue
        a, b = map(int, line.split("   "))
        heapq.heappush(left, a)
        heapq.heappush(right, b)

    total = 0
    for a, b in zip(heappopiter(left), heappopiter(right)):
        total += abs(a - b)
    return total


def heappopiter(heap: list[int]) -> Generator[int, None, None]:
    for _ in range(len(heap)):
        yield heapq.heappop(heap)


INPUT_S = """\
3   4
4   3
2   5
1   3
3   9
3   3
"""
EXPECTED = 11


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

    assert result == 3574690


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

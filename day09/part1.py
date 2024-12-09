from __future__ import annotations

import sys
import timeit
from pathlib import Path
from typing import Iterable

import pytest

import support as sup

INPUT_TXT = Path(__file__).parent / "input.txt"


def compute(s: str) -> int:
    blocks = list(to_blocks(s.splitlines()[0]))
    compacted = compact(blocks)

    return calc_hash(compacted)


def to_blocks(in_: Iterable[str]):
    file_id = 0
    for i, item in enumerate(in_):
        if i % 2 == 0:
            yield from [str(file_id)] * int(item)
            file_id += 1
        else:
            yield from "." * int(item)


def compact(blocks: str | list[str]):
    left = 0
    right = len(blocks) - 1
    while True:
        if blocks[left] == ".":
            while blocks[right] == ".":
                right -= 1
            yield blocks[right]
            right -= 1
        else:
            yield blocks[left]
        left += 1
        if left > right:
            break


def calc_hash(in_: Iterable[str]):
    total = 0
    for i, item in enumerate(in_):
        total += i * int(item)
    return total


INPUT_S = """\
2333133121414131402
"""
EXPECTED = 1928


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

    assert result == 6200294120911


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

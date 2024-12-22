#!/usr/bin/env python3
from __future__ import annotations

import sys
import timeit
from functools import lru_cache
from pathlib import Path

import pytest

import support as sup

INPUT_TXT = Path(__file__).parent / "input.txt"

# +---+---+---+
# | 7 | 8 | 9 |
# +---+---+---+
# | 4 | 5 | 6 |
# +---+---+---+
# | 1 | 2 | 3 |
# +---+---+---+
#     | 0 | A |
#     +---+---+
NUMPAD_PATHS = {
    "7": {
        "7": "",
        "8": ">",
        "9": ">>",
        "4": "v",
        "5": "v>",
        "6": "v>>",
        "1": "vv",
        "2": "vv>",
        "3": "vv>>",
        "0": ">vvv",
        "A": ">>vvv",
    },
    "8": {
        "7": "<",
        "8": "",
        "9": ">",
        "4": "<v",
        "5": "v",
        "6": "v>",
        "1": "<vv",
        "2": "vv",
        "3": "vv>",
        "0": "vvv",
        "A": "vvv>",
    },
    "9": {
        "7": "<<",
        "8": "<",
        "9": "",
        "4": "<<v",
        "5": "<v",
        "6": "v",
        "1": "<<vv",
        "2": "<vv",
        "3": "vv",
        "0": "<vvv",
        "A": "vvv",
    },
    "4": {
        "7": "^",
        "8": "^>",
        "9": "^>>",
        "4": "",
        "5": ">",
        "6": ">>",
        "1": "v",
        "2": "v>",
        "3": "v>>",
        "0": ">vv",
        "A": ">>vv",
    },
    "5": {
        "7": "<^",
        "8": "^",
        "9": "^>",
        "4": "<",
        "5": "",
        "6": ">",
        "1": "<v",
        "2": "v",
        "3": "v>",
        "0": "vv",
        "A": "vv>",
    },
    "6": {
        "7": "<<^",
        "8": "<^",
        "9": "^",
        "4": "<<",
        "5": "<",
        "6": "",
        "1": "<<v",
        "2": "<v",
        "3": "v",
        "0": "<vv",
        "A": "vv",
    },
    "1": {
        "7": "^^",
        "8": "^^>",
        "9": "^^>>",
        "4": "^",
        "5": "^>",
        "6": "^>>",
        "1": "",
        "2": ">",
        "3": ">>",
        "0": ">v",
        "A": ">>v",
    },
    "2": {
        "7": "<^^",
        "8": "^^",
        "9": "^^>",
        "4": "<^",
        "5": "^",
        "6": "^>",
        "1": "<",
        "2": "",
        "3": ">",
        "0": "v",
        "A": "v>",
    },
    "3": {
        "7": "<<^^",
        "8": "<^^",
        "9": "^^",
        "4": "<<^",
        "5": "<^",
        "6": "^",
        "1": "<<",
        "2": "<",
        "3": "",
        "0": "<v",
        "A": "v",
    },
    "0": {
        "7": "^^^<",
        "8": "^^^",
        "9": "^^^>",
        "4": "^^<",
        "5": "^^",
        "6": "^^>",
        "1": "^<",
        "2": "^",
        "3": "^>",
        "0": "",
        "A": ">",
    },
    "A": {
        "7": "^^^<<",
        "8": "<^^^",
        "9": "^^^",
        "4": "^^<<",
        "5": "<^^",
        "6": "^^",
        "1": "^<<",
        "2": "<^",
        "3": "^",
        "0": "<",
        "A": "",
    },
}
#     +---+---+
#     | ^ | A |
# +---+---+---+
# | < | v | > |
# +---+---+---+
KEYPAD_PATHS = {
    "^": {
        "^": "",
        "v": "v",
        "<": "v<",
        ">": "v>",
        "A": ">",
    },
    "v": {
        "v": "",
        "^": "^",
        "<": "<",
        ">": ">",
        "A": "^>",
    },
    "<": {
        "<": "",
        "^": ">^",
        "v": ">",
        ">": ">>",
        "A": ">>^",
    },
    ">": {
        ">": "",
        "^": "<^",
        "v": "<",
        "<": "<<",
        "A": "^",
    },
    "A": {
        "A": "",
        "^": "<",
        "v": "<v",
        "<": "v<<",
        ">": "v",
    },
}


def compute(s: str) -> int:
    total = 0
    for code in s.splitlines():
        num = int(code[:-1])
        count = sum(
            translate_pad_sequence(curr, target, 0)
            for curr, target in zip(f"A{code[:-1]}", code)
        )
        total += count * num
    return total


@lru_cache
def translate_pad_sequence(current, target, keypad_num):
    pad = NUMPAD_PATHS if keypad_num == 0 else KEYPAD_PATHS
    sequence = f"{pad[current][target]}A"
    if keypad_num == 2:
        return len(sequence)

    return sum(
        translate_pad_sequence(curr, target, keypad_num + 1)
        for curr, target in zip(f"A{sequence[:-1]}", sequence)
    )


INPUT_S = """\
029A
980A
179A
456A
379A
"""
EXPECTED = 126384


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

    assert result == 184718


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

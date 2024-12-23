#!/usr/bin/env python3
from __future__ import annotations

import sys
import timeit
from pathlib import Path

import pytest

import support as sup

INPUT_TXT = Path(__file__).parent / "input.txt"


def compute(s: str) -> str:
    graph_finder = sup.GraphCycleFinder()
    for line in s.splitlines():
        copm1, comp2 = line.split("-")
        graph_finder.add_edge(copm1, comp2)

    max_cycle = max(graph_finder.find_cycles(), key=len)
    return ",".join(sorted(max_cycle))


INPUT_S = """\
ka-co
ta-co
de-co
ta-ka
de-ta
ka-de
"""
EXPECTED = "co,de,ka,ta"


@pytest.mark.parametrize(
    "input_s,expected",
    [
        (INPUT_S, EXPECTED),
    ],
)
def test_debug(input_s: str, expected: str) -> None:
    assert compute(input_s) == expected


def test_input() -> None:
    result = compute(read_input())

    assert result == "af,aq,ck,ee,fb,it,kg,of,ol,rt,sc,vk,zh"


def read_input() -> str:
    with open(INPUT_TXT) as f:
        return f.read()


if __name__ == "__main__":
    input_data = read_input()
    print("Answer is:     ", compute(input_data))

    if "-b" in sys.argv:
        number_of_runs = 10
        bench_time = timeit.timeit(
            "compute(data)",
            setup="from __main__ import compute",
            globals={"data": input_data},
            number=number_of_runs,
        )
        print(f"{number_of_runs} runs took: {bench_time}s")
        one_run = sup.humanized_seconds(bench_time / number_of_runs)
        print(f"Average time:   {one_run}")

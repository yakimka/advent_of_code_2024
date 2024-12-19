#!/usr/bin/env python3
from __future__ import annotations

import sys
import timeit
from pathlib import Path

import pytest

import support as sup

INPUT_TXT = Path(__file__).parent / "input.txt"


def compute(s: str) -> int:
    lines = s.splitlines()
    colors = lines[0].split(", ")
    colors_by_letter = {}
    for color in colors:
        colors_by_letter.setdefault(color[0], []).append(color)

    total = 0
    for pattern in lines[2:]:
        graph = construct_graph(pattern, colors_by_letter)
        if has_path(graph, 0, len(pattern)):
            total += 1

    return total


def construct_graph(pattern: str, colors_by_letter: dict[str, list[str]]):
    graph = {len(pattern): {}}
    for i, stripe in enumerate(pattern):
        graph[i] = {}
        for stripe_pattern in colors_by_letter.get(stripe, []):
            next_node = i + len(stripe_pattern)
            if stripe_pattern != pattern[i:next_node]:
                continue
            graph[i][next_node] = 1

    return graph


def has_path(graph: dict[int, dict[int, int]], start: int, end: int) -> bool:
    visited = set()
    stack = [start]
    while stack:
        node = stack.pop()
        if node == end:
            return True
        if node in visited:
            continue
        visited.add(node)
        stack.extend(graph.get(node, {}).keys())

    return False


INPUT_S = """\
r, wr, b, g, bwu, rb, gb, br

brwrr
bggr
gbbr
rrbgbr
ubwu
bwurrg
brgr
bbrgwb
"""
EXPECTED = 6


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

    assert result == 238


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

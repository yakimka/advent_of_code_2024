from __future__ import annotations

import sys
import timeit
from collections import defaultdict
from pathlib import Path

import pytest

import support as sup

INPUT_TXT = Path(__file__).parent / "input.txt"


def compute(s: str) -> int:
    sections = s.strip().split("\n\n")
    rules = [tuple(line.split("|")) for line in sections[0].splitlines()]
    updates = [line.split(",") for line in sections[1].splitlines()]

    total = 0
    for update in updates:
        if not is_valid_update(update, rules):
            sorted_pages = topological_sort(update, rules)
            total += int(find_middle_page(sorted_pages))

    return total


def topological_sort(pages, rules):
    graph = defaultdict(list)
    for x, y in rules:
        if x in pages and y in pages:
            graph[x].append(y)

    return sup.topological_sort(graph)


def is_valid_update(update, rules):
    relevant_rules = [rule for rule in rules if rule[0] in update and rule[1] in update]

    for x, y in relevant_rules:
        if update.index(x) > update.index(y):
            return False
    return True


def find_middle_page(update):
    mid_index = len(update) // 2
    return update[mid_index]


INPUT_S = """\
47|53
97|13
97|61
97|47
75|29
61|13
75|53
29|13
97|29
53|29
61|53
97|53
61|29
47|13
75|47
97|75
47|61
75|61
47|29
75|13
53|13

75,47,61,53,29
97,61,53,29,13
75,29,13
75,97,47,61,53
61,13,29
97,13,75,29,47
"""
EXPECTED = 123


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

    assert result == 5799


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

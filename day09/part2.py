from __future__ import annotations

import sys
import timeit
from pathlib import Path

import pytest

import support as sup

INPUT_TXT = Path(__file__).parent / "input.txt"


def compute(s: str) -> int:
    disk = []
    file_blocks = []
    free_blocks = []

    file_id = 0
    for i, item in enumerate(s.splitlines()[0]):
        block_size = int(item)
        if i % 2 == 0:
            file_blocks.append((len(disk), block_size))
            disk.extend([file_id] * block_size)
            file_id += 1
        else:
            free_blocks.append((len(disk), block_size))
            disk.extend(["."] * block_size)

    defrag_disk(disk, file_blocks, free_blocks)
    return sum(id * item for id, item in enumerate(disk) if item != ".")


def defrag_disk(disk, file_blocks, free_blocks):
    for file_id, file_size in reversed(file_blocks):
        for free_id, free_size in free_blocks:
            if free_id > file_id:
                break

            if free_size >= file_size:
                free_slice = slice(free_id, free_id + file_size)
                file_slice = slice(file_id, file_id + file_size)

                disk[free_slice] = disk[file_slice]
                disk[file_slice] = ["."] * file_size
                idx = free_blocks.index((free_id, free_size))
                if file_size == free_size:
                    free_blocks.pop(idx)
                else:
                    free_blocks[idx] = (free_id + file_size, free_size - file_size)
                break


INPUT_S = """\
2333133121414131402
"""
EXPECTED = 2858


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

    assert result == 6227018762750


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

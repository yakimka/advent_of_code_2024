#!/usr/bin/env python3
from __future__ import annotations

import sys
import timeit
from pathlib import Path

import pytest

import support as sup

INPUT_TXT = Path(__file__).parent / "input.txt"


def compute(s: str) -> int:
    _, program = s.split("\n\n")
    _, program = program.split(": ")
    program = [int(x) for x in program.split(",")]

    return solve(program, len(program) - 1, 0)


def solve(program: list[int], cursor: int, current: int) -> int | None:
    for value in range(8):
        output = run_program(current * 8 + value, 0, 0, program)
        if output == program[cursor:]:
            if cursor == 0:
                return current * 8 + value
            answer = solve(program, cursor - 1, current * 8 + value)
            if answer is not None:
                return answer
    return None


def run_program(a, b, c, program):
    def combo_value(operand):
        if operand <= 3:
            return operand
        elif operand == 4:
            return a
        elif operand == 5:
            return b
        elif operand == 6:
            return c

    ip = 0
    output = []

    while ip < len(program):
        opcode = program[ip]
        if ip + 1 >= len(program):
            break
        operand = program[ip + 1]

        if opcode == 0:  # adv
            # A = A // (2^(combo operand))
            val = combo_value(operand)
            denom = 2**val
            a = a // denom
            ip += 2
        elif opcode == 1:  # bxl
            b = b ^ operand
            ip += 2
        elif opcode == 2:  # bst
            val = combo_value(operand)
            b = val % 8
            ip += 2
        elif opcode == 3:  # jnz
            if a != 0:
                ip = operand
            else:
                ip += 2
        elif opcode == 4:  # bxc
            b = b ^ c
            ip += 2
        elif opcode == 5:  # out
            val = combo_value(operand) % 8
            output.append(val)
            ip += 2
        elif opcode == 6:  # bdv
            val = combo_value(operand)
            b = a // (2**val)
            ip += 2
        elif opcode == 7:  # cdv
            val = combo_value(operand)
            c = a // (2**val)
            ip += 2
        else:
            # Unknown opcode - halt
            break

    return output


INPUT_S = """\
Register A: 2024
Register B: 0
Register C: 0

Program: 0,3,5,4,3,0
"""
EXPECTED = 117440


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

    assert result == 236581108670061


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

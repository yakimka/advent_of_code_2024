#!/usr/bin/env python3
from __future__ import annotations

import sys
import timeit
from pathlib import Path

import pytest

import support as sup

INPUT_TXT = Path(__file__).parent / "input.txt"


def compute(s: str) -> str:
    registries, program = s.split("\n\n")
    registries = [int(x.split(": ")[1]) for x in registries.splitlines()]
    _, program = program.split(": ")
    register_a = registries[0]
    register_b = registries[1]
    register_c = registries[2]
    program = [int(x) for x in program.split(",")]

    result = run_program(register_a, register_b, register_c, program)
    return ",".join(str(x) for x in result)


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
Register A: 729
Register B: 0
Register C: 0

Program: 0,1,5,4,3,0
"""
EXPECTED = "4,6,3,5,6,3,5,2,1,0"


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

    assert result == "1,5,0,5,2,0,1,3,5"


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

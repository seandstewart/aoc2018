#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import dataclasses
import pathlib
from typing import Set, Tuple

from dec21 import INPUT
from dec19.answer import get_program


@dataclasses.dataclass
class Program:
    borval: int = 0
    setval: int = 0
    banval1: int = 0
    banval2: int = 0
    mulval: int = 0
    gtval: int = 0

    def load(self, path: pathlib.Path):
        """Load the low-level instructions and extract the important values/operations.

        This should work with all inputs, but I only have one to test with.
        """
        important_ops = {'bori', 'seti', 'bani', 'muli', 'gtir'}
        ip, instructions = get_program(path)
        instructions = [x for x in instructions if x.opcode in important_ops]
        for instruction in instructions:
            if instruction.opcode == 'seti' and instruction.a > self.setval:
                self.setval = instruction.a
            elif instruction.opcode == 'bani':
                if instruction.b < 400:
                    self.banval1 = instruction.b
                elif instruction.b > 500:
                    self.banval2 = instruction.b
            elif instruction.opcode == 'bori':
                self.borval = instruction.b
            elif instruction.opcode == 'muli' and instruction.b > 300:
                self.mulval = instruction.b
            elif instruction.opcode == 'gtir':
                self.gtval = instruction.a

    def run(self) -> Tuple[int, int, Set[int]]:
        """Run the program defined in the input, but short-circuit it.

        The Program is designed to to loop through the instructions until a certain set of criteria are met.
        We can identify the target values because they are unique values in the instruction set,
        then we can perform the operation which takes place one at a time in the loop all at once.

        The answer for part 1 is the first 'exit value' found, the answer to part 2 is the last.

        We know it's the last exit value if the exit values start to repeat."""
        first = last = op = 0
        seen = set()

        while True:
            comp = op | self.borval
            op = self.setval

            while True:
                # This is the calculation that takes place one-at-a-time in the instructions
                op = (((op + (comp & self.banval1)) & self.banval2) * self.mulval) & self.banval2
                # This indicates we've reached an exit value
                if self.gtval > comp:
                    # We've started looping back through exit values, break out.
                    if op in seen:
                        return first, last, seen
                    # Track the exit values we've seen
                    seen.add(op)
                    # Part 2
                    last = op
                    if len(seen) == 1:
                        # Part 1
                        first = op
                    break
                # Otherwise, we need to keep looping
                else:
                    comp = int(comp / self.gtval)


def get_answer1(path: pathlib.Path = INPUT) -> int:
    program = Program()
    program.load(path)
    first, last, seen = program.run()
    return first


def get_answer2(path: pathlib.Path = INPUT) -> int:
    program = Program()
    program.load(path)
    first, last, seen = program.run()
    return last

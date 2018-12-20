import collections
import dataclasses
import pathlib
import logging

from typing import Tuple, NewType, List

from dec16.answer import VirtualMemory, Instruction
from dec19 import INPUT

from util.helpers import load_values_list, Values

log = logging.getLogger(__name__)

IPAddress = NewType('IPAddress', int)
Program = NewType('Program', Tuple[IPAddress, List[Instruction]])


class Instruction(Instruction):
    opcode: str


def memory_factory(n: int = 6) -> VirtualMemory:
    return VirtualMemory([0 for _ in range(n)])


@dataclasses.dataclass
class IPController:
    program: Program
    memory: VirtualMemory = dataclasses.field(default_factory=memory_factory)

    @staticmethod
    def solve(n: int) -> int:
        """These are the rules that are applied to r0 step-by-step. We're just fast-forwarding."""
        answer = 0
        for i in range(1, n + 1):
            if i ** 2 == n:
                answer += 1
            elif n % i == 0:
                answer += i
        return answer

    def run(self) -> int:
        pointer, instructions = self.program
        instruction = instructions[self.memory[pointer]]
        in_scope = True
        canary = self.memory[5]
        counter = collections.Counter()
        start = self.memory[0]
        while in_scope:
            try:
                # Try to short-circuit the loop. r1 is a comparison value
                # if initial r0 == 0, the first time r1 + *previous* r5 == *current* r5, we're done
                # else, allow that value to repeat a couple since the above *always* happens once
                if canary and self.memory[1] + canary == self.memory[5]:
                    if (start and counter[canary] > 2) or start == 0:
                        break
                    counter[canary] += 1
                # Set the new canary value
                canary = self.memory[5]
                getattr(self.memory, instruction.opcode)(instruction.a, instruction.b, instruction.c)
                self.memory[pointer] += 1
                instruction = instructions[self.memory[pointer]]
            # Ideally we've short-circuited the loop before we get an index error.
            except IndexError:
                in_scope = False
                log.info("Your optimization didn't work, dummy.")

        return self.solve(self.memory[5])


def get_program(path: pathlib.Path = INPUT) -> Program:
    values: Values = load_values_list(path)
    ip = int(values.pop(0).split()[-1])
    instr = []
    for value in values:
        op, a, b, c = value.split()
        instr.append(Instruction(op, int(a), int(b), int(c)))

    program: Program = (ip, instr)
    return program


def get_answer1(path: pathlib.Path = INPUT):
    program = get_program(path)
    controller = IPController(program)
    return controller.run()


def get_answer2(path: pathlib.Path = INPUT):
    program = get_program(path)
    controller = IPController(program)
    controller.memory[0] = 1
    return controller.run()

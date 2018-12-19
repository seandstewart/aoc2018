import dataclasses
import pathlib

from typing import Tuple, NewType, List

from dec16.answer import VirtualMemory, Registers, Instruction
from dec19 import INPUT

from util.helpers import load_values_list, Values


InstructionPointers = NewType('InstructionPointer', Tuple[Registers, ...])
IPAddress = NewType('IPAddress', int)
Program = NewType('Program', Tuple[IPAddress, List[Instruction]])


class Instruction(Instruction):
    opcode: str


def pointer_factory(n: int = 6) -> InstructionPointers:
    ips: InstructionPointers = tuple(VirtualMemory([x] + [0 for _ in range(5)]) for x in range(n))
    return ips


@dataclasses.dataclass
class IPController:
    program: Program
    memory: VirtualMemory = VirtualMemory([0 for _ in range(6)])

    def run(self) -> VirtualMemory:
        start, instructions = self.program
        instruction = instructions[start]
        in_scope = True
        while in_scope:
            try:
                getattr(self.memory, instruction.opcode)(instruction.a, instruction.b, instruction.c)
                self.memory[0] += 1
                instruction = instructions[self.memory[0]]
            except IndexError:
                in_scope = False
        return self.memory


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
    mem = controller.run()
    return mem

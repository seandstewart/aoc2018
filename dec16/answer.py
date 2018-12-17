import dataclasses
import pathlib
import re

from typing import NamedTuple, Tuple, NewType, List

from dec16 import INPUT, INPUT2
from util.helpers import load_values_list, Values, chunks, flatten_iter

Registers = NewType('Registers', List[int])


PATTERN = re.compile(r'\d+')


@dataclasses.dataclass
class VirtualMemory:
    registers: Registers

    def __getitem__(self, item: int):
        return self.registers[item]

    def __setitem__(self, key: int, value: int):
        self.registers[key] = value

    def addr(self, a: int, b: int, c: int):
        self[c] = self[a] + self[b]

    def addi(self, a: int, b: int, c: int):
        self[c] = self[a] + b

    def mulr(self, a: int, b: int, c: int):
        self[c] = self[a] * self[b]

    def muli(self, a: int, b: int, c: int):
        self[c] = self[a] * b

    def banr(self, a: int, b: int, c: int):
        self[c] = self[a] & self[b]

    def bani(self, a: int, b: int, c: int):
        self[c] = self[a] & b

    def borr(self, a: int, b: int, c: int):
        self[c] = self[a] | self[b]

    def bori(self, a: int, b: int, c: int):
        self[c] = self[a] | b

    def setr(self, a: int, b: int, c: int):
        self[c] = self[a]

    def seti(self, a: int, b: int, c: int):
        self[c] = a

    def gtir(self, a: int, b: int, c: int):
        self[c] = int(a > self[b])

    def gtri(self, a: int, b: int, c: int):
        self[c] = int(self[a] > b)

    def gtrr(self, a: int, b: int, c: int):
        self[c] = int(self[a] > self[b])

    def eqir(self, a: int, b: int, c: int):
        self[c] = int(a == self[b])

    def eqri(self, a: int, b: int, c: int):
        self[c] = int(self[a] == b)

    def eqrr(self, a: int, b: int, c: int):
        self[c] = int(self[a] == self[b])

    operations = {
        addr, addi, mulr, muli, banr, bani, borr, bori, setr, seti, gtir, gtri, gtrr, eqir, eqri, eqrr
    }


class Instruction(NamedTuple):
    opcode: int
    a: int
    b: int
    c: int


State = NewType('State', Tuple[int, int, int, int])


@dataclasses.dataclass
class InstructionSet:
    before: State
    instruction: Instruction
    after: State

    def __post_init__(self):
        registers: Registers = list(self.before)
        self.memory = VirtualMemory(registers)
        self.candidates = set()
        for operation in VirtualMemory.operations:
            local = VirtualMemory(registers[:])
            getattr(local, operation.__name__)(*self.instruction[1:])
            if local.registers == list(self.after):
                self.candidates.add(operation.__name__)


@dataclasses.dataclass
class MachineController:
    examples: List[InstructionSet]
    memory: VirtualMemory

    def __post_init__(self):
        self.opcodes = self.resolve_opcodes()

    def resolve_opcodes(self):
        found = {}
        candidates = set(flatten_iter(x.candidates for x in self.examples if len(x.candidates) > 1))
        while candidates:
            for operation in self.examples:
                operation.candidates -= set(found.values())
                if len(operation.candidates) == 1:
                    found[operation.instruction.opcode] = operation.candidates.pop()
            candidates -= set(found.values())

        return found

    def run(self, instructions: List[Instruction]):
        for instruction in instructions:
            operation = self.opcodes[instruction.opcode]
            getattr(self.memory, operation)(instruction.a, instruction.b, instruction.c)


def load_examples(path: pathlib.Path = INPUT) -> List[InstructionSet]:
    values: Values = load_values_list(path)
    examples = []
    for before, instruction, after in chunks(values, 3):  # Instruction sets are groups of three lines
        before: State = tuple(int(x) for x in PATTERN.findall(before))
        after: State = tuple(int(x) for x in PATTERN.findall(after))
        instruction = Instruction(*(int(x) for x in PATTERN.findall(instruction)))
        examples.append(InstructionSet(before, instruction, after))

    return examples


def load_instructions(path: pathlib.Path = INPUT2) -> List[Instruction]:
    values: Values = load_values_list(path)
    instructions = []
    for value in values:
        instructions.append(
            Instruction(*(int(x) for x in PATTERN.findall(value)))
        )
    return instructions


def get_answer1(path: pathlib.Path = INPUT):
    examples = load_examples(path)

    return len([x for x in examples if len(x.candidates) > 2])


def get_answer2(input: pathlib.Path = INPUT, input2: pathlib.Path = INPUT2) -> MachineController:
    registers: Registers = [0 for _ in range(4)]
    mem = VirtualMemory(registers)
    examples = load_examples(input)
    instructions = load_instructions(input2)
    controller = MachineController(examples, mem)
    controller.run(instructions)
    return controller

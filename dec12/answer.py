import dataclasses
import pathlib
from typing import Set, Dict, Tuple

from dec12 import INPUT


@dataclasses.dataclass
class StateMachine:
    state: Set[int]
    rules: Dict[str, str]

    def step(self):
        result = set()
        for i in range(min(self.state) - 2, max(self.state) + 3):
            key = ''.join(
                '#' if j in self.state else '.' for j in range(i - 2, i + 3)
            )
            if self.rules[key] == '#':
                result.add(i)
        self.state = result

    def run(self, n: int = 1) -> Tuple[int, int, int]:
        power = total = i = 0
        for i in range(n):
            power = total
            self.step()
            total = sum(self.state)
        return power, total, i


def get_state_and_rules(path: pathlib.Path = INPUT) -> Tuple[Set[int], Dict[str, str]]:
    lines = [x for x in path.read_text().split('\n') if x]
    state = set(i for i, x in enumerate(lines[0].split()[-1]) if x == '#')
    rules = dict(line.split()[::2] for line in lines[1:])
    return state, rules


def get_answer1(path: pathlib.Path = INPUT) -> int:
    state, rules = get_state_and_rules(path)
    machine = StateMachine(state, rules)
    power, total, i = machine.run()
    return total


def get_answer2(path: pathlib.Path = INPUT) -> int:
    state, rules = get_state_and_rules(path)
    machine = StateMachine(state, rules)
    power, total, i = machine.run(1000)
    return power + (total - power) * (50000000000 - i)

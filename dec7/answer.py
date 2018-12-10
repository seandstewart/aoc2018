#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import functools
import logging
import re
from typing import List, NewType, Pattern,Union, Dict, Tuple, Set

from util import Values, Value
from util.helpers import flatten_iter

logger = logging.getLogger(__name__)


PATTERN: Pattern = re.compile(r'.+(?P<first>[A-Z]).+(?P<second>[A-Z]).*')


Score = NewType('Score', int)
ScoreMap = NewType('ScoreMap', Dict[Value, Score])
QueueEntry = NewType('QueueEntry', Tuple[Score, Value])


class Worker:
    def __init__(self, ident):
        self.id = ident
        self.step = None

    def __repr__(self):
        return f"{type(self)}(id={self.id}, step={self.step}, free={self.free})"

    @property
    def free(self) -> bool:
        return not self.step

    def work(self, step: 'Step' = None) -> Union['Step', None]:
        self.step = step or self.step
        if self.step:
            step = self.step
            step.duration -= 1

            if step.duration <= 0:
                self.step = None
                return step


@functools.total_ordering
class Step:
    def __init__(self, name: Value, min_duration: int = 60):
        self.name = name
        self.predicates = []
        self.duration = min_duration + (ord(self.name) - 64)

    def __repr__(self):
        return f"{type(self)}(name={self.name}, predicates={self.predicates}, duration={self.duration})"

    def __str__(self):
        return self.name

    def __lt__(self, other: Union[str, 'Step']):
        return str(self) < str(other)

    def __eq__(self, other: Union[str, 'Step']):
        return str(self) == str(other)


class Queue:
    def __init__(self, *steps: Values, workers: int = 0):
        self.step_map: Dict[Value, Step] = {}
        self.final: List[Step] = []
        self.active: Set[Value] = set()
        self.workers = [Worker(num) for num in range(workers)]
        self.total_seconds = 0
        self.parse(*steps)

    def __repr__(self):
        return f"{type(self)}(steps={list(self.step_map.values())})"

    def parse(self, *steps: Value):
        pairs = [PATTERN.match(x).groups() for x in steps]
        names = set(flatten_iter(pairs))
        for name in names:
            self.step_map[name] = Step(name)

        for first, second in pairs:
            self.step_map[second].predicates.append(first)

    def get_free_workers(self) -> List[Worker]:
        return [x for x in self.workers if x.free]

    def get_busy_workers(self) -> List[Worker]:
        return [x for x in self.workers if not x.free]

    def get_free_steps(self) -> List[Step]:
        return sorted(x for x in self.step_map.values() if not x.predicates)

    def get_ready_steps(self) -> List[Step]:
        ready = []
        for step in self.step_map.values():
            if all(x in self.final for x in step.predicates):
                ready.append(step)

        return ready

    def free_up_steps(self):
        for step in self.step_map.values():
            if step.predicates and step not in self.final:
                step.predicates = [x for x in step.predicates if x not in self.final]

    def get_next_available(self) -> List[Step]:
        self.free_up_steps()
        free = self.get_free_steps()
        ready = self.get_ready_steps()
        candidates = free + ready
        new = []
        seen = set()
        if candidates:
            for candidate in candidates:
                if candidate not in self.final and candidate.name not in seen:
                    new.append(candidate)
                    seen.add(candidate.name)

        return sorted(new)

    def run(self) -> List[Step]:
        steps = self.get_next_available()
        while steps:
            if len(self.workers) > 1:
                free = self.get_free_workers()
                busy = self.get_busy_workers()
                steps = [x for x in steps if x.name not in self.active]
                reports = [x.work() for x in busy]
                self.final.extend((x for x in reports if x))
                for step, worker in zip(steps, free):
                    if step.name not in self.active:
                        if worker.work(step):
                            self.final.append(step)
                        else:
                            self.active.add(step.name)
                self.active -= set(x.name for x in self.final)
            else:
                self.final.append(steps[0])
            self.total_seconds += 1
            steps = self.get_next_available()

        return self.final

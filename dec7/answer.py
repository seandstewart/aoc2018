#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import collections
import dataclasses
import functools
import logging
import pathlib
import re
from typing import List, NewType, Pattern, NamedTuple, Hashable, Union, Callable, Iterator, Dict, \
    Tuple, Set

from dec7 import INPUT
from util import Values, Value
from util.helpers import load_values_list, flatten_iter

logger = logging.getLogger(__name__)


PATTERN: Pattern = re.compile(r'.+(?P<first>[A-Z]).+(?P<second>[A-Z]).*')


Score = NewType('Score', int)
ScoreMap = NewType('ScoreMap', Dict[Value, Score])
QueueEntry = NewType('QueueEntry', Tuple[Score, Value])
Queue = NewType('Queue', List[QueueEntry])


class Worker:
    def __init__(self, ident):
        self.id = ident
        self.step = None

    @property
    def free(self) -> bool:
        return bool(self.step)

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
    def __init__(self, name: Value):
        self.name = name
        self.predicates = []
        self.duration = 60 + (ord(self.name) - 64)

    def __repr__(self):
        return self.name

    def __str__(self):
        return repr(self)

    def __lt__(self, other: Union[str, 'Step']):
        return str(self) < str(other)

    def __eq__(self, other: Union[str, 'Step']):
        return str(self) == str(other)


class Queue:
    def __init__(self, *steps: Values, workers: int = 0):
        self.step_map: Dict[Value, Step] = {}
        self.step_order = collections.deque()
        self.active = set()
        self.workers = [Worker(num) for num in range(workers)]
        self.total_seconds = 0
        self.parse(*steps)

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
            if all(x in self.step_order for x in step.predicates):
                ready.append(step)

        return ready

    def free_up_steps(self):
        for step in self.step_map.values():
            if step.predicates and step not in self.step_order:
                step.predicates = [x for x in step.predicates if x not in self.step_order]

    def get_rough_sorted_steps(self) -> List[Step]:
        self.free_up_steps()
        free = self.get_free_steps()
        ready = self.get_ready_steps()
        candidates = free + ready
        new = []
        seen = set()
        if candidates:
            for candidate in candidates:
                if candidate not in self.step_order and candidate.name not in seen:
                    new.append(candidate)
                    seen.add(candidate.name)

        return sorted(new)

    def get_step_order(self) -> collections.deque:
        steps = self.get_rough_sorted_steps()
        while steps:
            if len(self.workers) > 1:
                free = self.get_free_workers()
                busy = self.get_busy_workers()
                steps = [x for x in steps if x.name not in self.active]
                reports = [x.work() for x in busy]
                self.step_order.extend((x for x in reports if x))
                for step, worker in zip(steps, free):
                    if step.name not in self.active:
                        report = worker.work(step)
                        if report:
                            self.step_order.append(report)
                        else:
                            self.active.add(report.name)
                for step in self.step_order:
                    if step.name in self.active:
                        self.active.remove(step.name)
            else:
                self.step_order.append(steps[0])
            self.total_seconds += 1
            steps = self.get_rough_sorted_steps()

        return self.step_order


def get_queue(path: pathlib.Path = INPUT) -> Queue:
    values: Values = load_values_list(path, as_int=False)
    score_map: ScoreMap = collections.defaultdict(int)
    for value in values:
        match = PATTERN.match(value)
        first, second = match.group('first'), match.group('second')
        if first not in score_map:
            score_map[first] = 0
            dupes = sorted(x for x, y in score_map.items() if y == score_map[first])
            for ix, entry in enumerate(dupes):
                score_map[entry] = ix
        second_score = score_map[first] + 1
        score_map[second] = second_score if second_score > score_map[second] else score_map[second]
        dupes = sorted(x for x, y in score_map.items() if y == score_map[second])
        for ix, entry in enumerate(dupes):
            score_map[entry] += ix

    queue: Queue = sorted((y, x,) for x, y in score_map.items())
    return queue


def stringify_queue(queue: Queue) -> str:
    queue.sort()
    return "".join(y for x, y in queue)



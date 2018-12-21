#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import collections
import enum
import pathlib

from dec20 import INPUT
from util.containers import CardinalDirections, Point


class OrFlags(enum.Enum):
    START = '('
    OR = '|'
    FINISH = ')'


class FloorPlan:

    def __init__(self, scenario: str):
        self.rooms = {}
        self.branches = collections.deque()
        self.map(scenario)

    def map(self, scenario: str):
        position = Point(0, 0)
        doors = 0
        for flag in scenario.strip('^$'):
            if flag == OrFlags.START.value:
                self.branches.append((position, doors))
            elif flag == OrFlags.FINISH.value:
                position, doors = self.branches.pop()
            elif flag == OrFlags.OR.value:
                position, doors = self.branches[-1]
            else:
                position += CardinalDirections.get(flag)
                doors += 1
                if position in self.rooms:
                    self.rooms[position] = min(self.rooms[position], doors)
                else:
                    self.rooms[position] = doors


def get_answer1(path: pathlib.Path = INPUT):
    floor = FloorPlan(path.read_text().strip())
    return max(floor.rooms.values())


def get_answer2(path: pathlib.Path = INPUT):
    floor = FloorPlan(path.read_text().strip())
    return sum(x >= 1000 for x in floor.rooms.values())


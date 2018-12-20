#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import collections
import enum
import pathlib

from dec13.answer import Point, Direction
from dec20 import INPUT


class Directions(enum.Enum):
    NORTH = Direction('N', 0, 1)
    SOUTH = Direction('S', 0, -1)
    EAST = Direction('E', 1, 0)
    WEST = Direction('W', -1, 0)

    @classmethod
    def get(cls, icon: str, default: Direction = None):
        for direction in cls:
            if direction.value.icon == icon:
                return direction.value
        if default:
            return default
        raise KeyError(f"<{icon}> is not a valid direction.")


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
                position += Directions.get(flag)
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


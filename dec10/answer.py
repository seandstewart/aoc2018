#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import collections
import dataclasses
import logging
import operator
import pathlib
import re
from typing import Union, Tuple, NamedTuple, Iterator, List

from dec10 import INPUT
from util.helpers import load_values_list

logger = logging.getLogger(__name__)

PATTERN = re.compile(r'-?\d+')


@dataclasses.dataclass
class Point:
    x: int
    y: int

    def __iter__(self) -> Iterator[int]:
        return iter((self.x, self.y))

    def __add__(self, other: 'Point') -> 'Point':
        return type(self)(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Point') -> 'Point':
        return type(self)(self.x - other.x, self.y - other.y)

    def __isub__(self, other: 'Point'):
        self.x -= other.x
        self.y -= other.y
        return self

    def __iadd__(self, other: 'Point'):
        self.x += other.x
        self.y += other.y
        return self


@dataclasses.dataclass
class Velocity(Point):
    x: int
    y: int

    def __mul__(self, other: int) -> 'Velocity':
        if other != 1:
            return type(self)(self.x * other, self.y * other)
        else:
            return self

    def __imul__(self, other: int):
        self.x *= other
        self.y *= other
        return self


@dataclasses.dataclass
class Satellite:
    position: Point
    velocity: Velocity

    def move(self, multiplier: int = 1, reverse: bool = False):
        if reverse:
            self.position -= (self.velocity * multiplier)
        else:
            self.position += (self.velocity * multiplier)


@dataclasses.dataclass
class StarChart:
    satellites: List[Satellite]

    def __post_init__(self):
        self.entropy = None
        self.elapsed = 0
        vxs = {x.velocity.x for x in self.satellites}
        vys = {x.velocity.y for x in self.satellites}
        self.max_speed = max(max(vxs), max(vys))
        self.chart = None
        self._set_box()

    def _set_box(self):
        xs = {x.position.x for x in self.satellites}
        ys = {x.position.y for x in self.satellites}
        self.left = min(xs)
        self.right = max(xs)
        self.top = min(ys)
        self.bottom = max(ys)
        self.width = self.right - self.left
        self.height = self.bottom - self.top

    def plot(self):
        self.chart = [[None for _ in range(self.right + 1)] for __ in range(self.bottom + 1)]
        for satellite in self.satellites:
            self.chart[satellite.position.y][satellite.position.x] = '#'

    def draw(self, delim='', na_rep=' ', header=False, index=False) -> str:
        """Draw the chart in as a human-readable table."""
        table = []
        if header:
            header = f"{delim}Row{delim}{f'{delim}'.join(str(x) for x in range(self.right))}"
            sep = '-' * self.right
            table = [header, sep]
        for ix, row in enumerate(self.chart):
            row_text = f'{delim}'.join(na_rep if x is None else str(x) for x in row)
            if index:
                row_text = f'{delim}{ix}{delim}{row_text}'
            table.append(row_text)

        return '\n'.join(table)

    def move(self, multiplier: int = 1, reverse: bool = False):
        for satellite in self.satellites:
            satellite.move(multiplier, reverse)
        self._set_box()

    def scan(self):
        while True:
            # Skip ahead till everything is on the chart
            if self.top < 0 or self.left < 0:
                distance = max(abs(self.left), abs(self.top))
                multiplier = (distance // self.max_speed) or 1
                self.move(multiplier)
                self.elapsed += multiplier - 1

            # Determine our 'entropy'. If it starts going up, we're done gazing.
            entropy = self.bottom - self.top
            if self.entropy and entropy > self.entropy:
                self.move(reverse=True)
                break

            self.entropy = entropy
            self.move()
            self.elapsed += 1

        # We broke out of the loop, which means we have our message. Plot it!
        self.plot()


def get_satellites(path: pathlib.Path = INPUT) -> List[Satellite]:
    values = load_values_list(path, as_int=False)
    satellites = []
    for value in values:
        pos_x, pos_y, vel_x, vel_y = (int(x) for x in PATTERN.findall(value))
        satellites.append(
            Satellite(position=Point(pos_x, pos_y), velocity=Velocity(vel_x, vel_y))
        )
    return satellites


def get_answer1(path: pathlib.Path = INPUT):
    satellites = get_satellites(path)
    chart = StarChart(satellites)
    chart.scan()
    print(chart.draw(na_rep=' '))
    return chart

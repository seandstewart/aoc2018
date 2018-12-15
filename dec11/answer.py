#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import dataclasses
import datetime
import itertools
import logging
import operator
import re
from typing import Tuple, NamedTuple
from dataclasses import InitVar

from dec10 import INPUT
from util.helpers import load_values_list

logger = logging.getLogger(__name__)

PATTERN = re.compile(r'-?\d+')


class WinningGrid(NamedTuple):
    power: int
    cell: 'FuelCell'
    size: int


@dataclasses.dataclass
class FuelCell:
    serial_number: int
    offset: int
    x: int
    y: int

    def __post_init__(self):
        self._power = None

    def __iter__(self):
        return iter((self.x, self.y))

    @property
    def power(self):
        if self._power is None:
            level = str((self.base_power + self.serial_number) * self.rack_id)
            level = (int(level[-3]) if len(level) > 2 else 0) - self.offset
            self._power = level
        return self._power

    @property
    def rack_id(self):
        return self.x + 10

    @property
    def base_power(self):
        return self.y * self.rack_id


@dataclasses.dataclass
class FuelGrid:
    serial_number: int
    offset: int = 5
    top: InitVar[int] = 1
    left: InitVar[int] = 1
    bottom: InitVar[int] = 301
    right: InitVar[int] = 301

    def __post_init__(self, top: int, left: int, bottom: int, right: int):
        self.grid = []
        self.ranking = []
        self.populate(top, left, bottom, right)

    def populate(self, top: int, left: int, bottom: int, right: int):
        self.grid = [
            [FuelCell(self.serial_number, self.offset, x, y) for x in range(left, right)]
            for y in range(top, bottom)
        ]

    def get(self, x: int, y: int) -> FuelCell:
        return self.grid[y - 1][x - 1]

    def get_cell_group(self, x: int, y: int, size: int = 3) -> Tuple[FuelCell]:
        group = []
        for yix in range(y, y + size):
            for xix in range(x, x + size):
                try:
                    group.append(self.get(xix, yix))
                except IndexError:
                    # We're at the end a row or column
                    pass
        return tuple(group)

    def rank_cell_groups(self):
        for yix, xix in itertools.product(range(len(self.grid)), range(len(self.grid))):
            cell = self.grid[yix][xix]
            ylen = len(self.grid) - yix
            xlen = len(self.grid) - xix
            size = xlen if xlen < ylen else ylen
            best = WinningGrid(cell.power, cell, 1)
            print(f"{datetime.datetime.now()}: Cell: {cell}, Possible Groups: {size}")
            for i in range(1, size):
                group = self.get_cell_group(*cell, size=size)
                power = sum(x.power for x in group)
                if power > best.power:
                    best = WinningGrid(power, cell, size)
            self.ranking.append(best)
        self.ranking.sort(key=operator.attrgetter('power'))

    @property
    def maximum_power_group(self) -> Tuple[int, Tuple[FuelCell]]:
        if not self.ranking:
            self.rank_cell_groups()
        if self.ranking:
            power, cell = self.ranking[-1]
            return power, self.get_cell_group(*cell)


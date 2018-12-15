#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from collections import defaultdict
from itertools import product
from operator import attrgetter
from typing import Tuple, Iterator, NamedTuple

powergetter = attrgetter('power')


class FuelCell(NamedTuple):
    x: int
    y: int


class PowerGrid(NamedTuple):
    power: int
    cell: FuelCell
    size: int


class FuelGrid:

    def __init__(self, serial: int, size: int = 300):
        self.serial: int = serial
        self.size: int = size
        self.table: defaultdict = defaultdict(int)
        self.populate()

    def range(self, reducer: int = 0) -> Iterator[int]:
        stop = self.size + 1
        reducer = reducer if reducer < stop else reducer - 1
        return range(1, stop - reducer + 1)

    def populate(self):
        table = self.table
        serial = self.serial
        for x, y in product(self.range(), self.range()):
            rack_id = x + 10
            power = (((rack_id * y + serial) * rack_id) // 100) % 10 - 5
            table[(x, y)] = power + table[(x, y - 1)] + table[(x - 1, y)] - table[(x - 1, y - 1)]

    def get_power(self, x: int, y: int, size: int = 3) -> int:
        table = self.table
        x0, y0, x1, y1 = x - 1, y - 1, x + size - 1, y + size - 1
        return table[(x0, y0)] + table[(x1, y1)] - table[(x1, y0)] - table[(x0, y1)]

    def best_for_size(self, size: int):
        powers = (
            PowerGrid(self.get_power(x, y, size), FuelCell(x, y), size)
            for x, y in product(self.range(size), self.range(size))
        )
        try:
            return max(powers, key=powergetter)
        except ValueError:
            print(size)

    def best_overall(self):
        powers = (self.best_for_size(s) for s in self.range())
        return max(powers, key=powergetter)


def get_answer1(serial: int, size: int = 3) -> Tuple[int, int, int]:
    grid = FuelGrid(serial)
    return grid.best_for_size(size)


def get_answer2(serial: int) -> Tuple[int, int, int, int]:
    grid = FuelGrid(serial)
    return grid.best_overall()

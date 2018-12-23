#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import dataclasses
import enum
import functools
import itertools
from typing import Dict, Tuple

import numba
import numpy
from numba import intp

from dec22 import INPUT
from util.containers import Point, CardinalDirections


# @numba.jit(nopython=True)
@functools.lru_cache(None)
def calc_erosion_level(index: int, depth: int, modulo: int):
    return (index + depth) % modulo


# @numba.jit(nopython=True)
@functools.lru_cache(None)
def mul(x: int, y: int):
    return x * y


# @numba.jit(nopython=True)
@functools.lru_cache(None)
def mod(x: int, y: int):
    return x % y


class TerrainType(enum.IntEnum):
    ROCKY = 0
    WET = 1
    NARROW = 2

    @classmethod
    @functools.lru_cache(None)
    def get(cls, value: int):
        modulo = mod(value, len(cls))
        for terrain in cls:
            if modulo == terrain:
                return terrain
        raise TypeError


@dataclasses.dataclass
class Terrain:
    loc: Point
    type: TerrainType
    index: int
    erosion: int


class CaveSystem:
    OXMUL = 48271
    OYMUL = 16807
    MODULO = 20183

    def __init__(self, depth: int, target: Point):
        self.depth: int = depth
        self.target: Point = target
        self.cave_map: Dict[Tuple, Terrain] = {}
        self.populate()

    def get_erosion_level(self, index: int):
        return calc_erosion_level(index, self.depth, self.MODULO)

    def get_geo_index(self, point: Point):
        if point in {self.target, (0, 0)}:
            return 0
        if point.x == 0:
            return mul(point.y, self.OXMUL)
        if point.y == 0:
            return mul(point.x, self.OYMUL)
        neighbor1 = self.cave_map[(point.x - 1, point.y)]
        neighbor2 = self.cave_map[(point.x, point.y - 1)]
        return mul(neighbor2.index, neighbor1.index)

    def populate(self):
        for x, y in itertools.product(range(self.target.x + 1), range(self.target.y + 1)):
            point = Point(x, y)
            index = self.get_geo_index(point)
            erosion = self.get_erosion_level(index)
            terrain = TerrainType.get(erosion)
            terrain = Terrain(point, terrain, index, erosion)
            self.cave_map[tuple(point)] = terrain

    def get_target_risk_level(self):
        return sum(x.type for x in self.cave_map.values())


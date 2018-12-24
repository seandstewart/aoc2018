#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import dataclasses
import enum
import functools
import itertools
from copy import copy
from typing import Dict, Tuple

import numpy as np

from dec22 import INPUT
from util.containers import Point


class TerrainType(enum.IntEnum):
    ROCKY = 0
    WET = 1
    NARROW = 2

    @classmethod
    @functools.lru_cache(None)
    def get(cls, value: int):
        for terrain in cls:
            if value == terrain:
                return terrain
        raise TypeError


@dataclasses.dataclass
class Terrain:
    loc: Point
    type: TerrainType


class CaveSystem:
    OXMUL = 48271
    OYMUL = 16807
    MODULO = 20183
    PADDING = 3

    def __init__(self, depth: int, target: Point):
        self.depth: int = depth
        self.target: Point = target
        self.xmax = self.target.x * self.PADDING
        self.ymax = self.target.y * self.PADDING
        self.cave = np.empty((self.xmax, self.ymax), dtype=int)
        self.cave_types = None
        self.cave_map = {}
        self.populate()

    def xrange(self, start: int = 1):
        return range(start, self.xmax)

    def yrange(self, start: int = 1):
        return range(start, self.ymax)

    def populate(self):
        # Set the 0-indexes
        xx, yy = np.meshgrid(np.arange(self.xmax), np.arange(self.ymax), indexing="ij")
        self.cave[xx == 0] = (yy[xx == 0] * self.OXMUL + self.depth) % self.MODULO
        self.cave[yy == 0] = (xx[yy == 0] * self.OYMUL + self.depth) % self.MODULO
        # Calculate erosion levels
        for x, y in itertools.product(self.xrange(), self.yrange()):
            self.cave[x, y] = (
                (self.cave[x - 1, y] % self.MODULO) * (self.cave[x, y - 1] % self.MODULO) + self.depth
            ) % self.MODULO
        # Target is equal to start
        self.cave[tuple(self.target)] = self.depth
        self.cave_types = self.cave % len(TerrainType)
        # Populate the mapping for easy debugging
        for x, y in itertools.product(self.xrange(start=0), self.yrange(start=0)):
            terrain_type = TerrainType.get(self.cave_types[x, y])
            loc = Point(x, y)
            self.cave_map[x, y] = Terrain(loc, terrain_type)

    def draw(self):
        rows = []
        for y in range(self.target.y + 6):
            row = []
            for x in range(self.target.x + 6):
                loc = Point(x, y)
                terrain = self.cave_map[loc]
                types = ['.', '=', '|']
                if loc == (0, 0):
                    ico = 'M'
                elif loc == self.target:
                    ico = 'T'
                else:
                    ico = types[terrain.type.value]
                row.append(ico)
            rows.append(''.join(row))
        return '\n'.join(rows)

    def get_target_risk_level(self):
        return self.cave_types[:self.target.x + 1, :self.target.y + 1].sum()


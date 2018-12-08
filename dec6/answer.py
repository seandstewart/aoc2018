#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import collections
import dataclasses
import functools
import logging
import pathlib
import string
from operator import itemgetter
from typing import List, NewType, Pattern, NamedTuple, Hashable, Union, Callable, Iterator, Dict, Tuple, Set

from dec6 import INPUT
from util import Value
from util.box import BoxArea, Point, Coordinate, Coordinates
from util.helpers import load_values_list, manhattan_distance

logger = logging.getLogger(__name__)


def get_coordinates(path: pathlib.Path = INPUT, delim: str = ', ') -> Coordinates:
    values = load_values_list(path, as_int=False)
    coords = []
    for value in values:
        x, y = value.split(delim)
        coords.append((int(x), int(y),))
    return coords


def get_city_slickers(path: pathlib.Path = INPUT, delim: str = ', ') -> List['CitySlicker']:
    coords = get_coordinates(path, delim)
    ids = (f"{a}{b}" for a in string.ascii_uppercase for b in string.ascii_uppercase)
    return [CitySlicker(x, *y) for x, y in zip(ids, coords)]


@functools.total_ordering
class Closest(NamedTuple):
    dist: int
    slickers: List['CitySlicker']

    def __lt__(self, other) -> bool:
        if isinstance(other, int):
            return self.dist < other
        return super(Closest, self).__lt__(other)

    def __eq__(self, other) -> bool:
        if isinstance(other, int):
            return self.dist == other
        return super(Closest, self).__eq__(other)


@functools.total_ordering
@dataclasses.dataclass
class Area:
    coords: Set[Coordinate] = dataclasses.field(default_factory=set)

    @property
    def size(self):
        return len(self.coords)

    def __int__(self):
        return self.size

    def __lt__(self, other) -> bool:
        if isinstance(other, int):
            return self.size < other
        return super(Area, self).__lt__(other)

    def __eq__(self, other) -> bool:
        if isinstance(other, int):
            return self.size == other
        return super(Area, self).__eq__(other)


@dataclasses.dataclass
class CitySlicker:
    id: str
    x: Point
    y: Point
    finite: bool = True
    area: Area = dataclasses.field(default_factory=Area)

    @property
    def area_id(self):
        return self.id.lower()

    def __iter__(self) -> Iterator[Point]:
        return iter((self.x, self.y))

    def __getitem__(self, item: int) -> Point:
        return tuple(self)[item]


class CityPlot(BoxArea):
    INTERSECTION = '.'

    def __init__(self, *slickers: CitySlicker):
        if slickers:
            ymax, xmax = max(slickers, key=itemgetter(1)).y + 1, max(slickers, key=itemgetter(0)).x + 1
        else:
            ymax, xmax = self.YMAX, self.XMAX
        self.boxes: Dict[str, CitySlicker] = {}
        self.finite: Set[str] = set()
        self.infinite: Set[str] = set()
        super(CityPlot, self).__init__(*slickers, ymax=ymax, xmax=xmax)

    def lives_on_edge(self, coord: Union[CitySlicker, Coordinate]):
        x, y = coord
        return x in (0, self.XMAX - 1) or y in (0, self.YMAX - 1)

    def get_total_distance(self, coord: Union[Coordinate, CitySlicker]) -> int:
        total = 0
        for slicker in self.boxes.values():
            total += manhattan_distance(coord, slicker)
        return total

    def get_largest_safe_area(self, max_dist: int = 1000) -> int:
        region_size = 0
        for x in range(self.XMAX):
            for y in range(self.YMAX):
                if self.get_total_distance((x, y,)) < max_dist:
                    region_size += 1
        return region_size

    def get_finite_largest_area(self) -> int:
        return max(int(self.boxes[x].area) for x in self.finite)

    def populate(self, *slickers: CitySlicker):
        for slicker in slickers:
            x, y = slicker
            self.boxes[slicker.id] = slicker
            self.matrix[y][x] = slicker.id
            slicker.area.coords.add((x, y,))

        # Populate the areas
        for x in range(self.XMAX):
            for y in range(self.YMAX):
                coord: Coordinate = (x, y,)
                closest: Closest = None
                for slicker in self.boxes.values():
                    distance = manhattan_distance(coord, slicker)

                    if closest is None or distance < closest.dist:
                        closest = Closest(distance, [slicker])
                    elif closest and distance == closest.dist:
                        closest.slickers.append(slicker)

                if closest:
                    # We've got an intersection
                    if len(closest.slickers) > 1:
                        self.matrix[y][x] = self.INTERSECTION
                    # Give it to this guy otherwise
                    else:
                        slicker = closest.slickers[-1]
                        slicker.finite = all(not self.lives_on_edge(x) for x in slicker.area.coords)
                        if slicker.finite:
                            self.finite.add(slicker.id)
                        else:
                            if slicker.id in self.finite:
                                self.finite.remove(slicker.id)
                            self.infinite.add(slicker.id)

                        if closest.dist > 0:
                            self.matrix[y][x] = slicker.area_id
                            for slicker in closest.slickers:
                                slicker.area.coords.add(coord)



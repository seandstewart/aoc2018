#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import dataclasses
import pathlib
import re
from typing import NewType, Tuple, ClassVar, Pattern, Hashable, Union, List, Iterable, Dict, Set

from dec3 import INPUT
from util import Value

BoundingBoxTuple = NewType('BoundingBoxTuple', Tuple[int, int, int, int, int])
Matrix = NewType('Matrix', List[List[Union[Hashable, None]]])
BoxID = NewType('BoxID', Union[str, int])
Point = NewType('Point', int)
Points = NewType('Points', List[int])
Coordinate = NewType('Coordinate', Tuple[Point, Point])
Coordinates = NewType('Coordinates', Iterable[Coordinate])


@dataclasses.dataclass(frozen=True)
class BoundingBox:
    BOUNDING_BOX_PATTERN: ClassVar[Pattern] = re.compile(
        r'#(?P<id>\d+)\s@\s(?P<left>\d+),(?P<top>\d+):\s(?P<width>\d+)x(?P<height>\d+)'
    )
    id: BoxID
    top: int
    left: int
    width: int
    height: int

    @classmethod
    def from_str(cls, value: Value) -> Union['BoundingBox', None]:
        match = cls.BOUNDING_BOX_PATTERN.match(value)
        if match:
            box = cls(
                id=match.group('id'),
                top=int(match.group('top')),
                left=int(match.group('left')),
                width=int(match.group('width')),
                height=int(match.group('height'))
            )
            return box

    @property
    def right(self) -> int:
        return self.left + self.width - 1

    @property
    def bottom(self) -> int:
        return self.top + self.height - 1

    @property
    def xrange(self) -> range:
        return range(self.left, self.right + 1)

    @property
    def yrange(self) -> range:
        return range(self.top, self.bottom + 1)

    @property
    def area(self) -> int:
        return self.width * self.height

    @property
    def coordinates(self) -> Coordinates:
        coordinates = []
        for y in self.yrange:
            for x in self.xrange:
                coordinates.append((y, x,))

        return coordinates

    @classmethod
    def compare(cls, left: 'BoundingBox', right: Union['BoundingBox', Value, BoundingBoxTuple]) \
            -> Union[Tuple[None, None, None], Tuple['BoundingBox', Points, Points]]:
        xinter, yinter = None, None
        if isinstance(right, str):
            right = cls.from_str(right)
        elif isinstance(right, tuple):
            right = cls(*right)
        if right:
            xinter = sorted(list(set(left.xrange) & set(right.xrange)))
            yinter = sorted(list(set(left.yrange) & set(right.yrange)))

        return right, xinter, yinter

    @classmethod
    def gen_id(cls, lx: int, rx: int, ty: int, by: int, extra='&'):
        return f'{hash((lx, rx, ty, by,))}{extra}'

    def __and__(self, other: Union['BoundingBox', Value, BoundingBoxTuple]) \
            -> Union['BoundingBox', None]:
        """Check for an intersection between two bounding boxes.

        Create a new :class:`BoundingBox` if an intersection is found."""
        other, xinter, yinter = self.compare(self, other)
        if xinter and yinter:
            return type(self)(
                id=self.gen_id(min(xinter), max(xinter), min(yinter), max(yinter)),
                left=min(xinter),
                height=len(xinter),
                top=min(yinter),
                width=len(yinter)
            )

    def issubset(self, other: 'BoundingBox') -> bool:
        return set(self.xrange).issubset(set(other.xrange)) \
               and set(self.yrange).issubset(set(other.xrange))

    def issuperset(self, other: 'BoundingBox') -> bool:
        return set(self.xrange).issuperset(set(other.xrange)) \
               and set(self.yrange).issubset(set(other.xrange))


class BoxArea:
    XMAX: int = 1000
    YMAX: int = 1000

    def __init__(self, *boxes: BoundingBox, ymax: int = YMAX, xmax: int = XMAX):
        self.YMAX = ymax
        self.XMAX = xmax
        self.matrix: Matrix = []
        self.boxes: Dict[BoxID, BoundingBox] = {x.id: x for x in boxes}
        self.overlapping: Set[BoundingBox] = set()
        self.intersections: Set[Coordinate] = set()
        self.unique: Set[BoundingBox] = set()
        self.reset()
        self.populate(*boxes)

    def reset(self):
        self.matrix = [[None for _ in range(self.XMAX)] for __ in range(self.YMAX)]
        self.boxes = {}
        self.overlapping = set()
        self.intersections = set()
        self.unique = set()

    def populate(self, *boxes: BoundingBox):
        for box in boxes:
            if box.id not in boxes:
                self.boxes[box.id] = box
            for y in box.yrange:
                yloc: List = self.matrix[y]
                for x in box.xrange:
                    other = yloc[x]
                    if other == box.id:
                        continue
                    elif other and other != 'X':
                        other = self.boxes[other]
                        if other & box:
                            self.intersections.add((x, y,))
                            self.overlapping.update({box, other})
                            if box in self.unique:
                                self.unique.remove(box)
                            if other in self.unique:
                                self.unique.remove(other)
                    else:
                        yloc[x] = box.id
                        if box not in self.overlapping:
                            self.unique.add(box)

    def draw(self, delim='', na_rep='_', header=False, index=False) -> str:
        """Draw the matrix in as a human-readable table."""
        table = []
        if header:
            header = f"{delim}Row{delim}{f'{delim}'.join(str(x) for x in range(self.XMAX))}"
            sep = '-' * self.XMAX
            table = [header, sep]
        for ix, row in enumerate(self.matrix):
            row_text = f'{delim}'.join(na_rep if x is None else str(x) for x in row)
            if index:
                row_text = f'{delim}{ix}{delim}{row_text}'
            table.append(row_text)

        return '\n'.join(table)

    def save(self, extension='txt'):
        path: pathlib.Path = INPUT.parent / f'answer1-table.{extension}'
        path.write_text(self.draw())

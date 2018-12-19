import dataclasses
import pathlib
import re
from itertools import product

from typing import NamedTuple, Tuple, NewType, List, Union

from dec17 import INPUT
from util.helpers import load_values_list, Values
from util.containers import OrderedSet

Registers = NewType('Registers', List[int])

PATTERN = re.compile(
    r'(?P<one>[xy])=(?P<val>\d+), (?P<two>[xy])=(?P<start>\d+)\.\.(?P<stop>\d+)'
)


class Point(NamedTuple):
    x: int
    y: int


@dataclasses.dataclass
class Vector:
    x: OrderedSet
    y: OrderedSet

    def __bool__(self) -> bool:
        return bool(self.x and self.y)

    def __iter__(self):
        return product(self.x, self.y)

    def __contains__(self, item: Union[int, Tuple[int, int], 'Vector']) -> bool:
        if isinstance(item, Vector):
            return bool(self.x & item.x and self.y & item.y)
        elif isinstance(item, tuple):
            any(x == item for x in self)
        else:
            super().__contains__(item)


def default_vector():
    return Vector(OrderedSet(), OrderedSet())


@dataclasses.dataclass
class VectorMap:
    boundaries: List[Vector]

    def __post_init__(self):
        self.grid = {}
        ys = []
        xs = []
        for vector in self.boundaries:
            ys.extend(vector.y)
            xs.extend(vector.x)
        self.left = min(xs)
        self.right = max(xs)
        self.top = min(ys)
        self.bottom = max(ys)
        self.grid = {tup: vector for vector in self.boundaries for tup in vector}
        self.available_area = OrderedSet(
            tup for tup in product(self.xrange(), self.yrange()) if tup not in self.grid
        )

    def xrange(self):
        return range(self.left, self.right + 1)

    def yrange(self):
        return range(self.top, self.bottom + 1)


def load_vectors(path: pathlib.Path = INPUT) -> List[Vector]:
    values: Values = load_values_list(path)
    vectors = []
    for value in values:
        print(value)
        match = PATTERN.match(value)
        kwargs = {
            match.group('one'): OrderedSet([int(match.group('val'))]),
            match.group('two'): OrderedSet(
                range(int(match.group('start')), int(match.group('stop')) + 1)
            )
        }
        vectors.append(Vector(**kwargs))

    return vectors


def get_answer1(path: pathlib.Path = INPUT):
    vectors = load_vectors(path)
    vector_map = VectorMap(vectors)

    return len(vector_map.available_area)

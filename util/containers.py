#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import enum
from collections import UserList
from typing import Optional, Iterable, Hashable, NamedTuple, Union, Tuple


class OrderedSet(UserList):

    def __init__(self, initlist: Optional[Iterable[Hashable]] = ...) -> None:
        super().__init__(initlist)

    @property
    def _set(self):
        return set(self.data)

    def __contains__(self, item: object) -> bool:
        return self._set.__contains__(item)

    def __add__(self, other: Iterable) -> 'OrderedSet':
        new = self[:]
        new.extend(other)
        return new

    def __iadd__(self, other: Iterable) -> None:
        self.extend(other)

    def __and__(self, other: Iterable) -> 'OrderedSet':
        new = self._set & set(other)
        return OrderedSet(x for x in self if x in new)

    def __iand__(self, other: Iterable) -> None:
        diff = self._set - set(other)
        for x in diff:
            try:
                self.remove(x)
            except ValueError:
                pass

    def __sub__(self, other: Iterable) -> 'OrderedSet':
        new = self._set - set(other)
        return OrderedSet(x for x in self if x in new)

    def __isub__(self, other: Iterable) -> None:
        new = self._set - set(other)
        lyst = self[:]
        for x in lyst:
            if x not in new:
                self.remove(x)

    def __or__(self, other: Iterable) -> 'OrderedSet':
        return self + OrderedSet(other)

    def __ior__(self, other: Iterable) -> None:
        self.extend(other)

    def __xor__(self, other: Iterable) -> 'OrderedSet':
        new = self._set ^ set(other)
        return OrderedSet(x for x in self if x in new) + OrderedSet(x for x in other if x in new)

    def __ixor__(self, other: Iterable) -> None:
        new = self._set ^ set(other)
        lyst = self[:]
        for x in lyst:
            if x not in new:
                self.remove(x)
        self.extend(OrderedSet(x for x in other if x in new))

    def __gt__(self, other: Iterable) -> bool:
        return self._set > set(other)

    def __ge__(self, other: Iterable) -> bool:
        return self._set >= set(other)

    def __lt__(self, other: Iterable) -> bool:
        return self._set < set(other)

    def __le__(self, other: Iterable) -> bool:
        return self._set <= set(other)

    def __eq__(self, other: Iterable) -> bool:
        return self._set == set(other)

    def extend(self, other: Iterable[Hashable]) -> None:
        other = [x for x in other if x not in self]
        super().extend(other)

    def append(self, item: Hashable) -> None:
        if item not in self:
            super().append(item)

    def add(self, item: Hashable) -> None:
        self.append(item)

    def difference(self, *others: Iterable) -> 'OrderedSet':
        new = OrderedSet(self)
        for other in others:
            new -= other
        return new

    def difference_update(self, *others: Iterable) -> None:
        for other in others:
            self -= other

    def intersection(self, *others: Iterable) -> 'OrderedSet':
        new = OrderedSet(self)
        for other in others:
            new &= other

        return new

    def intersection_update(self, *others: Iterable) -> None:
        for other in others:
            self &= other

    def symmetric_difference(self, other: Iterable) -> 'OrderedSet':
        return self ^ other

    def symmetric_difference_update(self, other: Iterable) -> None:
        self ^= other

    def union(self, *others: Iterable) -> 'OrderedSet':
        new = OrderedSet(self)
        for other in others:
            new | other
        return new

    def update(self, *others: Iterable) -> None:
        for other in others:
            self.extend(other)

    def discard(self, item: Hashable):
        try:
            self.remove(item)
        except ValueError:
            pass


class Direction(NamedTuple):
    icon: str
    x: int
    y: int


class CardinalDirections(enum.Enum):
    NORTH = Direction('N', 0, -1)
    SOUTH = Direction('S', 0, 1)
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


class Point(NamedTuple):
    x: int
    y: int

    def __add__(self, other: Union['Point', Direction, Tuple[int, int]]):
        if len(other) == 2:
            x, y = other
        else:
            x, y = other.x, other.y
        return Point(self.x + x, self.y + y)

    def __radd__(self, other: Union['Point', Direction]):
        return self.__add__(other)

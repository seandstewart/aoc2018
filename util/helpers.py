#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import logging
import pathlib
from collections import MutableSet, UserList
from typing import NewType, List, Union, Dict, Hashable, Tuple, Sequence, Iterable, Set, Any, \
    Generator, Iterator, Optional

logger = logging.getLogger(__name__)
Values = NewType('Values', List[Union[int, str]])


def load_values_list(path: pathlib.Path, as_int: bool = False) -> Values:
    values: Values = []
    if path.exists():
        with open(path) as file:
            values: Values = [x.strip('\n') for x in file.readlines() if x.strip()]
            if as_int:
                values: Values = [int(x) for x in values]
    else:
        logger.error("Couldn't locate input at: %s", path)

    return values


def split_dict_by_values(dikt: Dict[Hashable, Hashable]) -> Tuple[Dict[Hashable, Hashable], ...]:
    values = set(dikt.values())
    split = tuple(({x: y for x, y in dikt.items() if y == value} for value in values))
    return split


def cut_iter(x: Sequence, y: Sequence) -> Tuple[int, Sequence, Sequence]:
    """A naive method to provide a rough len diff and two equidistant iters

    Examples
    --------
    >>> x = 'same'
    >>> y = 'samesies'
    >>> cut_iter(x, y)
    (4, 'same', 'same')
    >>> x = 'same'
    >>> y = 'some'
    >>> cut_iter(x, y)
    (0, 'same', 'some')
    """
    results = (0, x, y,)

    if len(x) != len(y):
        longer, shorter = x, y
        if len(y) > len(x):
            longer, shorter = y, x

        diff = len(longer) - len(shorter)
        trimmed = longer[:len(shorter)]
        results = (diff, trimmed, shorter,)

    return results


def levenshtein_distance(x: Sequence, y: Sequence) -> int:
    """Calculate Levenshtein distance between the two iterables given.
    Raises
    ------
    TypeError
        If types are not iterable

    References
    ----------
    https://docs.python.org/2/glossary.html#term-iterable
    https://en.wikipedia.org/wiki/Levenshtein_distance

    Examples
    --------
    >>> levenshtein_distance('same', 'samesies')
    4
    >>> levenshtein_distance('same', 'salmon')
    4
    >>> levenshtein_distance('same', 'sort')
    3
    >>> levenshtein_distance('same', 'same')
    0
    >>> levenshtein_distance([0, 1, 2], [0, 1, 3, 5])
    2
    >>> levenshtein_distance([0, 1, 2], [0, 1, 3])
    1

    """
    if hasattr(x, '__iter__') or hasattr(x, '__getitem__'):
        dist, x, y = cut_iter(x, y)
        for ix, sub in enumerate(x):
            dist += int(y[ix] != sub)

    else:
        raise TypeError(
            f"Must provide iterables. Provided: {type(x)} (x), {type(y)} (y)"
        )

    return dist


def diffs(x: Sequence, y: Sequence, right: bool = True) -> Set[Any]:
    return set(sub if right else y[ix] for ix, sub in enumerate(x) if y[ix] != sub)


def flatten_iter(iterable: Iterable[Iterable]):
    try:
        result = type(iterable)()
    except TypeError:
        result = []
    for entry in iterable:
        result += entry
    return result


def manhattan_distance(a: Sequence, b: Sequence) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def chunks(l: Sequence, n: int) -> Iterator[Sequence]:
    """Yield successive n-sized chunks from l."""
    return (l[i:i + n] for i in range(0, len(l), n))


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

    def extend(self, other: Iterable[Hashable]):
        other = [x for x in other if x not in self]
        super().extend(other)

    def append(self, item: Hashable):
        if item not in self:
            self.append(item)

    def add(self, item: Hashable):
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

    def intersection_update(self, *others: Iterable) -> 'OrderedSet':
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

#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import logging
import pathlib
from typing import NewType, List, Union, Dict, Hashable, Tuple, Sequence, Iterable, Set, Any, \
    Iterator

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

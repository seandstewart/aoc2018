#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import collections
import logging
import pathlib
from operator import itemgetter
from typing import List, NewType, Pattern, NamedTuple, Hashable, Union, Callable

from dec5 import INPUT
from util import Value
from util.helpers import load_values_list

logger = logging.getLogger(__name__)


Comparator = NewType('Comparator', Callable[[str, str], bool])


def get_string(path: pathlib.Path = INPUT) -> Value:
    return load_values_list(path, as_int=False)[-1]


def compare_char_case(a: str, b: str):
    return a.swapcase() == b


def remove_matching_chars(value: str, cmp: Comparator = compare_char_case) -> str:
    stack, reduced = collections.deque(), collections.deque()
    for ix, char in enumerate(value):
        if stack and cmp(char, value[stack[-1]]):
            stack.pop()
            reduced.pop()
        else:
            stack.append(ix)
            reduced.append(char)

    return "".join(reduced)


def compute_shortest_string(value: str, cmp: Comparator = compare_char_case) -> str:
    chars = set(char.lower() for char in value)
    strings = collections.deque()
    for char in chars:
        reduced = remove_matching_chars(value.replace(char, "").replace(char.upper(), ""), cmp)
        strings.append((len(reduced), reduced,))

    strings = sorted(strings, key=itemgetter(0))
    return strings[0][1]

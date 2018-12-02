#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import logging
import pathlib
from typing import NewType, Dict, Set

from dec2 import INPUT
from dec2.answer1 import Value
from util.helpers import Values, load_values_list, levenshtein_distance, diffs
from util.bktree import BKTree, Distance

logger = logging.getLogger(__name__)

Repeaters = NewType('Repeaters', Dict[Value, Set[Value]])
Diffs = NewType('Diffs', Dict[Value, Set[Value]])


def locate_matches(path: pathlib.Path = INPUT, max_dist: Distance = 1) -> Repeaters:
    values: Values = load_values_list(path, as_int=False)
    candidates = set(values)
    repeaters: Repeaters = {}
    tree = BKTree(levenshtein_distance, *candidates)
    while candidates:
        candidate = candidates.pop()
        matches = set(y for x, y in tree.match(candidate, max_dist) if y != candidate)
        if matches:
            repeaters[candidate] = matches
            candidates -= set(matches)

    return repeaters


def get_intersections(repeaters: Repeaters) -> Diffs:
    diffmap: Diffs = {}
    for value, matches in repeaters.items():
        diffmap[value] = set(''.join(v for v in value if v not in diffs(value, x)) for x in matches)

    return diffmap

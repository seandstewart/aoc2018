#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import collections
import logging
import pathlib
from functools import reduce
from typing import NewType, List, Dict

from dec2 import INPUT
from util.helpers import load_values_list

logger = logging.getLogger(__name__)

Value = NewType('Value', str)
Iterations = NewType('Iterations', int)
Values = NewType('Values', List[Value])
RepeatOffenders = NewType('RepeatOffenders', Dict[int, int])


def count_repeat_offenders(path: pathlib.Path = INPUT, max_repeats: int = 3) -> RepeatOffenders:
    max_repeats: int = max_repeats + 1 if max_repeats > 2 else 3
    values: Values = load_values_list(path, as_int=False)
    offenders: RepeatOffenders = collections.defaultdict(int)
    for value in values:
        counter = collections.Counter(value)
        logger.debug("Line <%s>: %s", value, counter)
        for iteration in range(2, max_repeats):
            if iteration in counter.values():
                offenders[iteration] += 1
        logger.debug(offenders)
    return offenders


def get_checksum(repeaters: RepeatOffenders) -> int:
    return reduce(lambda x, y: x * y, repeaters.values())





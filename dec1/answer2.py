#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import logging
import pathlib
from itertools import accumulate, cycle
from typing import NewType, Set, Iterator

from dec1 import INPUT
from util.helpers import Values, load_values_list

logger = logging.getLogger(__name__)

Total = NewType('Total', int)
Seen = NewType('Seen', Set[Total])
Duped = NewType('Duped', Iterator[Total])


def iter_duped_totals(path: pathlib.Path = INPUT) -> Duped:
    values: Values = load_values_list(path)
    seen: Seen = set()
    duped: Duped = (total for total in accumulate(cycle(values)) if total in seen or seen.add(total))
    return duped

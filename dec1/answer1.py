#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import logging
import pathlib
from typing import NewType

from dec1 import INPUT
from util.helpers import load_values_list

logger = logging.getLogger(__name__)

Sum = NewType('Sum', int)


def sum_file(path: pathlib.Path = INPUT) -> Sum:
    total: Sum = sum(load_values_list(path))
    return total

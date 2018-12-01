#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import logging
import os
import pathlib
from typing import NewType, List

logger = logging.getLogger(__name__)

BASEDIR = pathlib.Path(os.path.dirname(__file__)).resolve()

Values = NewType('Values', List[int])


def load_values_list(path: pathlib.Path) -> Values:
    values: Values = []
    if path.exists():
        with open(path) as file:
            values: Values = [int(x) for x in file.readlines()]
    else:
        logger.error("Couldn't locate input at: %s", path)

    return values

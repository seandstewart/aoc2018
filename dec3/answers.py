#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import logging
import pathlib
from typing import List, Sequence, Set

from dec3 import INPUT
from util import Values
from util.box import BoundingBox, BoxArea
from util.helpers import load_values_list

logger = logging.getLogger(__name__)


def get_boxes(path: pathlib.Path = INPUT) -> List[BoundingBox]:
    values: Values = load_values_list(path, as_int=False)
    return [BoundingBox.from_str(x) for x in values if BoundingBox.BOUNDING_BOX_PATTERN.match(x)]


def get_overlapping_area(boxes: Sequence[BoundingBox]) -> int:
    boxmap = BoxArea(*boxes)
    return len(boxmap.intersections)


def get_unique_boxes(boxes: Sequence[BoundingBox]) -> Set[BoundingBox]:
    boxmap = BoxArea(*boxes)
    return boxmap.unique

#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from collections import defaultdict
from itertools import product
from typing import Tuple


def summed_area_table(serial: int) -> defaultdict:
    table = defaultdict(int)
    for x, y in product(range(1, 301), range(1, 301)):
        rack_id = x + 10
        power = (((rack_id * y + serial) * rack_id) // 100) % 10 - 5
        table[(x, y)] = power + table[(x, y - 1)] + table[(x - 1, y)] - table[(x - 1, y - 1)]
    return table


def region_sum(table: defaultdict, size: int, x: int, y: int) -> int:
    x0, y0, x1, y1 = x - 1, y - 1, x + size - 1, y + size - 1
    return table[(x0, y0)] + table[(x1, y1)] - table[(x1, y0)] - table[(x0, y1)]


def best(table: defaultdict, size: int) -> Tuple[int, int, int]:
    powers = []
    for x, y in product(range(1, 301 - size + 1), range(1, 301 - size + 1)):
        power = region_sum(table, size, x, y)
        powers.append((power, x, y))

    return max(powers)


def get_answer1(serial: int, size: int = 3) -> Tuple[int, int, int]:
    table = summed_area_table(serial)
    return best(table, size)


def get_answer2(serial: int) -> Tuple[int, int, int, int]:
    table = summed_area_table(serial)
    powers = (best(table, s) + (s,) for s in range(1, 301))
    return max(powers)

#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from dec2 import answer1, EXAMPLE1


def test_count_repeat_offenders():
    offenders = answer1.count_repeat_offenders(EXAMPLE1)
    assert offenders[2] == 4
    assert offenders[3] == 3


def test_get_checksum():
    assert answer1.get_checksum(answer1.count_repeat_offenders(EXAMPLE1)) == 12

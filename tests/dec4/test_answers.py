#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from dec4 import EXAMPLE, answers


def test_get_target_with_total():
    raw = answers.get_raw_log(EXAMPLE)
    parsed = answers.parse_raw_log(raw)
    target = answers.get_target_shift(parsed)
    assert target.total_sleep == 50
    assert target.guard_id == '10'


def test_get_target_with_freq():
    raw = answers.get_raw_log(EXAMPLE)
    parsed = answers.parse_raw_log(raw)
    target = answers.get_target_shift(parsed, sort='num_hits')
    assert target.num_hits == 2
    assert target.guard_id == '99'

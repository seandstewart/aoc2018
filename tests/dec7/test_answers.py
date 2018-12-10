#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from dec7 import EXAMPLE, answer
from util.helpers import load_values_list


def test_get_order_with_no_workers():
    steps = load_values_list(EXAMPLE, as_int=False)
    queue = answer.Queue(*steps)
    queue.run()
    assert "".join(x.name for x in queue.final) == 'CABDFE'


def test_get_total_seconds():
    steps = load_values_list(EXAMPLE, as_int=False)
    queue = answer.Queue(*steps, workers=2)
    for step in queue.step_map.values():
        step.duration = ord(step.name) - 64
    queue.run()
    assert queue.total_seconds == 15

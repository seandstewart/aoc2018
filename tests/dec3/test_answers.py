#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from dec3 import EXAMPLE, answers


def test_get_boxes():
    boxes = answers.get_boxes(EXAMPLE)
    assert {box.id for box in boxes} == {'1', '2', '3'}


def test_get_overlapping_area():
    boxes = answers.get_boxes(EXAMPLE)
    assert answers.get_overlapping_area(boxes) == 4


def test_get_unique_boxes():
    boxes = answers.get_boxes(EXAMPLE)
    assert answers.get_unique_boxes(boxes) == {boxes[-1]}

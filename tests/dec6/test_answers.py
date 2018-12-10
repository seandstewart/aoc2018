#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from dec6 import EXAMPLE, answer


def test_get_finite_largest_area():
    slickers = answer.get_city_slickers(EXAMPLE)
    plot = answer.CityPlot(*slickers)
    assert plot.get_finite_largest_area() == 17


def test_get_largest_safe_area():
    slickers = answer.get_city_slickers(EXAMPLE)
    plot = answer.CityPlot(*slickers)
    assert plot.get_largest_safe_area(32) == 16

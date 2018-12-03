#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from dec2 import answer2, EXAMPLE2, INPUT


def test_locate_matches():
    matches = answer2.locate_matches(EXAMPLE2)
    assert len(matches) == 1
    key = max(matches.keys())
    assert matches[key] == {'fguij'} or matches[key] == {'fghij'}


def test_get_intersections(benchmark):
    diffmap = benchmark(answer2.get_intersections, answer2.locate_matches(EXAMPLE2))
    assert len(diffmap) == 1
    key = max(diffmap.keys())
    assert diffmap[key] == {'fgij'}


def test_get_intersections_real(benchmark):
    benchmark(answer2.get_intersections, answer2.locate_matches(INPUT))

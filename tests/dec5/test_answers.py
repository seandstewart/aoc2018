#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from dec5 import EXAMPLE, answer


def test_remove_matching_chars(benchmark):
    value = answer.get_string(EXAMPLE)
    reduced = benchmark(answer.remove_matching_chars, value)
    assert reduced == "dabCBAcaDA"


def test_compute_shortest_string(benchmark):
    value = answer.get_string(EXAMPLE)
    reduced = benchmark(answer.compute_shortest_string, value)
    assert reduced == "daDA"


def test_benchmark_remove_matching_chars_real(benchmark):
    value = answer.get_string()
    benchmark(answer.remove_matching_chars, value)


def test_benchmark_compute_shortest_string_real(benchmark):
    value = answer.get_string()
    benchmark(answer.compute_shortest_string, value)

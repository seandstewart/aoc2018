#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from dec8 import EXAMPLE, answer


def test_checksum():
    license = answer.LicenseTree(EXAMPLE)
    assert license.checksum == 138


def test_root_value():
    license = answer.LicenseTree(EXAMPLE)
    assert license.root.value == 66

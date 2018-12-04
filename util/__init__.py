#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import pathlib
from typing import NewType, List

BASEDIR = pathlib.Path(os.path.dirname(__file__)).resolve()

Value = NewType('Value', str)
Values = NewType('Values', List[Value])

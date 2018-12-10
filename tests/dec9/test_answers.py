#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from dec9 import EXAMPLE, answer


def test_get_high_score():
    examples = EXAMPLE.read_text().splitlines(keepends=False)
    for example in examples:
        match = answer.PATTERN.match(example)
        game = answer.MarbleGame(int(match.group('players')), int(match.group('marbles')))
        game.play()
        assert game.winner[1] == int(match.group('score'))

#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import collections
import dataclasses
import logging
import operator
import pathlib
import re
from typing import Union, Tuple

from dec9 import INPUT

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class MarbleGame:
    num_players: int
    max_marble: int
    special: int = 23

    def __post_init__(self):
        self.bag = collections.deque(range(self.max_marble + 1))
        self.circle = collections.deque()
        self.scores = collections.defaultdict(int)

    def is_special(self, marble: int) -> bool:
        return marble and marble % self.special == 0

    @property
    def winner(self) -> Union[Tuple[int, int], None]:
        if self.scores:
            return sorted(self.scores.items(), key=operator.itemgetter(1))[-1]

    def play(self):
        self.circle.append(self.bag.popleft())
        while self.bag:
            for player in range(self.num_players):
                if not self.bag:
                    continue
                marble = self.bag.popleft()
                self.circle.rotate(2)
                if not self.is_special(marble):
                    self.circle.append(marble)
                else:
                    self.circle.rotate(-9)
                    self.scores[player] += self.circle.pop() + marble


PATTERN = re.compile(
    r'(?P<players>\d+) players; last marble is worth (?P<marbles>\d+) points'
    r'(: high score is (?P<score>\d+))?'
)


def get_answer1(path: pathlib.Path = INPUT):
    match = PATTERN.match(path.read_text())
    game = MarbleGame(int(match.group('players')), int(match.group('marbles')))
    game.play()
    return game.winner


def get_answer2(path: pathlib.Path = INPUT):
    match = PATTERN.match(path.read_text())
    game = MarbleGame(int(match.group('players')), int(match.group('marbles')) * 100)
    game.play()
    return game.winner

#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import collections
import dataclasses
import logging
import operator
from typing import Union, Tuple

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
        return marble % self.special == 0

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
                if not self.is_special(marble):
                    self.circle.rotate(2)
                    self.circle.append(marble)
                else:
                    self.circle.rotate(-7)
                    self.scores[player] += self.circle.pop() + marble
                    self.circle.rotate(-1)

from typing import List

from dec14 import INPUT

STOP = int(INPUT.read_text().strip())


class ScoreBoard:
    """Track the scores over time for 2 players."""
    def __init__(self, seek: int = 10):
        self.seek = seek
        self.scores = [3, 7]
        self.player1 = 0
        self.player2 = 1

    def step(self):
        """Get new scores and move the players on the board."""
        scores = self.scores
        score = scores[self.player1] + scores[self.player2]
        if score >= 10:
            self.scores.append(1)
        scores.append(score % 10)
        self.player1 = (self.player1 + scores[self.player1] + 1) % len(scores)
        self.player2 = (self.player2 + scores[self.player2] + 1) % len(scores)

    def iterate(self, stop: int = STOP) -> List[int]:
        """Part 1: Find the next 10 recipes after iterating for ``stop``

        To do this we iterate another 10 times and return that.
        """
        while len(self.scores) < stop + self.seek:
            self.step()
        return self.scores[stop:stop + self.seek]

    def num_scores(self, stop: int = STOP) -> int:
        """Part 2: Move the scoreboard 1 step at a time until the pattern provided by ``stop`` is matched

        Return the number of recipes made.
        """
        digits = [int(x) for x in str(stop)]
        while True:
            self.step()
            if self.scores[-len(digits) - 1:-1] == digits:
                return len(self.scores) - len(digits) - 1
            if self.scores[-len(digits):] == digits:
                return len(self.scores) - len(digits)

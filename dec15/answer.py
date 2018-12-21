import dataclasses
import heapq
import pathlib
from itertools import count
from functools import total_ordering
from operator import attrgetter
from typing import List, Set, Union

from dec15 import INPUT
from util.containers import Point, CardinalDirections
from util.helpers import manhattan_distance

positiongetter = attrgetter('position')


class DeadSoldierError(Exception):
    pass


@total_ordering
@dataclasses.dataclass
class Soldier:
    team: str
    position: Point
    hp: int = 200

    def __lt__(self, other: 'Soldier') -> bool:
        if self.hp == other.hp:
            return self.position < other.position
        else:
            return self.hp < other.hp

    def __eq__(self, other: 'Soldier') -> bool:
        return self.hp == other.hp and self.position == other.position


class TableTopGame:

    def __init__(self, lines, elf_attack=None):
        self.elf_attack = elf_attack
        self.walls = set()
        self.units = []
        self.rounds = 0
        self.left = None
        self.right = None
        self.top = None
        self.bottom = None
        self.populate(lines)

    def populate(self, lines: List[str]):
        for y, line in enumerate(lines):
            for x, icon in enumerate(line.strip()):
                if icon == '#':
                    self.walls.add(Point(y, x))
                elif icon in 'EG':
                    self.units.append(Soldier(icon, Point(y, x)))
        self.left = min(x for y, x in self.walls)
        self.right = max(x for y, x in self.walls)
        self.top = min(y for y, x in self.walls)
        self.bottom = max(y for y, x in self.walls)

    def xrange(self):
        return range(self.left, self.right + 1)

    def yrange(self):
        return range(self.top, self.bottom + 1)

    def draw(self):
        units = dict((x.position, x) for x in self.units if x.hp > 0)
        rows = []
        for y in self.yrange():
            row = []
            row_units = []
            for x in self.xrange():
                icon = '#' if (y, x) in self.walls else '.'
                unit = units.get(Point(y, x))
                if unit:
                    icon = unit.team
                    row_units.append(unit)
                row.append(icon)
            row.append('   ')
            row.append(', '.join('%s(%d)' % (unit.team, unit.hp)
                                 for unit in row_units))
            rows.append(''.join(row))
        return '\n'.join(rows) + '\n'

    def __str__(self):
        return self.draw()

    @property
    def total_hp(self):
        return sum(x.hp for x in self.units if x.hp > 0)

    def occupied_positions(self, unit=None) -> Set[Point]:
        units = set(x.position for x in self.units if x != unit and x.hp > 0)
        return self.walls | units

    def shortest_paths(self, source: Point, targets: Set[Point], occupied: Set[Point]) \
            -> List[List[Point]]:
        result, best, visited, queue = [], None, set(), [(0, 0, [source])]
        while queue:
            _, distance, path = heapq.heappop(queue)
            # Check if we have the best option
            if best and len(path) > best:
                return result
            # Check if this node is a candidate
            node: Point = path[-1]
            if node in targets:
                result.append(path)
                best = len(path)
                continue
            # Ignore nodes we've already seen
            if node in visited:
                continue
            visited.add(node)
            # Finally, check if we need to push a new entry to the queue
            for neighbor in self.get_adjacent({node}):
                if neighbor in occupied:
                    continue
                if neighbor in visited:
                    continue

                heapq.heappush(queue, (distance + 1, distance + 1, list(path) + [neighbor]))

        return result

    @staticmethod
    def get_adjacent(positions: Set[Point]) -> Set[Point]:
        return set(
            point + direction for point in positions for direction in (
                x.value for x in CardinalDirections
            )
        )

    def choose_target(self, position: Point, targets: Set[Point], occupied: Set[Point]) -> \
            Union[Point, None]:
        if not targets:
            return None
        if position in targets:
            return position
        paths = self.shortest_paths(position, targets, occupied)
        ends = [x[-1] for x in paths]
        return min(ends) if ends else None

    def choose_move(self, position: Point, target: Point, occupied: Set[Point]) -> Union[Point, None]:
        if position == target:
            return position
        paths = self.shortest_paths(position, {target}, occupied)
        starts = [x[1] for x in paths]
        return min(starts) if starts else None

    def get_move(self, unit: Soldier) -> Union[Point, None]:
        occupied = self.occupied_positions(unit)
        # Get all the enemies still alive
        targets = set(x.position for x in self.units if x.team != unit.team and x.hp > 0)
        # No valid moves
        if not targets:
            return None

        # Everyone we can hit
        in_range = self.get_adjacent(targets) - occupied
        target = self.choose_target(unit.position, in_range, occupied)
        # Nothing to do, just pass this turn
        if target is None:
            return unit.position

        move = self.choose_move(unit.position, target, occupied)
        return move

    def get_attack(self, unit: Soldier) -> Union[Soldier, None]:
        units = [
            x for x in self.units
            if x.team != unit.team and x.hp > 0
            and manhattan_distance(unit.position, x.position) == 1
        ]
        return min(units) if units else None

    def run_attack(self, unit: Soldier):
        attack = self.get_attack(unit)
        if attack:
            if self.elf_attack:
                if unit.team == 'G':
                    attack.hp -= 3
                    if attack.hp <= 0:
                        raise DeadSoldierError
                else:
                    attack.hp -= self.elf_attack
            else:
                attack.hp -= 3

    def step(self) -> bool:
        self.units.sort(key=positiongetter)
        for unit in self.units:
            # This dude's dead
            if unit.hp <= 0:
                continue
            move = self.get_move(unit)
            # This dude is useless
            if move is None:
                return False
            unit.position = move
            # Attack!
            self.run_attack(unit)
        self.rounds += 1
        return True

    def run(self):
        while self.step():
            continue
        return self.rounds, self.total_hp


def get_answer1(path: pathlib.Path = INPUT) -> int:
    lines = [x for x in path.read_text().split('\n') if x]
    rounds, hp = TableTopGame(lines).run()
    return rounds * hp


def get_answer2(path: pathlib.Path = INPUT) -> int:
    lines = [x for x in path.read_text().split('\n') if x]
    for elf_attack in count(4):
        try:
            rounds, hp = TableTopGame(lines, elf_attack).run()
            return rounds * hp
        except DeadSoldierError:
            pass


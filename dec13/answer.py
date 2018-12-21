from collections import defaultdict
from functools import total_ordering
from typing import Mapping, NewType, Dict, Tuple, List

from util.containers import Direction, Point

Movement = NewType('Movement', Mapping[Direction, Direction])


UP = Direction('^', 0, -1)
DOWN = Direction('v', 0, 1)
LEFT = Direction('<', -1, 0)
RIGHT = Direction('>', 1, 0)
INTERSECTION = '+'
FORWARD_DIAG = '/'
REVERSE_DIAG = '\\'
HORIZONTAL = '-'
VERTICAL = '|'

STRAIGHT: Movement = {UP: UP, DOWN: DOWN, LEFT: LEFT, RIGHT: RIGHT}
WEST: Movement = {UP: LEFT, DOWN: RIGHT, LEFT: DOWN, RIGHT: UP}
EAST: Movement = {UP: RIGHT, DOWN: LEFT, LEFT: UP, RIGHT: DOWN}
FORWARD_TURN: Movement = {UP: RIGHT, DOWN: LEFT, LEFT: DOWN, RIGHT: UP}
REVERSE_TURN: Movement = {UP: LEFT, DOWN: RIGHT, LEFT: UP, RIGHT: DOWN}

DIRECTION_MAP = {x.icon: x for x in (UP, DOWN, LEFT, RIGHT)}
ACTION_MAP = {
    INTERSECTION: [WEST, STRAIGHT, EAST],
    FORWARD_DIAG: FORWARD_TURN,
    REVERSE_DIAG: REVERSE_TURN,
    HORIZONTAL: STRAIGHT,
    VERTICAL: STRAIGHT
}


@total_ordering
class Cart:
    """An object which moves along a track."""
    def __init__(self, position: Point, direction: Direction):
        self.position = position
        self.direction = direction
        self.intersections = 0
        self.ok = True

    def __eq__(self, other: 'Cart') -> bool:
        return other.position == self.position

    def __lt__(self, other: 'Cart') -> bool:
        return (self.position.y, self.position.x,) < (other.position.y, other.position.x,)

    def move(self, direction: Direction = None):
        self.position = self.position + (direction or self.direction)

    def step(self, grid: Mapping):
        self.move()
        icon = grid[self.position]
        action = STRAIGHT if icon in DIRECTION_MAP else ACTION_MAP[icon]
        if isinstance(action, list):
            # Choose an action based on the divisor of the previous number of intersections
            # in relation to the number of available options
            action = action[self.intersections % len(action)]
            # Add to the index to randomize the next choice a bit
            self.intersections += 1
        self.direction = action[self.direction]

    def collides(self, other: 'Cart') -> bool:
        return self is not other and self.ok and other.ok and self.position == other.position


class CartsController:
    """A controller which moves carts along a track."""
    def __init__(self, chart: List[str]):
        self.grid: Dict[Point, str] = defaultdict(str)
        self.carts: List[Cart] = []
        self.populate(chart)
        self.surviving_carts: List[Cart] = self.carts[:]
        self.collisions: Dict[Point, Tuple[Cart, Cart]] = {}
        self.loops = 0

    @property
    def first_collision(self):
        if self.collisions:
            return next(iter(self.collisions.items()))

    @property
    def final_cart(self):
        if len(self.surviving_carts) == 1:
            return self.surviving_carts[-1]

    def populate(self, chart: List[str]):
        for y, row in enumerate(chart):
            for x, icon in enumerate(row):
                point = Point(x, y)
                self.grid[point] = icon
                if icon in DIRECTION_MAP:
                    self.carts.append(Cart(point, DIRECTION_MAP[icon]))
        self.carts.sort()

    def step(self):
        for cart in self.surviving_carts:
            cart.step(self.grid)
            for other in (x for x in self.surviving_carts if x is not cart):
                if cart.collides(other):
                    cart.ok = other.ok = False
                    self.collisions[cart.position] = (cart, other,)
        self.surviving_carts = sorted(x for x in self.surviving_carts if x.ok)

    def run(self):
        while len(self.surviving_carts) > 1:
            self.step()
            self.loops += 1

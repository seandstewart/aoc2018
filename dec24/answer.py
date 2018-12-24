#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Dr. Santa: The Py-Game
"""
import collections
import dataclasses
import enum
import operator
import pathlib
import re
import typing
import uuid
from functools import lru_cache, total_ordering

from dec24 import INPUT

ELEMENTAL_MULTIPLIER = 2
initgetter = operator.attrgetter('initiative')


class Team(enum.Enum):
    IS = 'Immune System'
    INF = 'Infection'


class Element(enum.Enum):
    BLUDG = 'bludgeoning'
    COLD = 'cold'
    FIRE = 'fire'
    RAD = 'radiation'
    SLASH = 'slashing'

    @classmethod
    @lru_cache(None, typed=True)
    def get(cls, value: str) -> 'Element':
        for el in cls:
            if value == el.value:
                return el
        raise TypeError(value)


class Attack(typing.NamedTuple):
    power: int
    initiative: int
    type: Element


class Target(typing.NamedTuple):
    group: 'UnitGroup'
    damage_est: int

    @property
    def is_alive(self):
        return self.group.is_alive


@dataclasses.dataclass
@total_ordering
class UnitGroup:
    team: Team
    id: str
    units: int
    hp: int
    attack: Attack
    weak: typing.Set[Element] = dataclasses.field(default_factory=set)
    immune: typing.Set[Element] = dataclasses.field(default_factory=set)
    PATTERN: typing.ClassVar[typing.Pattern] = re.compile(
        r"(?P<units>\d+) units each with (?P<hp>\d+) hit points "
        r"((\((?P<buffer1>weak|immune) to (?P<type1>\w+(, )?)+(; )?)?"
        r"((?P<buffer2>weak|immune) to (?P<type2>(\w+(, )?)+))?\))? ?"
        r"with an attack that does (?P<attack_power>\d+) (?P<attack_type>\w+) damage "
        r"at initiative (?P<initiative>\d+)"
    )

    @classmethod
    def from_str(cls, string: str, ident: int, team: Team = Team.IS) -> 'UnitGroup':
        match = cls.PATTERN.match(string)
        ident = f"{team.value} {ident}"
        buffers = {}
        if match.group('buffer1'):
            buffers[match.group('buffer1')] = {Element.get(x) for x in match.group('type1').split(', ')}
        if match.group('buffer2'):
            buffers[match.group('buffer2')] = {Element.get(x) for x in match.group('type2').split(', ')}

        return cls(
            team=team,
            id=ident,
            units=int(match.group('units')),
            hp=int(match.group('hp')),
            attack=Attack(
                power=int(match.group('attack_power')),
                initiative=int(match.group('initiative')),
                type=Element.get(match.group('attack_type'))
            ),
            **buffers
        )

    @property
    def power(self) -> int:
        return self.units * self.attack.power

    @property
    def total_hp(self) -> int:
        return self.units * self.hp

    @property
    def is_alive(self) -> bool:
        return self.units > 0

    def estimate_damage(self, other: 'UnitGroup') -> int:
        est = other.power
        if other.attack.type in self.weak:
            est *= ELEMENTAL_MULTIPLIER
        elif other.attack.type in self.immune:
            est = 0
        return est

    def __eq__(self, other: 'UnitGroup') -> bool:
        return (other.power, other.attack.initiative) == (self.power, self.attack.initiative)

    def __lt__(self, other: 'UnitGroup') -> bool:
        if self.power == other.power:
            return self.attack.initiative < other.attack.initiative
        return self.power < other.power

    def select_target(self, enemies: typing.Sequence['UnitGroup']) -> Target:
        selection: Target = None
        for group in enemies:
            damage_est = self.power
            if self.attack.type in group.weak:
                damage_est *= ELEMENTAL_MULTIPLIER
            # Only select if we can deal some damage
            elif self.attack.type in group.immune:
                continue

            if selection:
                # The best one yet!
                if damage_est > selection.damage_est:
                    selection = Target(group, damage_est)
                    continue
                # Break the tie...
                if damage_est == selection.damage_est:
                    # Secondary tie break
                    if selection.group.power > group.power:
                        continue
                    if group.power == selection.group.power:
                        group1 = selection.group
                        # Keep the current selection on another tie
                        selection = selection if group1.attack.initiative >= group.attack.initiative \
                            else Target(group, damage_est)
                        continue
                    # We have a winner... so far
                    if group.power > selection.group.power:
                        selection = Target(group, damage_est)
                        continue
            # If there isn't a selection yet, default to this one.
            selection = Target(group, damage_est)

        return selection

    def take_damage(self, other: 'UnitGroup'):
        damage = self.estimate_damage(other)
        print(f"Dealing {damage} damage.")
        self.units -= damage // self.hp
        print(f"Remaining units: {self.units}")


class BattlePair(typing.NamedTuple):
    group: UnitGroup
    target: Target

    @property
    def initiative(self):
        return self.group.attack.initiative

    def fight(self):
        self.target.group.take_damage(self.group)


@dataclasses.dataclass
class ImmunityWar:
    immunes: typing.List[UnitGroup]
    infects: typing.List[UnitGroup]

    @staticmethod
    def select_targets(groups, candidates) -> typing.List[BattlePair]:
        pairs: typing.List[BattlePair] = []
        for group in groups:
            # Move along...
            if not candidates:
                break
            target = group.select_target(candidates)
            if target:
                candidates.remove(target.group)
                pairs.append(BattlePair(group, target))
        pairs.sort(key=initgetter, reverse=True)
        return pairs

    def battle(self):
        pairs: typing.List[BattlePair] = []
        dead: typing.List[UnitGroup] = []
        seen_dead: typing.Set[str] = set()
        self.immunes.sort(reverse=True)
        self.infects.sort(reverse=True)
        pairs.extend(self.select_targets(self.infects, collections.deque(self.immunes)))
        pairs.extend(self.select_targets(self.immunes, collections.deque(self.infects)))
        pairs.sort(key=initgetter, reverse=True)
        for pair in pairs:
            print(f"{pair.group.id} attacking {pair.target.group.id} "
                  f"(HP: {pair.target.group.hp}) with {pair.target.damage_est} damage.")
            if pair.group.is_alive and pair.target.is_alive:
                pair.fight()
                print(f"Result: {pair.target.group.id}, Units: {pair.target.group.units}")
            if not pair.group.is_alive and pair.group.id not in seen_dead:
                dead.append(pair.group)
                seen_dead.add(pair.group.id)
            if not pair.target.is_alive and pair.target.group.id not in seen_dead:
                dead.append(pair.target.group)
                seen_dead.add(pair.target.group.id)
        self.immunes = [x for x in self.immunes if x.id not in seen_dead]
        self.infects = [x for x in self.infects if x.id not in seen_dead]
        return seen_dead

    def run_war(self):
        counter = 0
        while True:
            counter += 1
            print(f"Battle {counter}\n")
            self.battle()
            if not self.immunes or not self.infects:
                break
        return self.immunes or self.infects


def load_groups(path: pathlib.Path = INPUT) -> \
        typing.Tuple[typing.List[UnitGroup], typing.List[UnitGroup]]:
    criteria = path.read_text()
    immunes, infects = criteria.split('\n\n')
    immunes, infects = immunes.split('\n'), infects.split('\n')
    immunes.pop(0)
    infects.pop(0)
    immunes = sorted((UnitGroup.from_str(x, ix + 1) for ix, x in enumerate(immunes) if x), reverse=True)
    infects = sorted((UnitGroup.from_str(x, ix + 1, Team.INF) for ix, x in enumerate(infects) if x), reverse=True)
    return immunes, infects

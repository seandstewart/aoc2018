#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import collections
import dataclasses
import datetime
import enum
import functools
import logging
import pathlib
import re
from operator import attrgetter
from typing import List, NewType, Sequence, Set, Tuple, Pattern, NamedTuple, Hashable, Union

from dec4 import INPUT
from util import Values
from util.helpers import load_values_list

logger = logging.getLogger(__name__)


class Action(enum.Enum):
    SLEEP = 'sleep'
    SHIFT = 'shift'


class RawLogEntry(NamedTuple):
    date: datetime.datetime
    entry: str


@functools.total_ordering
@dataclasses.dataclass
class TimeRange:
    start: datetime.datetime
    stop: datetime.datetime = None

    def __lt__(self, other: 'TimeRange') -> bool:
        return self.minutes or 0 < other.minutes or 0

    def __eq__(self, other: 'TimeRange') -> bool:
        return self.minutes or 0 == other.minutes or 0

    @property
    def minutes(self) -> Union[int, None]:
        if self.stop:
            return int((self.stop - self.start).total_seconds() / 60)

    @property
    def hours(self) -> Union[int, None]:
        if self.stop:
            return int(self.minutes / 60)


class LogAction(NamedTuple):
    time: TimeRange
    action: Action


RawLog = NewType('RawLog', List[RawLogEntry])

DATE_PATTERN: str = '%Y-%m-%d %H:%M'
LOG_PATTERN: Pattern = re.compile(r'\[(?P<datestring>.+)\]\s(?P<entry>.+)')
GUARD_PATTERN: Pattern = re.compile(r'Guard\s#(?P<id>\d+)')
SLEEPS_PATTERN: Pattern = re.compile(r'falls\sasleep')
WAKES_PATTERN: Pattern = re.compile(r'wakes\sup')
LOG_SORT_KEY = attrgetter('date')


@functools.total_ordering
@dataclasses.dataclass
class GuardShift:
    id: Hashable
    time: TimeRange
    sleep_sessions: List[LogAction] = dataclasses.field(default_factory=list)

    def __lt__(self, other: 'GuardShift') -> bool:
        return self.total_minutes_slept < other.total_minutes_slept

    def __eq__(self, other: 'GuardShift'):
        return self.total_minutes_slept == other.total_minutes_slept

    @property
    def total_minutes_slept(self) -> int:
        if self.sleep_sessions:
            return sum(x.time.minutes or 0 for x in self.sleep_sessions)
        return 0

    @property
    def max_sleep_time(self) -> Union[TimeRange, None]:
        """This is the time range at which the guard had the most sleep for a session.

        Not the maximum minutes slept.
        """
        if self.sleep_sessions:
            return max((x.time for x in self.sleep_sessions))

    @property
    def max_minutes_slept(self) -> Union[int, None]:
        """This is the maximum amount of minutes slept."""
        if self.sleep_sessions:
            return self.max_sleep_time.minutes


GuardShiftLog = NewType('GuardShiftLog', List[GuardShift])


def get_raw_log(path: pathlib.Path = INPUT) -> RawLog:
    values: Values = load_values_list(path, as_int=False)
    log: RawLog = []
    for value in values:
        match = LOG_PATTERN.match(value)
        if match:
            date = datetime.datetime.strptime(match.group('datestring'), DATE_PATTERN)
            log.append(RawLogEntry(date, match.group('entry')))
    log.sort(key=LOG_SORT_KEY)

    return log


def parse_raw_log(log: RawLog) -> GuardShiftLog:
    parsed: GuardShiftLog = []
    locale: GuardShift = None
    for date, entry in log:
        match = GUARD_PATTERN.match(entry)
        if match:
            shift = GuardShift(
                id=match.group('id'),
                time=TimeRange(date)
            )
            if locale:
                locale.time.stop = date
                parsed.append(locale)
            locale = shift
            continue
        match = SLEEPS_PATTERN.match(entry)
        if match:
            locale.sleep_sessions.append(
                LogAction(
                    time=TimeRange(date),
                    action=Action.SLEEP
                )
            )
            continue
        match = WAKES_PATTERN.match(entry)
        if match:
            latest: LogAction = locale.sleep_sessions[-1]
            latest.time.stop = date
        else:
            logger.error("Couldn't match entry: %s", entry)

    if locale not in parsed:
        parsed.append(locale)

    return parsed


class MaxSleepShift(NamedTuple):
    guard_id: Hashable
    shifts: GuardShiftLog
    total_sleep: int
    most_common_sleep_minute: int = None
    num_hits: int = 0


def get_shift_sleep_freq(shifts: GuardShiftLog) -> collections.Counter:
    counter = collections.Counter()
    for shift in shifts:
        for session in shift.sleep_sessions:
            counter.update(range(session.time.start.minute, session.time.stop.minute))

    return counter


def get_max_shift(log: GuardShiftLog, sort: str = 'total_sleep') -> MaxSleepShift:
    guards = set(x.id for x in log)
    guard_sleep_maxes = []
    for guard in guards:
        shifts: GuardShiftLog = [x for x in log if x.id == guard]
        sleep_freqs = get_shift_sleep_freq(shifts)
        common_minute, num_hits = None, 0
        most_common = sleep_freqs.most_common(1)
        if most_common:
            common_minute, num_hits = most_common[0]
        total_sleep = sum(x.total_minutes_slept for x in shifts)
        guard_sleep_maxes.append(
            MaxSleepShift(
                guard_id=guard,
                shifts=shifts,
                total_sleep=total_sleep,
                most_common_sleep_minute=common_minute,
                num_hits=num_hits
            )
        )

    guard_sleep_maxes.sort(key=attrgetter(sort))
    return guard_sleep_maxes[-1]




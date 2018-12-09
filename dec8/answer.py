#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import collections
import logging
import pathlib
import uuid
from typing import NamedTuple, Hashable, List

from dec8 import INPUT
from util.helpers import load_values_list, flatten_iter

logger = logging.getLogger(__name__)


class Header(NamedTuple):
    """Defines the count of entries required for a given node"""
    children: int
    metadatum: int


class Node(NamedTuple):
    id: Hashable
    parent_id: Hashable
    header: Header
    children: List['Node']
    metadata: List[int]

    @property
    def incomplete(self) -> bool:
        return len(self.children) < self.header.children

    @property
    def value(self) -> int:
        if self.children:
            return sum(self.children[x - 1].value for x in self.metadata if x <= len(self.children))
        else:
            return sum(self.metadata)


class LicenseTree:
    def __init__(self, path: pathlib.Path = INPUT):
        self.nodes = {}
        self.root = None
        self.checksum = 0
        self.build(path)

    def __repr__(self):
        return (
            f"{type(self)}(checksum={self.checksum}, nodes={len(self.nodes)}, "
            f"value={self.root.value if self.root else None})"
        )

    def build(self, path: pathlib.Path):
        values = collections.deque(get_license_key(path))
        node: Node = None
        parent: Node = None
        gen_header: bool = True
        while values:
            if gen_header:
                header = Header(values.popleft(), values.popleft())
                node = Node(str(uuid.uuid4()), parent.id if parent else None, header, [], [])
                self.nodes[node.id] = node
                if node.parent_id is not None:
                    self.nodes[node.parent_id].children.append(node)
                if not self.root:
                    self.root = node
            if node.incomplete:
                parent = node
                gen_header = True
            else:
                node.metadata.extend((values.popleft() for _ in range(node.header.metadatum)))
                self.checksum += sum(node.metadata)
                if parent is None:
                    gen_header = True
                    continue

                node = self.nodes[node.parent_id] if node.parent_id else self.root
                gen_header = False


def get_license_key(path: pathlib.Path = INPUT) -> List[int]:
    return flatten_iter([map(int, x.split()) for x in load_values_list(path, as_int=False)])





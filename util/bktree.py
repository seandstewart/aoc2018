#!/usr/bin/python2.7
# -*- coding: UTF-8 -*-
from collections import deque
from operator import itemgetter
from typing import NewType, Callable, Sequence, Union, List, Tuple, Dict, Any, Iterator

_getitem0 = itemgetter(0)


DistanceFunc = NewType('DistanceFunc', Callable[[Sequence, Sequence], int])
Distance = NewType('Distance', int)
Entry = NewType('Entry', Union[int, str])
Tree = NewType('Tree', Tuple[Entry, Dict[Distance, 'Tree']])
FlatTree = NewType('FlatTree', Dict[Entry, Distance])
Node = NewType('Node', Tuple[Distance, List[Entry]])
Match = NewType('Match', Tuple[Distance, Entry])


class BKTree:
    """BK-tree data structure that allows fast querying of "close" match

    Given a function to calculate a distance metric

    Notes
    -----
    While intended for hamming or Levenshtein distance, this data structure offers
    the ability to build relationships using any similarity calculation, with the
    same optimizations (e.g., semantic similarity, difflib's fuzzy matching). For
    best results, your distance function should return ``int``, not ``float``

    Parameters
    ----------
    distance_func : func
        The function for calculating relative distance between two items.
        Defaults: :func:`~helpers.evals.distance`
    *items
        Optionally provide items (of the same type) which you wish to compare

    Attributes
    ----------
    distance_func
    tree : tuple dict
        (item, {dist: (item, {dist: (...), ...}, ...), ...}, ...)
        - item : int or iter
        - dist : int
            The relative distance of the "child" item(s) within the dict
    flat : dict
        A flat dict of all items available in the tree and their relative distance
        from the root node. (Not populated on init, must call :meth:`~flatten`
    """

    def __init__(self, distance_func: Callable, *items: Union[int, str]):
        self.distance_func = distance_func
        self.tree: Tree = (None, {})
        self.flat: FlatTree = {}

        _add = self.add
        for item in items:
            _add(item)

        self.distances = sorted(self.tree[1].keys())

    @staticmethod
    def extract(node) -> List[Entry]:
        """Extract all items from a given node recursively

        Parameters
        ----------
        node : tuple
            a node in the shape of :attr:`~tree`

        Returns
        -------
        items : list
        """
        _extract = BKTree.extract
        items = [node[0]]
        for child in node[1].values():
            items.append(child[0])
            for step in child[1].values():
                items.extend(_extract(step))

        return items

    def flatten(self) -> FlatTree:
        """Flatten the tree into an unordered dict of item : distance"""
        tree = self.tree
        flat = self.flat
        _extract = self.extract
        if tree[0] is not None:
            flat[tree[0]] = 0
            for dist, nodes in tree[1].iteritems():
                for node in _extract(nodes):
                    flat[node] = dist

        return flat

    def _stats(self, func: Callable) -> Node:
        """Helper method for :meth:`~max` and :meth:`~min`
        """
        nodes = self.tree[1]
        key = 0
        items = []
        if nodes:
            key = func(nodes)
            items = self.extract(nodes[key])
        node: Node = (key, items,)

        return node

    def max(self) -> Node:
        """Return the node with the highest distance from the root node"""

        return self._stats(max)

    def min(self) -> Node:
        """Return the node with the lowest distance from the root node"""

        return self._stats(min)

    def add(self, item: Entry):
        """Add given item to this tree.

        Parameters
        ----------
        item : int or str
            All items in the tree must have the same type
        """
        node = self.tree
        if node[0] is None:
            self.tree = (item, {})

        else:
            # Slight speed optimization -- avoid lookups inside the loop
            calc = self.distance_func

            while True:
                parent, children = node
                dist = calc(item, parent)
                node = children.get(dist)
                if node is None:
                    children[dist] = (item, {})
                    break

    def match(self, item: Entry, dist: int) -> List[Match]:
        """Find matches for the given item within the given distance
        """
        matches = []

        if self.tree[0] is not None:
            candidates = deque([self.tree])

            # Slight speed optimization -- avoid lookups inside the loop
            # blatantly copying pybktree
            popleft = candidates.popleft
            extend = candidates.extend
            append = matches.append
            calc = self.distance_func

            while candidates:
                candidate, children = popleft()
                cdist = calc(candidate, item)
                if cdist <= dist:
                    append((cdist, candidate))

                if children:
                    lower = cdist - dist
                    upper = cdist + dist
                    extend(c for d, c in children.items() if lower <= d <= upper)

            matches.sort(key=_getitem0)

        return matches

    def find(self, item: Entry, inclusive: bool = True, flatten: bool = True, default: Any = None) -> \
            Union[Tree, FlatTree]:
        """Find the distance node for a given item
        """
        result = default
        flat = self.flat
        if self.tree[0] is not None:
            if not flat:
                self.flatten()

            dist = flat.get(item)
            if dist is not None:
                result = self.get(dist, inclusive, flatten, default)

        return result

    @staticmethod
    def _get(dist: Distance, tree: Tree, flatten: bool, default: Any) -> Union[Tree, FlatTree]:
        """Helper method for getting nodes by distance
        """
        result = default
        root = tree[0]
        if root is not None:
            if dist == 0:
                result = root if isinstance(root, (list, set)) else [root]
            else:
                result = tree[1].get(dist, default)
                if flatten and result:
                    result = BKTree.extract(result)

        return result

    def get(self, dist: Distance, inclusive: bool = True, flatten: bool = True, default: Any=None) -> \
            Union[Tree, FlatTree]:
        """Get a node or nodes within the given distance
        """
        tree = self.tree
        result = default
        if inclusive:
            result = {
                k: self._get(k, tree, flatten, default) for k in tree[1].keys() & set(range(1, dist + 1))
            }

        elif dist in tree[1].keys():
            result = {dist: self._get(dist, tree, flatten, default)}

        return result

    def __iter__(self) -> Iterator[Tree]:
        """Return iterator over all items in this tree

        Notes
        -----
        items are yielded in arbitrary order.

        Yields
        ------
        candidate
            An item from the tree
        """
        if self.tree:
            candidates = deque([self.tree])

            # Slight speed optimization -- avoid lookups inside the loop
            popleft = candidates.popleft
            extend = candidates.extend

            while candidates:
                candidate, children = popleft()
                yield candidate
                extend(children.values())

    def __repr__(self):
        return '<{} using {} with {} top-level nodes>'.format(
            self.__class__.__name__,
            self.distance_func.__name__,
            len(self.tree[1]) if self.tree else 0,
        )

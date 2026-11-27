from copy import deepcopy
from typing import Generic, Hashable, Iterable, Iterator, Optional, Tuple, TypeVar

V = TypeVar("V", bound=Hashable)
Edge = Tuple[V, V]
_NOT_SET = object()


class GraphIterator(Iterator):

    def __init__(
        self,
        owner: "DirectedGraph",
        kind: str,
        values: Iterable,
        reverse: bool = False,
        read_only: bool = False,
    ):
        self._owner = owner
        self.kind = kind
        self._values = tuple(values)
        self._index = len(self._values) - 1 if reverse else 0
        self._step = -1 if reverse else 1
        self._last = _NOT_SET
        self.read_only = read_only

    def __iter__(self):
        return self

    def __next__(self):
        return self.move_next()

    def move_next(self):
        if self._index < 0 or self._index >= len(self._values):
            self._last = _NOT_SET
            raise StopIteration
        value = self._values[self._index]
        self._last = value
        self._index += self._step
        return deepcopy(value) if self.read_only else value

    def move_prev(self):
        previous_index = self._index - self._step
        if previous_index < 0 or previous_index >= len(self._values):
            self._last = _NOT_SET
            raise StopIteration
        self._index = previous_index
        value = self._values[self._index]
        self._last = value
        return deepcopy(value) if self.read_only else value

    @property
    def current(self):
        if self._last is _NOT_SET:
            raise RuntimeError("Итератор ещё не возвращал элемент.")
        return deepcopy(self._last) if self.read_only else self._last

    def __reversed__(self):
        return GraphIterator(
            self._owner,
            self.kind,
            reversed(self._values),
            read_only=self.read_only,
        )


class _Vertex:

    def __init__(self, value):
        self.value = value
        self.first_out = None
        self.first_in = None


class _Edge:

    def __init__(self, source, target):
        self.source = source
        self.target = target
        self.next_out = None
        self.next_in = None


class DirectedGraph(Generic[V]):

    def __init__(self, values: Optional[Iterable[V]] = None):
        self._vertices = {}
        self._edge_count = 0
        if values is not None:
            for value in values:
                self.add_vertex(value)

    def is_empty(self) -> bool:
        return not self._vertices

    def empty(self) -> bool:
        return self.is_empty()

    def clear(self) -> None:
        self._vertices.clear()
        self._edge_count = 0

    def copy(self) -> "DirectedGraph[V]":
        return deepcopy(self)

    def assign_from(self, other: "DirectedGraph[V]") -> None:
        if not isinstance(other, DirectedGraph):
            raise TypeError("Источник должен быть ориентированным графом.")
        copied = other.copy()
        self._vertices = copied._vertices
        self._edge_count = copied._edge_count

    def __eq__(self, other) -> bool:
        if not isinstance(other, DirectedGraph):
            return NotImplemented
        return set(self.vertices()) == set(other.vertices()) and set(
            self.edges()
        ) == set(other.edges())

    def __ne__(self, other) -> bool:
        return not self == other

    def __lt__(self, other) -> bool:
        if not isinstance(other, DirectedGraph):
            return NotImplemented
        return (self.vertex_count, self.edge_count) < (
            other.vertex_count,
            other.edge_count,
        )

    def __le__(self, other) -> bool:
        return self == other or self < other

    def __gt__(self, other) -> bool:
        if not isinstance(other, DirectedGraph):
            return NotImplemented
        return other < self

    def __ge__(self, other) -> bool:
        return self == other or self > other

    @property
    def vertex_count(self) -> int:
        return len(self._vertices)

    @property
    def edge_count(self) -> int:
        return self._edge_count

    def has_vertex(self, value: V) -> bool:
        return value in self._vertices

    def has_edge(self, source: V, target: V) -> bool:
        self._require_vertex(source)
        self._require_vertex(target)
        return self._find_out_edge(source, target) is not None

    def add_vertex(self, value: V) -> None:
        if value in self._vertices:
            raise ValueError("Такая вершина уже существует.")
        self._vertices[value] = _Vertex(value)

    def add_edge(self, source: V, target: V) -> None:
        source_vertex = self._require_vertex(source)
        target_vertex = self._require_vertex(target)
        if self._find_out_edge(source, target) is not None:
            raise ValueError("Такое ребро уже существует.")

        edge = _Edge(source, target)
        edge.next_out = source_vertex.first_out
        source_vertex.first_out = edge
        edge.next_in = target_vertex.first_in
        target_vertex.first_in = edge
        self._edge_count += 1

    def remove_vertex(self, value: V) -> None:
        vertex = self._require_vertex(value)
        incident = list(dict.fromkeys(self.incident_edges(value)))
        for edge in incident:
            self.remove_edge(*edge)
        del self._vertices[vertex.value]

    def remove_edge(self, source: V, target: V) -> None:
        source_vertex = self._require_vertex(source)
        target_vertex = self._require_vertex(target)
        edge = self._find_out_edge(source, target)
        if edge is None:
            raise KeyError("Ребро не найдено.")
        source_vertex.first_out = self._unlink(
            source_vertex.first_out, edge, "next_out"
        )
        target_vertex.first_in = self._unlink(
            target_vertex.first_in, edge, "next_in"
        )
        self._edge_count -= 1

    @staticmethod
    def _unlink(first, target, link_name):
        if first is target:
            return getattr(first, link_name)
        current = first
        while current is not None:
            following = getattr(current, link_name)
            if following is target:
                setattr(current, link_name, getattr(target, link_name))
                return first
            current = following
        raise RuntimeError("Повреждена внутренняя структура графа.")

    def _find_out_edge(self, source: V, target: V):
        current = self._vertices[source].first_out
        while current is not None:
            if current.target == target:
                return current
            current = current.next_out
        return None

    def _require_vertex(self, value: V):
        try:
            return self._vertices[value]
        except (KeyError, TypeError) as error:
            raise KeyError(f"Вершина {value!r} не найдена.") from error

    def degree(self, value: V) -> int:
        return self.out_degree(value) + self.in_degree(value)

    def out_degree(self, value: V) -> int:
        current = self._require_vertex(value).first_out
        count = 0
        while current is not None:
            count += 1
            current = current.next_out
        return count

    def in_degree(self, value: V) -> int:
        current = self._require_vertex(value).first_in
        count = 0
        while current is not None:
            count += 1
            current = current.next_in
        return count

    def edge_degree(self, source: V, target: V) -> int:
        if not self.has_edge(source, target):
            raise KeyError("Ребро не найдено.")
        incident = set(self.incident_edges(source))
        incident.update(self.incident_edges(target))
        incident.discard((source, target))
        return len(incident)

    def vertices(self) -> GraphIterator:
        return GraphIterator(self, "vertex", self._vertices.keys())

    def edges(self) -> GraphIterator:
        return GraphIterator(self, "edge", self._all_edges())

    def incident_edges(self, value: V) -> GraphIterator:
        return GraphIterator(self, "incident_edge", self._incident(value))

    def adjacent_vertices(self, value: V) -> GraphIterator:
        return GraphIterator(self, "adjacent_vertex", self._adjacent(value))

    def incoming_edges(self, value: V) -> GraphIterator:
        self._require_vertex(value)
        current = self._vertices[value].first_in
        result = []
        while current is not None:
            result.append((current.source, current.target))
            current = current.next_in
        return GraphIterator(self, "incoming_edge", result)

    def _all_edges(self):
        result = []
        for value in self._vertices:
            current = self._vertices[value].first_out
            while current is not None:
                result.append((current.source, current.target))
                current = current.next_out
        return result

    def _incident(self, value: V):
        self._require_vertex(value)
        result = list(self._outgoing(value))
        result.extend(self._incoming(value))
        return list(dict.fromkeys(result))

    def _outgoing(self, value: V):
        current = self._vertices[value].first_out
        while current is not None:
            yield (current.source, current.target)
            current = current.next_out

    def _incoming(self, value: V):
        current = self._vertices[value].first_in
        while current is not None:
            yield (current.source, current.target)
            current = current.next_in

    def _adjacent(self, value: V):
        self._require_vertex(value)
        current = self._vertices[value].first_out
        while current is not None:
            yield current.target
            current = current.next_out

    def const_vertices(self) -> GraphIterator:
        return GraphIterator(
            self, "vertex", self._vertices.keys(), read_only=True
        )

    def const_edges(self) -> GraphIterator:
        return GraphIterator(
            self, "edge", self._all_edges(), read_only=True
        )

    def const_incident_edges(self, value: V) -> GraphIterator:
        return GraphIterator(
            self, "incident_edge", self._incident(value), read_only=True
        )

    def const_adjacent_vertices(self, value: V) -> GraphIterator:
        return GraphIterator(
            self, "adjacent_vertex", self._adjacent(value), read_only=True
        )

    def reverse_vertices(self) -> GraphIterator:
        return GraphIterator(self, "vertex", self._vertices.keys(), reverse=True)

    def reverse_edges(self) -> GraphIterator:
        return GraphIterator(self, "edge", self._all_edges(), reverse=True)

    def reverse_incident_edges(self, value: V) -> GraphIterator:
        return GraphIterator(
            self, "incident_edge", self._incident(value), reverse=True
        )

    def reverse_adjacent_vertices(self, value: V) -> GraphIterator:
        return GraphIterator(
            self, "adjacent_vertex", self._adjacent(value), reverse=True
        )

    def reverse_const_vertices(self) -> GraphIterator:
        return GraphIterator(
            self, "vertex", self._vertices.keys(), reverse=True,
            read_only=True
        )

    def reverse_const_edges(self) -> GraphIterator:
        return GraphIterator(
            self, "edge", self._all_edges(), reverse=True, read_only=True
        )

    def reverse_const_incident_edges(self, value: V) -> GraphIterator:
        return GraphIterator(
            self, "incident_edge", self._incident(value), reverse=True,
            read_only=True
        )

    def reverse_const_adjacent_vertices(self, value: V) -> GraphIterator:
        return GraphIterator(
            self, "adjacent_vertex", self._adjacent(value), reverse=True,
            read_only=True
        )

    def remove_vertex_at(self, iterator: GraphIterator) -> V:
        value = self._iterator_value(iterator, "vertex")
        self.remove_vertex(value)
        return value

    def remove_edge_at(self, iterator: GraphIterator) -> Edge:
        edge = self._iterator_value(iterator, "edge")
        self.remove_edge(*edge)
        return edge

    def _iterator_value(self, iterator, expected_kind):
        if not isinstance(iterator, GraphIterator):
            raise TypeError("Ожидается итератор графа.")
        if iterator._owner is not self or iterator.kind != expected_kind:
            raise ValueError("Итератор принадлежит другому контейнеру.")
        if iterator._last is _NOT_SET:
            raise RuntimeError("Итератор ещё не возвращал элемент.")
        return iterator._last

    def __iter__(self):
        return self.vertices()

    def __str__(self) -> str:
        vertex_text = ", ".join(str(value) for value in self.vertices())
        edge_text = ", ".join(
            f"{source} -> {target}" for source, target in self.edges()
        )
        return f"Вершины: [{vertex_text}]\nРёбра: [{edge_text}]"

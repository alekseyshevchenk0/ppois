import pytest

from graph import DirectedGraph


def make_graph():
    graph = DirectedGraph(["A", "B", "C", "D"])
    graph.add_edge("A", "B")
    graph.add_edge("A", "C")
    graph.add_edge("B", "C")
    graph.add_edge("C", "A")
    return graph


def test_empty_add_and_counts():
    graph = DirectedGraph()
    assert graph.is_empty()
    assert graph.empty()
    graph.add_vertex("A")
    assert not graph.is_empty()
    assert graph.vertex_count == 1
    assert graph.edge_count == 0


def test_add_and_find_edges():
    graph = make_graph()
    assert graph.has_vertex("A")
    assert graph.has_edge("A", "B")
    assert not graph.has_edge("B", "A")
    assert graph.vertex_count == 4
    assert graph.edge_count == 4


def test_duplicate_vertex_and_edge():
    graph = make_graph()
    with pytest.raises(ValueError):
        graph.add_vertex("A")
    with pytest.raises(ValueError):
        graph.add_edge("A", "B")


def test_missing_vertices_and_edge():
    graph = make_graph()
    assert not graph.has_vertex("Z")
    with pytest.raises(KeyError):
        graph.has_edge("A", "Z")
    with pytest.raises(KeyError):
        graph.add_edge("Z", "A")
    with pytest.raises(KeyError):
        graph.remove_edge("A", "D")


def test_degrees():
    graph = make_graph()
    assert graph.out_degree("A") == 2
    assert graph.in_degree("A") == 1
    assert graph.degree("A") == 3
    assert graph.edge_degree("A", "B") == 3


def test_iterators_vertices_edges_and_reverse():
    graph = make_graph()
    assert set(graph.vertices()) == {"A", "B", "C", "D"}
    assert set(graph.edges()) == {
        ("A", "B"), ("A", "C"), ("B", "C"), ("C", "A")
    }
    assert list(graph.reverse_vertices()) == list(reversed(list(graph.vertices())))
    assert list(graph.reverse_edges()) == list(reversed(list(graph.edges())))


def test_incident_adjacent_and_incoming_iterators():
    graph = make_graph()
    assert set(graph.incident_edges("A")) == {
        ("A", "B"), ("A", "C"), ("C", "A")
    }
    assert set(graph.adjacent_vertices("A")) == {"B", "C"}
    assert list(graph.incoming_edges("C")) == [("B", "C"), ("A", "C")]
    assert list(graph.reverse_incident_edges("A")) == list(
        reversed(list(graph.incident_edges("A")))
    )
    assert list(graph.reverse_adjacent_vertices("A")) == list(
        reversed(list(graph.adjacent_vertices("A")))
    )


def test_const_iterators():
    graph = make_graph()
    assert graph.const_vertices().read_only
    assert graph.const_edges().read_only
    assert graph.const_incident_edges("A").read_only
    assert graph.const_adjacent_vertices("A").read_only
    assert graph.reverse_const_vertices().read_only
    assert graph.reverse_const_edges().read_only
    assert graph.reverse_const_incident_edges("A").read_only
    assert graph.reverse_const_adjacent_vertices("A").read_only


def test_remove_edge_updates_both_chains():
    graph = make_graph()
    graph.remove_edge("A", "B")
    assert not graph.has_edge("A", "B")
    assert graph.edge_count == 3
    assert graph.out_degree("A") == 1
    assert graph.in_degree("B") == 0


def test_remove_vertex_removes_incident_edges():
    graph = make_graph()
    graph.remove_vertex("A")
    assert not graph.has_vertex("A")
    assert graph.edge_count == 1
    assert set(graph.edges()) == {("B", "C")}


def test_remove_by_iterators():
    graph = make_graph()
    iterator = graph.vertices()
    next(iterator)
    assert graph.remove_vertex_at(iterator) == "A"
    edge_iterator = graph.edges()
    edge = next(edge_iterator)
    assert graph.remove_edge_at(edge_iterator) == edge
    assert graph.edge_count == 0


def test_invalid_iterator_removal():
    graph = make_graph()
    other = make_graph()
    iterator = other.vertices()
    next(iterator)
    with pytest.raises(ValueError):
        graph.remove_vertex_at(iterator)
    with pytest.raises(RuntimeError):
        graph.remove_vertex_at(graph.vertices())


def test_iterator_type_validation():
    graph = make_graph()
    with pytest.raises(TypeError):
        graph.remove_edge_at(iter([("A", "B")]))
    iterator = graph.edges()
    next(iterator)
    with pytest.raises(ValueError):
        graph.remove_vertex_at(iterator)


def test_copy_assign_and_comparison():
    graph = make_graph()
    copied = graph.copy()
    assert copied == graph
    assert not copied != graph
    copied.add_vertex("E")
    assert copied > graph
    assert graph < copied
    assert graph <= copied
    assert copied >= graph
    assigned = DirectedGraph()
    assigned.assign_from(graph)
    assert assigned == graph
    assigned.add_vertex("E")
    assert assigned != graph


def test_assign_validation_and_clear():
    graph = make_graph()
    with pytest.raises(TypeError):
        graph.assign_from([])
    graph.clear()
    assert graph.is_empty()
    assert graph.edge_count == 0


def test_string_and_python_iteration():
    graph = make_graph()
    text = str(graph)
    assert "Вершины:" in text
    assert "Рёбра:" in text
    assert set(iter(graph)) == {"A", "B", "C", "D"}


def test_self_loop_and_vertex_removal():
    graph = DirectedGraph(["X"])
    graph.add_edge("X", "X")
    assert graph.degree("X") == 2
    assert graph.edge_degree("X", "X") == 2
    graph.remove_vertex("X")
    assert graph.edge_count == 0


def test_edge_degree_requires_existing_edge():
    graph = DirectedGraph(["A", "B"])
    with pytest.raises(KeyError):
        graph.edge_degree("A", "B")


def test_iterator_current_before_next():
    graph = DirectedGraph(["A"])
    iterator = graph.vertices()
    with pytest.raises(RuntimeError):
        _ = iterator.current


def test_iterator_current_supports_none_vertex():
    graph = DirectedGraph([None])
    iterator = graph.vertices()
    assert next(iterator) is None
    assert iterator.current is None


def test_remove_vertex_at_supports_none_vertex():
    graph = DirectedGraph([None])
    iterator = graph.vertices()
    next(iterator)
    assert graph.remove_vertex_at(iterator) is None
    assert graph.is_empty()

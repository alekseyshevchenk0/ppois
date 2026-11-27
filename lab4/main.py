from random import Random

from graph import DirectedGraph
from sorting import bozo_sort, merge_sort


BOZO_MAX_ATTEMPTS = 100_000
ITERATOR_METHODS = {
    ("1", False, False): "vertices",
    ("1", True, False): "reverse_vertices",
    ("1", False, True): "const_vertices",
    ("1", True, True): "reverse_const_vertices",
    ("2", False, False): "edges",
    ("2", True, False): "reverse_edges",
    ("2", False, True): "const_edges",
    ("2", True, True): "reverse_const_edges",
    ("3", False, False): "incident_edges",
    ("3", True, False): "reverse_incident_edges",
    ("3", False, True): "const_incident_edges",
    ("3", True, True): "reverse_const_incident_edges",
    ("4", False, False): "adjacent_vertices",
    ("4", True, False): "reverse_adjacent_vertices",
    ("4", False, True): "const_adjacent_vertices",
    ("4", True, True): "reverse_const_adjacent_vertices",
}


def _read_numbers():
    raw_numbers = input(
        "Числа через пробел или запятую: "
    ).replace(",", " ")
    parts = raw_numbers.split()
    if not parts:
        raise ValueError(
            "Пустой ввод недопустим."
        )
    try:
        return [int(part) for part in parts]
    except ValueError as error:
        raise ValueError(
            "Нужно вводить только целые числа."
        ) from error


def _sorting_menu():
    while True:
        print("\nСОРТИРОВКИ")
        print("1. Merge sort")
        print("2. Bozo sort")
        print("0. Назад")
        choice = input("Выберите сортировку: ").strip()

        if choice == "0":
            return
        if choice not in ("1", "2"):
            print("Неизвестный пункт меню.")
            continue

        try:
            numbers = _read_numbers()
        except ValueError as error:
            print("Ошибка:", error)
            continue

        order = input(
            "Порядок (1 — вверх, 2 — вниз): "
        ).strip()
        if order not in ("1", "2"):
            print("Неизвестный порядок.")
            continue

        reverse = order == "2"
        print("Исходные данные:", numbers)
        try:
            if choice == "1":
                result = merge_sort(numbers.copy(), reverse=reverse)
                algorithm = "Merge sort"
            else:
                result = bozo_sort(
                    numbers.copy(),
                    reverse=reverse,
                    max_attempts=BOZO_MAX_ATTEMPTS,
                    rng=Random(),
                )
                algorithm = "Bozo sort"
            print(f"Результат ({algorithm}):", result)
        except ValueError as error:
            print("Ошибка сортировки:", error)


def _read_yes_no(prompt):
    answer = input(prompt).strip().lower()
    if answer not in ("д", "н", "y", "n"):
        raise ValueError("Введите 'д' или 'н'.")
    return answer in ("д", "y")


def _iterator_menu(graph):
    while True:
        print("\nИТЕРАТОРЫ ГРАФА")
        print("1. Итератор вершин")
        print("2. Итератор рёбер")
        print("3. Итератор инцидентных рёбер")
        print("4. Итератор смежных вершин")
        print("0. Назад")
        kind = input("Выберите тип итератора: ").strip()
        if kind == "0":
            return
        if kind not in ("1", "2", "3", "4"):
            print("Неизвестный пункт меню.")
            continue

        try:
            reverse = _read_yes_no(
                "Обратный порядок? (д/н): "
            )
            read_only = _read_yes_no(
                "Константный вариант? (д/н): "
            )
            method_name = ITERATOR_METHODS[(kind, reverse, read_only)]
            if kind in ("3", "4"):
                value = input("Вершина: ").strip()
                iterator = getattr(graph, method_name)(value)
            else:
                iterator = getattr(graph, method_name)()
            print("Элементы:", list(iterator))
            print("Флаг read_only:", iterator.read_only)
        except (KeyError, ValueError, TypeError) as error:
            print("Ошибка:", error)


def _bidirectional_iterator_demo(graph):
    print("\nДВУНАПРАВЛЕННОЕ ПЕРЕМЕЩЕНИЕ")
    print("1. Итератор вершин")
    print("2. Итератор рёбер")
    print("0. Назад")
    choice = input("Выберите тип итератора: ").strip()

    if choice == "0":
        return
    if choice == "1":
        iterator = graph.vertices()
    elif choice == "2":
        iterator = graph.edges()
    else:
        print("Неизвестный пункт меню.")
        return

    print("Команды: n — следующий, p — предыдущий, 0 — выход")
    while True:
        command = input("Перемещение: ").strip().lower()
        if command == "0":
            return
        if command not in ("n", "p"):
            print("Неизвестная команда.")
            continue

        try:
            value = (
                iterator.move_next()
                if command == "n"
                else iterator.move_prev()
            )
            direction = "Следующий" if command == "n" else "Предыдущий"
            print(f"{direction} элемент:", value)
        except StopIteration:
            print("Достигнута граница последовательности.")


def _remove_by_iterator(graph, element_type):
    if element_type == "vertex":
        values = list(graph.vertices())
        remove_method = graph.remove_vertex_at
        iterator_factory = graph.vertices
        label = "вершину"
    else:
        values = list(graph.edges())
        remove_method = graph.remove_edge_at
        iterator_factory = graph.edges
        label = "ребро"

    if not values:
        print("Нет элементов для удаления.")
        return

    for index, value in enumerate(values):
        print(f"{index}: {value}")
    try:
        index = int(
            input(f"Введите номер элемента ({label}): ")
        )
    except ValueError as error:
        raise ValueError(
            "Номер должен быть целым."
        ) from error
    if index < 0 or index >= len(values):
        raise ValueError("Нет элемента с этим номером.")

    iterator = iterator_factory()
    for _ in range(index + 1):
        next(iterator)
    removed = remove_method(iterator)
    print("Удалено через итератор:", removed)


def _graph_copy_menu(graph):
    print("\nКОПИРОВАНИЕ И СРАВНЕНИЕ")
    copied = graph.copy()
    print("Копия графа создана:")
    print(copied)
    print("Исходный граф равен копии:", graph == copied)

    assigned = DirectedGraph()
    assigned.assign_from(graph)
    print("Граф после assign_from:")
    print(assigned)
    print(
        "Исходный граф равен присвоенному:",
        graph == assigned,
    )

    print("\nСравнение операторов:")
    print("==:", graph == copied)
    print("!=:", graph != copied)
    print("<:", graph < copied)
    print("<=:", graph <= copied)
    print(">:", graph > copied)
    print(">=:", graph >= copied)
    print("< и > сравнивают число вершин и рёбер.")

    marker = "__copy_check__"
    while copied.has_vertex(marker):
        marker += "_"
    copied.add_vertex(marker)
    print("Добавлена вершина в копию:", marker)
    print("Оригинал:", graph)
    print("Изменённая копия:", copied)
    print("Графы теперь равны:", graph == copied)


def _graph_menu():
    graph = DirectedGraph()
    while True:
        print("\nОРИЕНТИРОВАННЫЙ ГРАФ")
        print("1. Добавить вершину")
        print("2. Добавить ориентированное ребро")
        print("3. Показать граф")
        print("4. Проверить вершину и ребро")
        print("5. Показать степени вершины")
        print("6. Удалить вершину")
        print("7. Удалить ребро")
        print("8. Количество вершин и рёбер")
        print("9. Показать входящие рёбра вершины")
        print("10. Показать смежные вершины")
        print("11. Обратный порядок рёбер")
        print("12. Показать степень ребра")
        print("13. Пустота графа / очистка")
        print("14. Варианты итераторов")
        print("15. Удалить вершину через итератор")
        print("16. Удалить ребро через итератор")
        print("17. Копирование и сравнение графов")
        print("18. Двунаправленное перемещение итератора")
        print("0. Назад")
        choice = input("Выберите действие: ").strip()

        try:
            if choice == "1":
                value = input("Значение вершины: ").strip()
                graph.add_vertex(value)
                print("Вершина добавлена.")
            elif choice == "2":
                source = input("Начальная вершина: ").strip()
                target = input("Конечная вершина: ").strip()
                graph.add_edge(source, target)
                print("Ребро добавлено.")
            elif choice == "3":
                print(graph)
            elif choice == "4":
                source = input("Первая вершина: ").strip()
                target = input("Вторая вершина: ").strip()
                print(
                    "Первая вершина существует:",
                    graph.has_vertex(source),
                )
                print(
                    "Вторая вершина существует:",
                    graph.has_vertex(target),
                )
                if graph.has_vertex(source) and graph.has_vertex(target):
                    print(
                        "Ребро существует:",
                        graph.has_edge(source, target),
                    )
            elif choice == "5":
                value = input("Вершина: ").strip()
                print("Общая степень:", graph.degree(value))
                print("Полустепень захода:",
                      graph.in_degree(value))
                print("Полустепень исхода:",
                      graph.out_degree(value))
            elif choice == "6":
                graph.remove_vertex(input("Вершина: ").strip())
                print("Вершина удалена.")
            elif choice == "7":
                source = input("Начальная вершина: ").strip()
                target = input("Конечная вершина: ").strip()
                graph.remove_edge(source, target)
                print("Ребро удалено.")
            elif choice == "8":
                print("Количество вершин:", graph.vertex_count)
                print("Количество рёбер:", graph.edge_count)
            elif choice == "9":
                value = input("Вершина: ").strip()
                print(
                    "Входящие рёбра:",
                    list(graph.incoming_edges(value)),
                )
            elif choice == "10":
                value = input("Вершина: ").strip()
                print(
                    "Смежные вершины:",
                    list(graph.adjacent_vertices(value)),
                )
            elif choice == "11":
                print(
                    "Рёбра в обратном порядке:",
                    list(graph.reverse_edges()),
                )
            elif choice == "12":
                source = input("Начало ребра: ").strip()
                target = input("Конец ребра: ").strip()
                print(
                    "Степень ребра:",
                    graph.edge_degree(source, target),
                )
            elif choice == "13":
                print("Граф пуст:", graph.is_empty())
                print("Метод empty():", graph.empty())
                if _read_yes_no("Очистить граф? (д/н): "):
                    graph.clear()
                    print("Граф очищен.")
            elif choice == "14":
                _iterator_menu(graph)
            elif choice == "15":
                _remove_by_iterator(graph, "vertex")
            elif choice == "16":
                _remove_by_iterator(graph, "edge")
            elif choice == "17":
                _graph_copy_menu(graph)
            elif choice == "18":
                _bidirectional_iterator_demo(graph)
            elif choice == "0":
                return
            else:
                print("Неизвестный пункт меню.")
        except (KeyError, ValueError, TypeError, RuntimeError) as error:
            print("Ошибка:", error)


def main():
    while True:
        print("\nГЛАВНОЕ МЕНЮ")
        print("1. Сортировки")
        print("2. Ориентированный граф")
        print("0. Выход")
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            _sorting_menu()
        elif choice == "2":
            _graph_menu()
        elif choice == "0":
            print("Завершение программы.")
            return
        else:
            print("Неизвестный пункт меню.")


if __name__ == "__main__":
    main()

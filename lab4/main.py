from random import Random

from graph import DirectedGraph
from models import Student
from sorting import bozo_sort, merge_sort


def _show_sorting():
    numbers = [8, 3, 5, 1, 9]
    words = ["граф", "алгоритм", "контейнер", "сортировка"]
    students = [
        Student("Анна", 4.5),
        Student("Иван", 3.7),
        Student("Олег", 4.9),
    ]
    print("Исходные числа:", numbers)
    print("Merge sort:", merge_sort(numbers.copy()))
    print("Исходные строки:", words)
    print("Bozo sort:", bozo_sort(
        words.copy(), max_attempts=100_000, rng=Random(7)
    ))
    print("Студенты до сортировки:", ", ".join(map(str, students)))
    print(
        "Студенты после сортировки:",
        ", ".join(map(str, merge_sort(students.copy()))),
    )


def _show_graph():
    graph = DirectedGraph(["A", "B", "C", "D"])
    graph.add_edge("A", "B")
    graph.add_edge("A", "C")
    graph.add_edge("B", "C")
    graph.add_edge("C", "D")
    print(graph)
    print("Количество вершин:", graph.vertex_count)
    print("Количество рёбер:", graph.edge_count)
    print("Степень вершины C:", graph.degree("C"))
    print("Исходящие соседи A:", list(graph.adjacent_vertices("A")))
    print("Входящие рёбра C:", list(graph.incoming_edges("C")))
    print("Рёбра в обратном порядке:", list(graph.reverse_edges()))


def _graph_menu():
    graph = DirectedGraph()
    while True:
        print("\nГРАФ")
        print("1. Добавить вершину")
        print("2. Добавить ориентированное ребро")
        print("3. Показать граф")
        print("4. Проверить вершину и ребро")
        print("5. Показать степени вершины")
        print("6. Удалить вершину")
        print("7. Удалить ребро")
        print("0. Назад")
        choice = input("Выберите действие: ").strip()
        try:
            if choice == "1":
                graph.add_vertex(input("Значение вершины: ").strip())
            elif choice == "2":
                source = input("Начальная вершина: ").strip()
                target = input("Конечная вершина: ").strip()
                graph.add_edge(source, target)
            elif choice == "3":
                print(graph)
            elif choice == "4":
                source = input("Первая вершина: ").strip()
                target = input("Вторая вершина: ").strip()
                print("Вершина существует:", graph.has_vertex(source))
                if graph.has_vertex(source) and graph.has_vertex(target):
                    print("Ребро существует:", graph.has_edge(source, target))
            elif choice == "5":
                value = input("Вершина: ").strip()
                print("Общая степень:", graph.degree(value))
                print("Полустепень захода:", graph.in_degree(value))
                print("Полустепень исхода:", graph.out_degree(value))
            elif choice == "6":
                graph.remove_vertex(input("Вершина: ").strip())
            elif choice == "7":
                source = input("Начальная вершина: ").strip()
                target = input("Конечная вершина: ").strip()
                graph.remove_edge(source, target)
            elif choice == "0":
                return
            else:
                print("Неизвестный пункт меню.")
        except (KeyError, ValueError, TypeError) as error:
            print("Ошибка:", error)


def main():
    while True:
        print("1. Демонстрация сортировок")
        print("2. Демонстрация графа")
        print("3. Интерактивное управление графом")
        print("0. Выход")
        choice = input("Выберите действие: ").strip()
        if choice == "1":
            _show_sorting()
        elif choice == "2":
            _show_graph()
        elif choice == "3":
            _graph_menu()
        elif choice == "0":
            print("Завершение программы.")
            return
        else:
            print("Неизвестный пункт меню.")


if __name__ == "__main__":
    main()

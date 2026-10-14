#pragma once

#include <vector>
#include <iostream>

/**
 * @file tictactoe.hpp
 * @brief Содержит определение класса TicTacToe для игры в крестики-нолики произвольного размера.
 */

/**
 * @class TicTacToe
 * @brief Класс, реализующий игровую логику, состояние и правила крестиков-ноликов.
 */
class TicTacToe {
private:
    int size;                                   ///< Размер игрового поля (size x size)
    std::vector<std::vector<char>> board;       ///< Двумерный массив для хранения состояния ячеек поля
    char currentPlayer;                         ///< Символ текущего игрока ('X' или 'O')

public:
    /**
     * @brief Конструктор по умолчанию.
     * @details Создает стандартное игровое поле размером 3x3, начинает игру с игрока 'X'.
     */
    TicTacToe();

    /**
     * @brief Конструктор с параметром размера поля.
     * @param boardSize Размер игрового поля (должен быть больше 0).
     * @throws std::invalid_argument если boardSize <= 0.
     */
    explicit TicTacToe(int boardSize);

    /**
     * @brief Конструктор копирования.
     * @param other Ссылка на другой объект игры TicTacToe для копирования.
     */
    TicTacToe(const TicTacToe& other);

    /**
     * @brief Оператор присваивания копированием.
     * @param other Ссылка на другой объект игры TicTacToe.
     * @return Ссылка на текущий измененный объект.
     */
    TicTacToe& operator=(const TicTacToe& other);

    /**
     * @brief Деструктор по умолчанию.
     */
    ~TicTacToe() = default;

    /**
     * @brief Проверяет, является ли ход в указанную ячейку допустимым.
     * @param row Индекс строки (начиная с 0).
     * @param col Индекс столбца (начиная с 0).
     * @return true, если координаты в пределах поля и ячейка пуста, иначе false.
     */
    bool isValidMove(int row, int col) const;

    /**
     * @brief Устанавливает ход игрока в заданную позицию.
     * @param row Индекс строки.
     * @param col Индекс столбца.
     * @param mark Символ игрока ('X' или 'O').
     * @throws std::out_of_range если ход невалидный (ячейка занята или вне границ).
     */
    void setMove(int row, int col, char mark);

    /**
     * @brief Получает символ в конкретной ячейке поля.
     * @param row Индекс строки.
     * @param col Индекс столбца.
     * @return Символ в ячейке ('X', 'O' или ' ').
     * @throws std::out_of_range если координаты выходят за пределы поля.
     */
    char getCell(int row, int col) const;

    /**
     * @brief Проверяет наличие победителя на игровом поле.
     * @return Символ победителя ('X' или 'O'), либо пробел (' '), если победителя пока нет.
     */
    char checkWinner() const;

    /**
     * @brief Проверяет, заполнено ли игровое поле полностью.
     * @return true, если свободных ячеек не осталось (ничья), иначе false.
     */
    bool isBoardFull() const;

    /**
     * @brief Возвращает текущий размер игрового поля.
     * @return Размер поля (int).
     */
    int getSize() const;

    /**
     * @brief Оператор проверки на равенство игр.
     * @param other Объект для сравнения.
     * @return true, если размер, текущий игрок и состояние поля равны, иначе false.
     */
    bool operator==(const TicTacToe& other) const;

    /**
     * @brief Оператор проверки на неравенство игр.
     * @param other Объект для сравнения.
     * @return true, если игры отличаются, иначе false.
     */
    bool operator!=(const TicTacToe& other) const;

    /**
     * @brief Перегрузка оператора вывода игры в поток.
     * @param os Поток вывода.
     * @param game Объект игры TicTacToe.
     * @return Ссылка на поток вывода.
     */
    friend std::ostream& operator<<(std::ostream& os, const TicTacToe& game);

    /**
     * @brief Перегрузка оператора ввода игры из потока.
     * @param is Поток ввода.
     * @param game Объект игры TicTacToe для заполнения.
     * @return Ссылка на поток ввода.
     */
    friend std::istream& operator>>(std::istream& is, TicTacToe& game);
};
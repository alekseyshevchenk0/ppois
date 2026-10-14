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
    static constexpr char EMPTY = ' ';          ///< Символ пустой ячейки в памяти
    static constexpr char FILE_EMPTY = '.';     ///< Символ пустой ячейки в потоке/файле (пробел пропускается при чтении)

    int size;                                   ///< Размер игрового поля (size x size)
    std::vector<std::vector<char>> board;       ///< Двумерный массив для хранения состояния ячеек поля
    char currentPlayer;                         ///< Символ текущего игрока ('X' или 'O')

    /**
     * @brief Проверяет, лежат ли координаты в пределах поля.
     * @param row Индекс строки.
     * @param col Индекс столбца.
     * @return true, если 0 <= row, col < size, иначе false.
     */
    bool inBounds(int row, int col) const;

public:
    /**
     * @brief Конструктор с параметром размера поля.
     * @details Без аргумента создает стандартное поле 3x3. Игру начинает игрок 'X'.
     * Конструктор копирования, оператор присваивания и деструктор генерируются компилятором.
     * @param boardSize Размер игрового поля (должен быть больше 0), по умолчанию 3.
     * @throws std::invalid_argument если boardSize <= 0.
     */
    explicit TicTacToe(int boardSize = 3);

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
     * @throws std::invalid_argument если mark не 'X' и не 'O', либо ячейка уже занята.
     * @throws std::out_of_range если координаты выходят за пределы поля.
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
     * @brief Возвращает символ игрока, чей ход сейчас.
     * @return 'X' или 'O'.
     */
    char getCurrentPlayer() const;

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
    bool operator!=(const TicTacToe& other) const { return !(*this == other); }

    /**
     * @brief Перегрузка оператора вывода игры в поток.
     * @details Формат: "<size> <currentPlayer>", затем size строк по size символов через пробел.
     * Пустая ячейка выводится как '.'.
     * @param os Поток вывода.
     * @param game Объект игры TicTacToe.
     * @return Ссылка на поток вывода.
     */
    friend std::ostream& operator<<(std::ostream& os, const TicTacToe& game);

    /**
     * @brief Перегрузка оператора ввода игры из потока.
     * @details Ожидает формат, который выводит operator<<. При некорректных данных
     * (размер вне 1..100, неизвестный игрок или символ ячейки, обрыв потока) выставляет
     * failbit и не изменяет game.
     * @param is Поток ввода.
     * @param game Объект игры TicTacToe для заполнения.
     * @return Ссылка на поток ввода.
     */
    friend std::istream& operator>>(std::istream& is, TicTacToe& game);
};
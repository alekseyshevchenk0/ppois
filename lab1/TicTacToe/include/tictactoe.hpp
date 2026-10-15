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
public:
    static constexpr char PLAYER_X = 'X';   ///< Символ первого игрока (ходит первым)
    static constexpr char PLAYER_O = 'O';   ///< Символ второго игрока
    static constexpr char EMPTY_CELL = ' '; ///< Символ пустой ячейки
    static constexpr int DEFAULT_SIZE = 3;  ///< Размер поля по умолчанию

    /**
     * @brief Конструктор с параметром размера поля.
     * @details Без аргумента создает стандартное поле DEFAULT_SIZE x DEFAULT_SIZE.
     * Игру начинает игрок PLAYER_X.
     * @param boardSize Размер игрового поля (должен быть больше 0).
     * @throws std::invalid_argument если boardSize <= 0.
     */
    explicit TicTacToe(int boardSize = DEFAULT_SIZE);

    /**
     * @brief Конструктор копирования (поэлементное копирование состояния игры).
     * @param other Игра, которую нужно скопировать.
     */
    TicTacToe(const TicTacToe& other) = default;

    /**
     * @brief Оператор присваивания копированием.
     * @param other Игра, состояние которой копируется.
     * @return Ссылка на текущий объект.
     */
    TicTacToe& operator=(const TicTacToe& other) = default;

    /**
     * @brief Деструктор. Ресурсы освобождаются автоматически (память держит std::vector).
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
     * @brief Устанавливает ход игрока в заданную позицию и передает очередь другому игроку.
     * @param row Индекс строки.
     * @param col Индекс столбца.
     * @param mark Символ игрока (PLAYER_X или PLAYER_O).
     * @throws std::invalid_argument если mark неизвестен либо ячейка уже занята.
     * @throws std::out_of_range если координаты выходят за пределы поля.
     */
    void setMove(int row, int col, char mark);

    /**
     * @brief Получает символ в конкретной ячейке поля.
     * @param row Индекс строки.
     * @param col Индекс столбца.
     * @return Символ в ячейке (PLAYER_X, PLAYER_O или EMPTY_CELL).
     * @throws std::out_of_range если координаты выходят за пределы поля.
     */
    char getCell(int row, int col) const;

    /**
     * @brief Проверяет наличие победителя на игровом поле.
     * @return Символ победителя, либо EMPTY_CELL, если победителя пока нет.
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
     * @return PLAYER_X или PLAYER_O.
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
    bool operator!=(const TicTacToe& other) const;

    /**
     * @brief Перегрузка оператора вывода игры в поток.
     * @details Формат: "<size> <currentPlayer>", затем size строк по size символов через пробел.
     * Пустая ячейка выводится как '.'.
     * @param output Поток вывода.
     * @param game Объект игры TicTacToe.
     * @return Ссылка на поток вывода.
     */
    friend std::ostream& operator<<(std::ostream& output, const TicTacToe& game);

    /**
     * @brief Перегрузка оператора ввода игры из потока.
     * @details Ожидает формат, который выводит operator<<. При некорректных данных
     * (размер вне 1..100, неизвестный игрок или символ ячейки, обрыв потока) выставляет
     * failbit и не изменяет game.
     * @param input Поток ввода.
     * @param game Объект игры TicTacToe для заполнения.
     * @return Ссылка на поток ввода.
     */
    friend std::istream& operator>>(std::istream& input, TicTacToe& game);

private:
    int size_;                                  ///< Размер игрового поля (size_ x size_)
    std::vector<std::vector<char>> board_;      ///< Двумерный массив для хранения состояния ячеек поля
    char currentPlayer_;                        ///< Символ текущего игрока

    /**
     * @brief Проверяет, лежат ли координаты в пределах поля.
     * @param row Индекс строки.
     * @param col Индекс столбца.
     * @return true, если 0 <= row, col < size_, иначе false.
     */
    bool inBounds(int row, int col) const;

    /**
     * @brief Проверяет, заполнена ли линия одним и тем же символом.
     * @param startRow Строка первой ячейки линии.
     * @param startCol Столбец первой ячейки линии.
     * @param rowStep Сдвиг по строке от ячейки к ячейке (-1, 0 или 1).
     * @param colStep Сдвиг по столбцу от ячейки к ячейке (-1, 0 или 1).
     * @return Символ, которым заполнена вся линия, либо EMPTY_CELL.
     */
    char lineWinner(int startRow, int startCol, int rowStep, int colStep) const;
};

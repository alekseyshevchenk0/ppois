#include <iostream>
#include <limits>
#include "tictactoe.hpp"

namespace {

void clearInput() {
    std::cin.clear();
    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
}

}

void printBoard(const TicTacToe& game) {
    int size = game.getSize();
    std::cout << "\n    ";
    for (int j = 0; j < size; ++j) {
        std::cout << j + 1 << "   ";
    }
    std::cout << "\n";
    for (int i = 0; i < size; ++i) {
        std::cout << "   ";
        for (int j = 0; j < size; ++j) {
            std::cout << "----";
        }
        std::cout << "-\n";
        std::cout << " " << i + 1 << " ";
        for (int j = 0; j < size; ++j) {
            std::cout << "| " << game.getCell(i, j) << " ";
        }
        std::cout << "|\n";
    }
    std::cout << "   ";
    for (int j = 0; j < size; ++j) {
        std::cout << "----";
    }
    std::cout << "-\n\n";
}

void playTicTacToe() {
    int size = 3;
    std::cout << "Введите размер поля (например, 3 для 3x3): ";
    if (!(std::cin >> size) || size <= 0) {
        if (std::cin.eof()) return;
        std::cout << "Некорректный размер, устанавливается значение по умолчанию: 3.\n";
        clearInput();
        size = 3;
    }

    TicTacToe game(size);
    std::cout << "\nИгра началась. Первым ходит крестик (X).\n";

    while (true) {
        printBoard(game);

        char winner = game.checkWinner();
        if (winner != ' ') {
            std::cout << "Поздравляем. Победил игрок: " << winner << "!\n";
            break;
        }

        if (game.isBoardFull()) {
            std::cout << "Ничья. Свободные клетки закончились\n";
            break;
        }

        char mark = game.getCurrentPlayer();
        int row, col;
        std::cout << "Ходит '" << mark << "'. Введите строку и столбец (через пробел, от 1 до "
                  << size << "): ";

        if (!(std::cin >> row >> col)) {
            if (std::cin.eof()) return;
            std::cout << "Ошибка ввода. Пожалуйста, вводите числа\n";
            clearInput();
            continue;
        }
        --row;
        --col;

        if (game.isValidMove(row, col)) {
            game.setMove(row, col, mark);
        } else {
            std::cout << "Неверный ход. Клетка уже занята или выходит за пределы поля. Попробуйте снова\n";
        }
    }
}

int main() {
    int choice = 0;
    do {
        std::cout << "МЕНЮ КРЕСТИКИ-НОЛИКИ\n";
        std::cout << "1. Начать новую игру\n";
        std::cout << "2. Выход\n";
        std::cout << "Выберите пункт меню: ";

        if (!(std::cin >> choice)) {
            if (std::cin.eof()) break;
            std::cout << "Некорректный ввод\n";
            clearInput();
            continue;
        }

        switch (choice) {
            case 1:
                playTicTacToe();
                break;
            case 2:
                std::cout << "Выход из программы\n";
                break;
            default:
                std::cout << "Неверный пункт меню, попробуйте снова\n";
        }

        if (std::cin.eof()) break;
        std::cout << "\n";
    } while (choice != 2);

    return 0;
}
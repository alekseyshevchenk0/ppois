#include <iostream>
#include <limits>
#include <string>
#include "../include/tictactoe.hpp"

namespace {

constexpr int MENU_NEW_GAME = 1;
constexpr int MENU_EXIT = 2;
constexpr int USER_INDEX_OFFSET = 1;      // пользователь считает строки и столбцы с 1, класс — с 0
constexpr const char* CELL_BORDER = "----";

int toUserNumber(int boardIndex) {
    return boardIndex + USER_INDEX_OFFSET;
}

int toBoardIndex(int userNumber) {
    return userNumber - USER_INDEX_OFFSET;
}

// Сбрасывает ошибочное состояние cin и выбрасывает остаток строки.
void clearInput() {
    std::cin.clear();
    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
}

// Сообщает об ошибке ввода. При закрытом вводе (EOF) молчит: вызывающий код завершит работу.
void reportInputFailure(const std::string& message) {
    if (std::cin.eof()) return;
    std::cout << message << "\n";
    clearInput();
}

void printColumnNumbers(int size) {
    std::cout << "\n    ";
    for (int col = 0; col < size; ++col) {
        std::cout << toUserNumber(col) << "   ";
    }
    std::cout << "\n";
}

void printSeparator(int size) {
    std::cout << "   ";
    for (int col = 0; col < size; ++col) {
        std::cout << CELL_BORDER;
    }
    std::cout << "-\n";
}

void printRow(const TicTacToe& game, int row) {
    std::cout << " " << toUserNumber(row) << " ";
    for (int col = 0; col < game.getSize(); ++col) {
        std::cout << "| " << game.getCell(row, col) << " ";
    }
    std::cout << "|\n";
}

void printBoard(const TicTacToe& game) {
    printColumnNumbers(game.getSize());
    for (int row = 0; row < game.getSize(); ++row) {
        printSeparator(game.getSize());
        printRow(game, row);
    }
    printSeparator(game.getSize());
    std::cout << "\n";
}

// Читает размер поля. Возвращает false, если ввод закончился (EOF).
// При некорректном размере подставляет размер по умолчанию.
bool readBoardSize(int& size) {
    std::cout << "Введите размер поля (например, 3 для 3x3): ";
    if (std::cin >> size && size > 0) return true;
    if (std::cin.eof()) return false;
    std::cout << "Некорректный размер, устанавливается значение по умолчанию: " << TicTacToe::DEFAULT_SIZE << ".\n";
    clearInput();
    size = TicTacToe::DEFAULT_SIZE;
    return true;
}

// Возвращает true, если партия закончилась (победа или ничья), и сообщает результат.
bool announceIfFinished(const TicTacToe& game) {
    const char winner = game.checkWinner();
    if (winner != TicTacToe::EMPTY_CELL) {
        std::cout << "Поздравляем. Победил игрок: " << winner << "!\n";
        return true;
    }
    if (game.isBoardFull()) {
        std::cout << "Ничья. Свободные клетки закончились\n";
        return true;
    }
    return false;
}

void applyMove(TicTacToe& game, int row, int col) {
    if (!game.isValidMove(row, col)) {
        std::cout << "Неверный ход. Клетка уже занята или выходит за пределы поля. Попробуйте снова\n";
        return;
    }
    game.setMove(row, col, game.getCurrentPlayer());
}

// Один ход текущего игрока. Возвращает false, если ввод закончился (EOF).
bool playTurn(TicTacToe& game) {
    int userRow = 0;
    int userCol = 0;
    std::cout << "Ходит '" << game.getCurrentPlayer() << "'. Введите строку и столбец (через пробел, от "
              << toUserNumber(0) << " до " << game.getSize() << "): ";
    if (!(std::cin >> userRow >> userCol)) {
        reportInputFailure("Ошибка ввода. Пожалуйста, вводите числа");
        return !std::cin.eof();
    }
    applyMove(game, toBoardIndex(userRow), toBoardIndex(userCol));
    return true;
}

void playTicTacToe() {
    int size = 0;
    if (!readBoardSize(size)) return;

    TicTacToe game(size);
    std::cout << "\nИгра началась. Первым ходит крестик (" << TicTacToe::PLAYER_X << ").\n";
    while (true) {
        printBoard(game);
        if (announceIfFinished(game)) return;
        if (!playTurn(game)) return;
    }
}

void printMenu() {
    std::cout << "МЕНЮ КРЕСТИКИ-НОЛИКИ\n"
              << MENU_NEW_GAME << ". Начать новую игру\n"
              << MENU_EXIT << ". Выход\n"
              << "Выберите пункт меню: ";
}

// Выполняет пункт меню. Возвращает false, если пользователь выбрал выход.
bool executeChoice(int choice) {
    switch (choice) {
        case MENU_NEW_GAME:
            playTicTacToe();
            return true;
        case MENU_EXIT:
            std::cout << "Выход из программы\n";
            return false;
        default:
            std::cout << "Неверный пункт меню, попробуйте снова\n";
            return true;
    }
}

}  // namespace

int main() {
    bool running = true;
    while (running && !std::cin.eof()) {
        printMenu();
        int choice = 0;
        if (!(std::cin >> choice)) {
            reportInputFailure("Некорректный ввод");
            continue;
        }
        running = executeChoice(choice);
        std::cout << "\n";
    }
    return 0;
}
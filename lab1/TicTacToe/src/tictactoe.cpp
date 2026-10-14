#include "tictactoe.hpp"

#include <istream>
#include <ostream>
#include <stdexcept>

namespace {
constexpr int MAX_SIZE_FROM_STREAM = 100;
}

TicTacToe::TicTacToe(int boardSize) : size(boardSize), currentPlayer('X') {
    if (boardSize <= 0) {
        throw std::invalid_argument("Размер доски должен быть больше 0");
    }
    board.assign(size, std::vector<char>(size, EMPTY));
}

bool TicTacToe::inBounds(int row, int col) const {
    return row >= 0 && row < size && col >= 0 && col < size;
}

bool TicTacToe::isValidMove(int row, int col) const {
    return inBounds(row, col) && board[row][col] == EMPTY;
}

void TicTacToe::setMove(int row, int col, char mark) {
    if (mark != 'X' && mark != 'O') {
        throw std::invalid_argument("Знак должен быть 'X' или 'O'");
    }
    if (!inBounds(row, col)) {
        throw std::out_of_range("Координаты выходят за пределы доски");
    }
    if (board[row][col] != EMPTY) {
        throw std::invalid_argument("Клетка уже занята");
    }
    board[row][col] = mark;
    currentPlayer = (mark == 'X') ? 'O' : 'X';
}

char TicTacToe::getCell(int row, int col) const {
    if (!inBounds(row, col)) {
        throw std::out_of_range("Координаты выходят за пределы допустимого диапазона");
    }
    return board[row][col];
}

char TicTacToe::checkWinner() const {
    auto lineWinner = [this](int r0, int c0, int dr, int dc) -> char {
        char first = board[r0][c0];
        if (first == EMPTY) return EMPTY;
        for (int k = 1; k < size; ++k) {
            if (board[r0 + k * dr][c0 + k * dc] != first) return EMPTY;
        }
        return first;
    };

    for (int i = 0; i < size; ++i) {
        if (char w = lineWinner(i, 0, 0, 1); w != EMPTY) return w;
        if (char w = lineWinner(0, i, 1, 0); w != EMPTY) return w;
    }
    if (char w = lineWinner(0, 0, 1, 1); w != EMPTY) return w; 
    if (char w = lineWinner(0, size - 1, 1, -1); w != EMPTY) return w;

    return EMPTY;
}

bool TicTacToe::isBoardFull() const {
    for (const auto& row : board) {
        for (char c : row) {
            if (c == EMPTY) return false;
        }
    }
    return true;
}

int TicTacToe::getSize() const {
    return size;
}

char TicTacToe::getCurrentPlayer() const {
    return currentPlayer;
}

bool TicTacToe::operator==(const TicTacToe& other) const {
    return size == other.size && currentPlayer == other.currentPlayer && board == other.board;
}

std::ostream& operator<<(std::ostream& os, const TicTacToe& game) {
    os << game.size << ' ' << game.currentPlayer << '\n';
    for (int i = 0; i < game.size; ++i) {
        for (int j = 0; j < game.size; ++j) {
            char c = game.board[i][j];
            os << (c == TicTacToe::EMPTY ? TicTacToe::FILE_EMPTY : c);
            if (j + 1 < game.size) os << ' ';
        }
        os << '\n';
    }
    return os;
}

std::istream& operator>>(std::istream& is, TicTacToe& game) {
    int newSize;
    char newPlayer;
    if (!(is >> newSize >> newPlayer)) return is;

    if (newSize <= 0 || newSize > MAX_SIZE_FROM_STREAM ||
        (newPlayer != 'X' && newPlayer != 'O')) {
        is.setstate(std::ios::failbit);
        return is;
    }

    std::vector<std::vector<char>> newBoard(newSize, std::vector<char>(newSize, TicTacToe::EMPTY));
    for (int i = 0; i < newSize; ++i) {
        for (int j = 0; j < newSize; ++j) {
            char c;
            if (!(is >> c)) return is;
            if (c == TicTacToe::FILE_EMPTY) {
                newBoard[i][j] = TicTacToe::EMPTY;
            } else if (c == 'X' || c == 'O') {
                newBoard[i][j] = c;
            } else {
                is.setstate(std::ios::failbit);
                return is;
            }
        }
    }
    game.size = newSize;
    game.currentPlayer = newPlayer;
    game.board = std::move(newBoard);
    return is;
}
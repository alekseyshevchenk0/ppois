#include "../include/tictactoe.hpp"

#include <istream>
#include <ostream>
#include <stdexcept>
#include <utility>

namespace {

using Board = std::vector<std::vector<char>>;

constexpr char FILE_EMPTY_CELL = '.';
constexpr int MAX_SIZE_FROM_STREAM = 100;

bool isPlayerMark(char mark) {
    return mark == TicTacToe::PLAYER_X || mark == TicTacToe::PLAYER_O;
}

bool isValidHeader(int size, char player) {
    return size > 0 && size <= MAX_SIZE_FROM_STREAM && isPlayerMark(player);
}

bool parseCell(char symbol, char& cell) {
    if (symbol == FILE_EMPTY_CELL) {
        cell = TicTacToe::EMPTY_CELL;
        return true;
    }
    if (!isPlayerMark(symbol)) return false;
    cell = symbol;
    return true;
}

bool readBoard(std::istream& input, int size, Board& board) {
    board.assign(size, std::vector<char>(size, TicTacToe::EMPTY_CELL));
    for (auto& row : board) {
        for (char& cell : row) {
            char symbol;
            if (!(input >> symbol)) return false;
            if (parseCell(symbol, cell)) continue;
            input.setstate(std::ios::failbit);
            return false;
        }
    }
    return true;
}

}

TicTacToe::TicTacToe(int boardSize) : size_(boardSize), currentPlayer_(PLAYER_X) {
    if (boardSize <= 0) {
        throw std::invalid_argument("Размер доски должен быть больше 0");
    }
    board_.assign(size_, std::vector<char>(size_, EMPTY_CELL));
}

bool TicTacToe::inBounds(int row, int col) const {
    return row >= 0 && row < size_ && col >= 0 && col < size_;
}

bool TicTacToe::isValidMove(int row, int col) const {
    return inBounds(row, col) && board_[row][col] == EMPTY_CELL;
}

void TicTacToe::setMove(int row, int col, char mark) {
    if (!isPlayerMark(mark)) {
        throw std::invalid_argument("Знак должен быть 'X' или 'O'");
    }
    if (!inBounds(row, col)) {
        throw std::out_of_range("Координаты выходят за пределы доски");
    }
    if (board_[row][col] != EMPTY_CELL) {
        throw std::invalid_argument("Клетка уже занята");
    }
    board_[row][col] = mark;
    currentPlayer_ = (mark == PLAYER_X) ? PLAYER_O : PLAYER_X;
}

char TicTacToe::getCell(int row, int col) const {
    if (!inBounds(row, col)) {
        throw std::out_of_range("Координаты выходят за пределы допустимого диапазона");
    }
    return board_[row][col];
}

char TicTacToe::lineWinner(int startRow, int startCol, int rowStep, int colStep) const {
    const char firstCell = board_[startRow][startCol];
    if (firstCell == EMPTY_CELL) return EMPTY_CELL;
    for (int offset = 1; offset < size_; ++offset) {
        if (board_[startRow + offset * rowStep][startCol + offset * colStep] != firstCell) {
            return EMPTY_CELL;
        }
    }
    return firstCell;
}

char TicTacToe::checkWinner() const {
    for (int index = 0; index < size_; ++index) {
        const char rowWinner = lineWinner(index, 0, 0, 1);
        if (rowWinner != EMPTY_CELL) return rowWinner;
        const char columnWinner = lineWinner(0, index, 1, 0);
        if (columnWinner != EMPTY_CELL) return columnWinner;
    }
    const char mainDiagonalWinner = lineWinner(0, 0, 1, 1);
    if (mainDiagonalWinner != EMPTY_CELL) return mainDiagonalWinner;
    return lineWinner(0, size_ - 1, 1, -1);
}

bool TicTacToe::isBoardFull() const {
    for (const auto& row : board_) {
        for (char cell : row) {
            if (cell == EMPTY_CELL) return false;
        }
    }
    return true;
}

int TicTacToe::getSize() const {
    return size_;
}

char TicTacToe::getCurrentPlayer() const {
    return currentPlayer_;
}

bool TicTacToe::operator==(const TicTacToe& other) const {
    return size_ == other.size_ && currentPlayer_ == other.currentPlayer_ && board_ == other.board_;
}

bool TicTacToe::operator!=(const TicTacToe& other) const {
    return !(*this == other);
}

std::ostream& operator<<(std::ostream& output, const TicTacToe& game) {
    output << game.size_ << ' ' << game.currentPlayer_ << '\n';
    for (const auto& row : game.board_) {
        for (int col = 0; col < game.size_; ++col) {
            output << (row[col] == TicTacToe::EMPTY_CELL ? FILE_EMPTY_CELL : row[col]);
            if (col + 1 < game.size_) output << ' ';
        }
        output << '\n';
    }
    return output;
}

std::istream& operator>>(std::istream& input, TicTacToe& game) {
    int newSize;
    char newPlayer;
    if (!(input >> newSize >> newPlayer)) return input;

    if (!isValidHeader(newSize, newPlayer)) {
        input.setstate(std::ios::failbit);
        return input;
    }

    Board newBoard;
    if (!readBoard(input, newSize, newBoard)) return input;

    game.size_ = newSize;
    game.currentPlayer_ = newPlayer;
    game.board_ = std::move(newBoard);
    return input;
}

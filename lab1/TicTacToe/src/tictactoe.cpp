#include "tictactoe.hpp"
#include <stdexcept>

TicTacToe::TicTacToe() : size(3), currentPlayer('X') {
    board = std::vector<std::vector<char>>(size, std::vector<char>(size, ' '));
}

TicTacToe::TicTacToe(int boardSize) : size(boardSize), currentPlayer('X') {
    if (boardSize <= 0) {
        throw std::invalid_argument("Размер доски должен быть больше чем 0");
    }
    board = std::vector<std::vector<char>>(size, std::vector<char>(size, ' '));
}

TicTacToe::TicTacToe(const TicTacToe& other)
    : size(other.size), board(other.board), currentPlayer(other.currentPlayer) {}

TicTacToe& TicTacToe::operator=(const TicTacToe& other) {
    if (this != &other) {
        size = other.size;
        board = other.board;
        currentPlayer = other.currentPlayer;
    }
    return *this;
}

bool TicTacToe::isValidMove(int row, int col) const {
    if (row < 0 || row >= size || col < 0 || col >= size) {
        return false;
    }
    return board[row][col] == ' ';
}

void TicTacToe::setMove(int row, int col, char mark) {
    if (!isValidMove(row, col)) {
        throw std::out_of_range("Недопустимая позиция хода");
    }
    board[row][col] = mark;
    currentPlayer = (mark == 'X') ? 'O' : 'X';
}

char TicTacToe::getCell(int row, int col) const {
    if (row < 0 || row >= size || col < 0 || col >= size) {
        throw std::out_of_range("Координаты выходят за пределы допустимого диапазона");
    }
    return board[row][col];
}

char TicTacToe::checkWinner() const {
    for (int i = 0; i < size; ++i) {
        bool rowWin = true;
        bool colWin = true;
        for (int j = 1; j < size; ++j) {
            if (board[i][j] == ' ' || board[i][j] != board[i][0]) rowWin = false;
            if (board[j][i] == ' ' || board[j][i] != board[0][i]) colWin = false;
        }
        if (rowWin) return board[i][0];
        if (colWin) return board[0][i];
    }
    bool mainDiagWin = true;
    for (int i = 1; i < size; ++i) {
        if (board[i][i] == ' ' || board[i][i] != board[0][0]) {
            mainDiagWin = false;
            break;
        }
    }
    if (mainDiagWin) return board[0][0];
    bool antiDiagWin = true;
    for (int i = 1; i < size; ++i) {
        if (board[i][size - 1 - i] == ' ' || board[i][size - 1 - i] != board[0][size - 1]) {
            antiDiagWin = false;
            break;
        }
    }
    if (antiDiagWin) return board[0][size - 1];

    return ' ';
}

bool TicTacToe::isBoardFull() const {
    for (int i = 0; i < size; ++i) {
        for (int j = 0; j < size; ++j) {
            if (board[i][j] == ' ') return false;
        }
    }
    return true;
}

int TicTacToe::getSize() const {
    return size;
}

bool TicTacToe::operator==(const TicTacToe& other) const {
    return size == other.size && 
           currentPlayer == other.currentPlayer && 
           board == other.board;
}

bool TicTacToe::operator!=(const TicTacToe& other) const {
    return !(*this == other);
}

std::ostream& operator<<(std::ostream& os, const TicTacToe& game) {
    os << game.size << " " << game.currentPlayer << "\n";
    for (int i = 0; i < game.size; ++i) {
        for (int j = 0; j < game.size; ++j) {
            os << game.board[i][j] << (j == game.size - 1 ? "" : " ");
        }
        os << "\n";
    }
    return os;
}

std::istream& operator>>(std::istream& is, TicTacToe& game) {
    int newSize;
    char newPlayer;
    if (!(is >> newSize >> newPlayer)) return is;

    std::vector<std::vector<char>> newBoard(newSize, std::vector<char>(newSize));
    for (int i = 0; i < newSize; ++i) {
        for (int j = 0; j < newSize; ++j) {
            is >> newBoard[i][j];
        }
    }

    game.size = newSize;
    game.currentPlayer = newPlayer;
    game.board = newBoard;
    return is;
}
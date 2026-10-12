#ifndef TIC_TAC_TOE_H
#define TIC_TAC_TOE_H

#include <vector>
#include <iostream>

class TicTacToe {
private:
    int size;                      
    std::vector<std::vector<char>> board;
    char currentPlayer;       

public:
    TicTacToe();

    explicit TicTacToe(int boardSize);

    TicTacToe(const TicTacToe& other);

    TicTacToe& operator=(const TicTacToe& other);

    ~TicTacToe() = default;

    bool isValidMove(int row, int col) const;

    void setMove(int row, int col, char mark);

    char getCell(int row, int col) const;

    char checkWinner() const;

    bool isBoardFull() const;

    int getSize() const;

    bool operator==(const TicTacToe& other) const;

    bool operator!=(const TicTacToe& other) const;

    friend std::ostream& operator<<(std::ostream& os, const TicTacToe& game);

    friend std::istream& operator>>(std::istream& is, TicTacToe& game);
};

#endif
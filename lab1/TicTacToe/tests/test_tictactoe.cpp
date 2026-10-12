#include <gtest/gtest.h>
#include "../include/tictactoe.hpp"

TEST(TicTacToeTest, Initialization) {
    TicTacToe game(3);
    EXPECT_EQ(game.getSize(), 3);
    EXPECT_EQ(game.checkWinner(), ' ');
    EXPECT_FALSE(game.isBoardFull());

    for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) {
            EXPECT_EQ(game.getCell(i, j), ' ');
        }
    }
}

TEST(TicTacToeTest, ValidMoves) {
    TicTacToe game(3);
    EXPECT_TRUE(game.isValidMove(0, 0));
    
    game.setMove(0, 0, 'X');
    EXPECT_EQ(game.getCell(0, 0), 'X');
    EXPECT_FALSE(game.isValidMove(0, 0));
    EXPECT_FALSE(game.isValidMove(-1, 0));
    EXPECT_FALSE(game.isValidMove(3, 3));
}

TEST(TicTacToeTest, RowWinner) {
    TicTacToe game(3);
    game.setMove(0, 0, 'X');
    game.setMove(0, 1, 'X');
    game.setMove(0, 2, 'X');
    EXPECT_EQ(game.checkWinner(), 'X');
}

TEST(TicTacToeTest, DiagonalWinner) {
    TicTacToe game(3);
    game.setMove(0, 0, 'O');
    game.setMove(1, 1, 'O');
    game.setMove(2, 2, 'O');
    EXPECT_EQ(game.checkWinner(), 'O');
}

TEST(TicTacToeTest, BoardFullDraw) {
    TicTacToe game(3);
    char moves[3][3] = {
        {'X', 'O', 'X'},
        {'X', 'O', 'X'},
        {'O', 'X', 'O'}
    };
    
    for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) {
            game.setMove(i, j, moves[i][j]);
        }
    }
    
    EXPECT_TRUE(game.isBoardFull());
    EXPECT_EQ(game.checkWinner(), ' ');
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
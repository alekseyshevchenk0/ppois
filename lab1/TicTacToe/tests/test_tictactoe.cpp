#include <gtest/gtest.h>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
#include "../include/tictactoe.hpp"

namespace {
TicTacToe makeBoard(const std::vector<std::string>& rows) {
    TicTacToe game(static_cast<int>(rows.size()));
    for (int i = 0; i < static_cast<int>(rows.size()); ++i) {
        for (int j = 0; j < static_cast<int>(rows[i].size()); ++j) {
            if (rows[i][j] != '.') game.setMove(i, j, rows[i][j]);
        }
    }
    return game;
}

}

TEST(TicTacToeTest, Initialization) {
    TicTacToe game(3);
    EXPECT_EQ(game.getSize(), 3);
    EXPECT_EQ(game.getCurrentPlayer(), 'X');
    EXPECT_EQ(game.checkWinner(), ' ');
    EXPECT_FALSE(game.isBoardFull());

    for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) {
            EXPECT_EQ(game.getCell(i, j), ' ');
        }
    }
}

TEST(TicTacToeTest, DefaultConstructor) {
    TicTacToe game;
    EXPECT_EQ(game.getSize(), 3);
    EXPECT_EQ(game.getCurrentPlayer(), 'X');
}

TEST(TicTacToeTest, CustomSize) {
    TicTacToe game(5);
    EXPECT_EQ(game.getSize(), 5);
    EXPECT_EQ(game.getCell(4, 4), ' ');
}

TEST(TicTacToeTest, InvalidSizeException) {
    EXPECT_THROW(TicTacToe game(0), std::invalid_argument);
    EXPECT_THROW(TicTacToe game(-2), std::invalid_argument);
}

TEST(TicTacToeTest, ValidMoves) {
    TicTacToe game(3);
    EXPECT_TRUE(game.isValidMove(0, 0));

    game.setMove(0, 0, 'X');
    EXPECT_EQ(game.getCell(0, 0), 'X');
    EXPECT_FALSE(game.isValidMove(0, 0));
}

TEST(TicTacToeTest, IsValidMoveOutOfBounds) {
    TicTacToe game(3);
    EXPECT_FALSE(game.isValidMove(-1, 0));
    EXPECT_FALSE(game.isValidMove(0, -1));
    EXPECT_FALSE(game.isValidMove(3, 0));
    EXPECT_FALSE(game.isValidMove(0, 3));
    EXPECT_FALSE(game.isValidMove(3, 3));
    EXPECT_TRUE(game.isValidMove(2, 2));
}

TEST(TicTacToeTest, SetMoveSwitchesCurrentPlayer) {
    TicTacToe game(3);
    EXPECT_EQ(game.getCurrentPlayer(), 'X');
    game.setMove(0, 0, 'X');
    EXPECT_EQ(game.getCurrentPlayer(), 'O');
    game.setMove(1, 1, 'O');
    EXPECT_EQ(game.getCurrentPlayer(), 'X');
}

TEST(TicTacToeTest, SetMoveInvalidMark) {
    TicTacToe game(3);
    EXPECT_THROW(game.setMove(0, 0, 'Z'), std::invalid_argument);
    EXPECT_THROW(game.setMove(0, 0, ' '), std::invalid_argument);
    EXPECT_EQ(game.getCell(0, 0), ' ');
    EXPECT_EQ(game.getCurrentPlayer(), 'X');
}

TEST(TicTacToeTest, SetMoveOccupiedCell) {
    TicTacToe game(3);
    game.setMove(0, 0, 'X');
    EXPECT_THROW(game.setMove(0, 0, 'O'), std::invalid_argument);
    EXPECT_EQ(game.getCell(0, 0), 'X');
    EXPECT_EQ(game.getCurrentPlayer(), 'O');
}

TEST(TicTacToeTest, SetMoveOutOfRange) {
    TicTacToe game(3);
    EXPECT_THROW(game.setMove(-1, 0, 'X'), std::out_of_range);
    EXPECT_THROW(game.setMove(0, -1, 'X'), std::out_of_range);
    EXPECT_THROW(game.setMove(3, 0, 'X'), std::out_of_range);
    EXPECT_THROW(game.setMove(0, 3, 'X'), std::out_of_range);
    EXPECT_THROW(game.setMove(5, 5, 'O'), std::out_of_range);
}

TEST(TicTacToeTest, GetCellOutOfRange) {
    TicTacToe game(3);
    EXPECT_THROW(game.getCell(-1, 0), std::out_of_range);
    EXPECT_THROW(game.getCell(0, -1), std::out_of_range);
    EXPECT_THROW(game.getCell(3, 0), std::out_of_range);
    EXPECT_THROW(game.getCell(0, 3), std::out_of_range);
    EXPECT_THROW(game.getCell(5, 5), std::out_of_range);
}

TEST(TicTacToeTest, RowWinner) {
    for (int r = 0; r < 3; ++r) {
        for (char mark : {'X', 'O'}) {
            TicTacToe game(3);
            for (int c = 0; c < 3; ++c) game.setMove(r, c, mark);
            EXPECT_EQ(game.checkWinner(), mark) << "row " << r;
        }
    }
}

TEST(TicTacToeTest, ColumnWinner) {
    for (int c = 0; c < 3; ++c) {
        for (char mark : {'X', 'O'}) {
            TicTacToe game(3);
            for (int r = 0; r < 3; ++r) game.setMove(r, c, mark);
            EXPECT_EQ(game.checkWinner(), mark) << "col " << c;
        }
    }
}

TEST(TicTacToeTest, DiagonalWinner) {
    TicTacToe game(3);
    game.setMove(0, 0, 'O');
    game.setMove(1, 1, 'O');
    game.setMove(2, 2, 'O');
    EXPECT_EQ(game.checkWinner(), 'O');
}

TEST(TicTacToeTest, AntiDiagonalWinner) {
    TicTacToe game(3);
    game.setMove(0, 2, 'X');
    game.setMove(1, 1, 'X');
    game.setMove(2, 0, 'X');
    EXPECT_EQ(game.checkWinner(), 'X');
}

TEST(TicTacToeTest, NoWinnerOnEmptyBoard) {
    TicTacToe game(4);
    EXPECT_EQ(game.checkWinner(), ' ');
}

TEST(TicTacToeTest, NoWinnerOnIncompleteLines) {
    EXPECT_EQ(makeBoard({"XX.", "...", "..."}).checkWinner(), ' ');
    EXPECT_EQ(makeBoard({".XX", "...", "..."}).checkWinner(), ' ');
    EXPECT_EQ(makeBoard({"X.X", "...", "..."}).checkWinner(), ' ');
}

TEST(TicTacToeTest, NoWinnerOnMixedLines) {
    EXPECT_EQ(makeBoard({"XXO", "...", "..."}).checkWinner(), ' ');
    EXPECT_EQ(makeBoard({"X..", "O..", "X.."}).checkWinner(), ' ');
    EXPECT_EQ(makeBoard({"X..", ".O.", "..X"}).checkWinner(), ' ');
    EXPECT_EQ(makeBoard({"..X", ".O.", "X.."}).checkWinner(), ' ');
}

TEST(TicTacToeTest, WinnerOnLargerBoard) {
    TicTacToe game(4);
    for (int i = 0; i < 4; ++i) game.setMove(i, 3 - i, 'O');
    EXPECT_EQ(game.checkWinner(), 'O');

    TicTacToe almost(4);
    for (int i = 0; i < 3; ++i) almost.setMove(1, i, 'X');
    EXPECT_EQ(almost.checkWinner(), ' ');
}

TEST(TicTacToeTest, SingleCellBoard) {
    TicTacToe game(1);
    EXPECT_EQ(game.checkWinner(), ' ');
    EXPECT_FALSE(game.isBoardFull());
    game.setMove(0, 0, 'X');
    EXPECT_EQ(game.checkWinner(), 'X');
    EXPECT_TRUE(game.isBoardFull());
}

TEST(TicTacToeTest, BoardNotFull) {
    TicTacToe game(3);
    EXPECT_FALSE(game.isBoardFull());
    game.setMove(0, 0, 'X');
    EXPECT_FALSE(game.isBoardFull());
}

TEST(TicTacToeTest, BoardFullDraw) {
    TicTacToe game = makeBoard({"XOX",
                                "XOX",
                                "OXO"});
    EXPECT_TRUE(game.isBoardFull());
    EXPECT_EQ(game.checkWinner(), ' ');
}

TEST(TicTacToeTest, CopyAndAssign) {
    TicTacToe game1(3);
    game1.setMove(0, 0, 'X');

    TicTacToe game2(game1);
    EXPECT_EQ(game1, game2);

    TicTacToe game3;
    game3 = game1;
    EXPECT_TRUE(game1 == game3);
    EXPECT_FALSE(game1 != game3);

    game2.setMove(1, 1, 'O');
    EXPECT_NE(game1, game2);
    EXPECT_EQ(game1.getCell(1, 1), ' ');
}

TEST(TicTacToeTest, SelfAssign) {
    TicTacToe game(3);
    game.setMove(0, 0, 'X');
    TicTacToe& ref = game;
    game = ref;
    EXPECT_EQ(game.getCell(0, 0), 'X');
    EXPECT_EQ(game.getSize(), 3);
}

TEST(TicTacToeTest, EqualityDetectsDifferences) {
    TicTacToe a(3), b(3);
    EXPECT_TRUE(a == b);

    EXPECT_FALSE(a == TicTacToe(4));
    EXPECT_TRUE(a != TicTacToe(4));


    TicTacToe c(3), d(3);
    c.setMove(0, 0, 'X');
    d.setMove(0, 0, 'O');
    EXPECT_NE(c, d);


    TicTacToe e(3), f(3);
    e.setMove(0, 0, 'X');
    f.setMove(0, 1, 'X');
    EXPECT_NE(e, f);
}

TEST(TicTacToeTest, OutputFormat) {
    TicTacToe game(2);
    game.setMove(0, 1, 'X');

    std::ostringstream os;
    os << game;
    EXPECT_EQ(os.str(), "2 O\n. X\n. .\n");
}


TEST(TicTacToeTest, StreamOperators) {
    TicTacToe game1(3);
    game1.setMove(0, 0, 'X');

    std::stringstream ss;
    ss << game1;

    TicTacToe game2;
    ss >> game2;
    EXPECT_TRUE(ss);
    EXPECT_EQ(game1, game2);
}

TEST(TicTacToeTest, StreamRoundTripKeepsEmptyCells) {

    TicTacToe game = makeBoard({"X..",
                                ".O.",
                                "..X"});
    std::stringstream ss;
    ss << game;

    TicTacToe loaded;
    ss >> loaded;
    EXPECT_TRUE(ss);
    EXPECT_EQ(game, loaded);
    EXPECT_EQ(loaded.getCell(0, 1), ' ');
    EXPECT_EQ(loaded.getCell(1, 1), 'O');
    EXPECT_EQ(loaded.getCell(2, 2), 'X');
}

TEST(TicTacToeTest, StreamChangesSize) {
    TicTacToe big(5);
    big.setMove(4, 4, 'X');
    std::stringstream ss;
    ss << big;

    TicTacToe game(3);
    ss >> game;
    EXPECT_EQ(game.getSize(), 5);
    EXPECT_EQ(game.getCell(4, 4), 'X');
    EXPECT_EQ(game.getCurrentPlayer(), 'O');
}

TEST(TicTacToeTest, StreamReadsFromLiteral) {
    std::istringstream is("3 O\nX . .\n. O .\n. . X\n");
    TicTacToe game;
    is >> game;
    EXPECT_TRUE(is);
    EXPECT_EQ(game.getCurrentPlayer(), 'O');
    EXPECT_EQ(game.getCell(0, 0), 'X');
    EXPECT_EQ(game.getCell(1, 1), 'O');
    EXPECT_EQ(game.getCell(2, 2), 'X');
    EXPECT_EQ(game.getCell(0, 2), ' ');
}

TEST(TicTacToeTest, StreamAcceptsMaxSize) {
    std::string data = "100 X\n";
    for (int i = 0; i < 100; ++i) {
        for (int j = 0; j < 100; ++j) data += (j ? " ." : ".");
        data += "\n";
    }
    std::istringstream is(data);
    TicTacToe game;
    is >> game;
    EXPECT_TRUE(is);
    EXPECT_EQ(game.getSize(), 100);
}


class StreamFailureTest : public ::testing::TestWithParam<std::string> {};

TEST_P(StreamFailureTest, FailsAndKeepsGameUnchanged) {
    TicTacToe game(3);
    game.setMove(1, 1, 'X');
    const TicTacToe before = game;

    std::istringstream is(GetParam());
    is >> game;

    EXPECT_TRUE(is.fail());
    EXPECT_EQ(game, before);
}

INSTANTIATE_TEST_SUITE_P(
    BadInputs, StreamFailureTest,
    ::testing::Values(
        std::string(""),
        std::string("abc X\n"),
        std::string("3\n"),
        std::string("0 X\n"),
        std::string("-3 X\n"),
        std::string("101 X\n"), 
        std::string("2 Z\n. .\n. .\n"),
        std::string("2 X\n. Q\n. .\n"),
        std::string("2 X\n. .\n.\n"),
        std::string("3 X\nX O\n")                
    ));

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
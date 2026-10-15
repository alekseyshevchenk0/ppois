#include <gtest/gtest.h>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
#include "../include/tictactoe.hpp"

namespace {

TicTacToe makeBoard(const std::vector<std::string>& rows) {
    TicTacToe game(static_cast<int>(rows.size()));
    for (int row = 0; row < static_cast<int>(rows.size()); ++row) {
        for (int col = 0; col < static_cast<int>(rows[row].size()); ++col) {
            if (rows[row][col] != '.') game.setMove(row, col, rows[row][col]);
        }
    }
    return game;
}

std::string emptyBoardText(int size) {
    std::string text = std::to_string(size) + " X\n";
    for (int row = 0; row < size; ++row) {
        for (int col = 0; col < size; ++col) text += (col ? " ." : ".");
        text += "\n";
    }
    return text;
}

}  

TEST(TicTacToeTest, Initialization) {
    TicTacToe game(3);
    EXPECT_EQ(game.getSize(), 3);
    EXPECT_EQ(game.getCurrentPlayer(), TicTacToe::PLAYER_X);
    EXPECT_EQ(game.checkWinner(), TicTacToe::EMPTY_CELL);
    EXPECT_FALSE(game.isBoardFull());

    for (int row = 0; row < 3; ++row) {
        for (int col = 0; col < 3; ++col) {
            EXPECT_EQ(game.getCell(row, col), TicTacToe::EMPTY_CELL);
        }
    }
}

TEST(TicTacToeTest, DefaultConstructor) {
    TicTacToe game;
    EXPECT_EQ(game.getSize(), TicTacToe::DEFAULT_SIZE);
    EXPECT_EQ(game.getCurrentPlayer(), TicTacToe::PLAYER_X);
}

TEST(TicTacToeTest, CustomSize) {
    TicTacToe game(5);
    EXPECT_EQ(game.getSize(), 5);
    EXPECT_EQ(game.getCell(4, 4), TicTacToe::EMPTY_CELL);
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
    EXPECT_EQ(game.getCurrentPlayer(), TicTacToe::PLAYER_X);
    game.setMove(0, 0, 'X');
    EXPECT_EQ(game.getCurrentPlayer(), TicTacToe::PLAYER_O);
    game.setMove(1, 1, 'O');
    EXPECT_EQ(game.getCurrentPlayer(), TicTacToe::PLAYER_X);
}

TEST(TicTacToeTest, SetMoveInvalidMark) {
    TicTacToe game(3);
    EXPECT_THROW(game.setMove(0, 0, 'Z'), std::invalid_argument);
    EXPECT_THROW(game.setMove(0, 0, ' '), std::invalid_argument);
    EXPECT_EQ(game.getCell(0, 0), TicTacToe::EMPTY_CELL);
    EXPECT_EQ(game.getCurrentPlayer(), TicTacToe::PLAYER_X);
}

TEST(TicTacToeTest, SetMoveOccupiedCell) {
    TicTacToe game(3);
    game.setMove(0, 0, 'X');
    EXPECT_THROW(game.setMove(0, 0, 'O'), std::invalid_argument);
    EXPECT_EQ(game.getCell(0, 0), 'X');
    EXPECT_EQ(game.getCurrentPlayer(), TicTacToe::PLAYER_O);
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
    for (int row = 0; row < 3; ++row) {
        for (char mark : {'X', 'O'}) {
            TicTacToe game(3);
            for (int col = 0; col < 3; ++col) game.setMove(row, col, mark);
            EXPECT_EQ(game.checkWinner(), mark) << "row " << row;
        }
    }
}

TEST(TicTacToeTest, ColumnWinner) {
    for (int col = 0; col < 3; ++col) {
        for (char mark : {'X', 'O'}) {
            TicTacToe game(3);
            for (int row = 0; row < 3; ++row) game.setMove(row, col, mark);
            EXPECT_EQ(game.checkWinner(), mark) << "col " << col;
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
    EXPECT_EQ(game.checkWinner(), TicTacToe::EMPTY_CELL);
}

TEST(TicTacToeTest, NoWinnerOnIncompleteLines) {
    EXPECT_EQ(makeBoard({"XX.", "...", "..."}).checkWinner(), TicTacToe::EMPTY_CELL);
    EXPECT_EQ(makeBoard({".XX", "...", "..."}).checkWinner(), TicTacToe::EMPTY_CELL);
    EXPECT_EQ(makeBoard({"X.X", "...", "..."}).checkWinner(), TicTacToe::EMPTY_CELL);
}

TEST(TicTacToeTest, NoWinnerOnMixedLines) {
    EXPECT_EQ(makeBoard({"XXO", "...", "..."}).checkWinner(), TicTacToe::EMPTY_CELL);
    EXPECT_EQ(makeBoard({"X..", "O..", "X.."}).checkWinner(), TicTacToe::EMPTY_CELL);
    EXPECT_EQ(makeBoard({"X..", ".O.", "..X"}).checkWinner(), TicTacToe::EMPTY_CELL);
    EXPECT_EQ(makeBoard({"..X", ".O.", "X.."}).checkWinner(), TicTacToe::EMPTY_CELL);
}

TEST(TicTacToeTest, WinnerOnLargerBoard) {
    TicTacToe fullLine(4);
    for (int index = 0; index < 4; ++index) fullLine.setMove(index, 3 - index, 'O');
    EXPECT_EQ(fullLine.checkWinner(), 'O');

    TicTacToe almostLine(4);
    for (int col = 0; col < 3; ++col) almostLine.setMove(1, col, 'X');
    EXPECT_EQ(almostLine.checkWinner(), TicTacToe::EMPTY_CELL);
}

TEST(TicTacToeTest, SingleCellBoard) {
    TicTacToe game(1);
    EXPECT_EQ(game.checkWinner(), TicTacToe::EMPTY_CELL);
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
    EXPECT_EQ(game.checkWinner(), TicTacToe::EMPTY_CELL);
}

TEST(TicTacToeTest, CopyAndAssign) {
    TicTacToe original(3);
    original.setMove(0, 0, 'X');

    TicTacToe copied(original);
    EXPECT_EQ(original, copied);

    TicTacToe assigned;
    assigned = original;
    EXPECT_TRUE(original == assigned);
    EXPECT_FALSE(original != assigned);

    copied.setMove(1, 1, 'O');
    EXPECT_NE(original, copied);
    EXPECT_EQ(original.getCell(1, 1), TicTacToe::EMPTY_CELL);
}

TEST(TicTacToeTest, SelfAssign) {
    TicTacToe game(3);
    game.setMove(0, 0, 'X');
    TicTacToe& sameGame = game;
    game = sameGame;
    EXPECT_EQ(game.getCell(0, 0), 'X');
    EXPECT_EQ(game.getSize(), 3);
}

TEST(TicTacToeTest, EqualityDetectsDifferentSize) {
    EXPECT_TRUE(TicTacToe(3) == TicTacToe(3));
    EXPECT_FALSE(TicTacToe(3) == TicTacToe(4));
    EXPECT_TRUE(TicTacToe(3) != TicTacToe(4));
}

TEST(TicTacToeTest, EqualityDetectsDifferentCurrentPlayer) {
    TicTacToe xMovedFirst(3);
    TicTacToe oMovedFirst(3);
    xMovedFirst.setMove(0, 0, 'X');
    oMovedFirst.setMove(0, 0, 'O');
    EXPECT_NE(xMovedFirst, oMovedFirst);
}

TEST(TicTacToeTest, EqualityDetectsDifferentCells) {
    TicTacToe movedToCorner(3);
    TicTacToe movedToEdge(3);
    movedToCorner.setMove(0, 0, 'X');
    movedToEdge.setMove(0, 1, 'X');
    EXPECT_NE(movedToCorner, movedToEdge);
}

TEST(TicTacToeTest, OutputFormat) {
    TicTacToe game(2);
    game.setMove(0, 1, 'X');

    std::ostringstream output;
    output << game;
    EXPECT_EQ(output.str(), "2 O\n. X\n. .\n");
}

TEST(TicTacToeTest, StreamOperators) {
    TicTacToe original(3);
    original.setMove(0, 0, 'X');

    std::stringstream stream;
    stream << original;

    TicTacToe loaded;
    stream >> loaded;
    EXPECT_TRUE(stream);
    EXPECT_EQ(original, loaded);
}

TEST(TicTacToeTest, StreamRoundTripKeepsEmptyCells) {
    TicTacToe original = makeBoard({"X..",
                                    ".O.",
                                    "..X"});
    std::stringstream stream;
    stream << original;

    TicTacToe loaded;
    stream >> loaded;
    EXPECT_TRUE(stream);
    EXPECT_EQ(original, loaded);
    EXPECT_EQ(loaded.getCell(0, 1), TicTacToe::EMPTY_CELL);
    EXPECT_EQ(loaded.getCell(1, 1), 'O');
    EXPECT_EQ(loaded.getCell(2, 2), 'X');
}

TEST(TicTacToeTest, StreamChangesSize) {
    TicTacToe bigGame(5);
    bigGame.setMove(4, 4, 'X');
    std::stringstream stream;
    stream << bigGame;

    TicTacToe game(3);
    stream >> game;
    EXPECT_EQ(game.getSize(), 5);
    EXPECT_EQ(game.getCell(4, 4), 'X');
    EXPECT_EQ(game.getCurrentPlayer(), TicTacToe::PLAYER_O);
}

TEST(TicTacToeTest, StreamReadsFromLiteral) {
    std::istringstream input("3 O\nX . .\n. O .\n. . X\n");
    TicTacToe game;
    input >> game;
    EXPECT_TRUE(input);
    EXPECT_EQ(game.getCurrentPlayer(), TicTacToe::PLAYER_O);
    EXPECT_EQ(game.getCell(0, 0), 'X');
    EXPECT_EQ(game.getCell(1, 1), 'O');
    EXPECT_EQ(game.getCell(2, 2), 'X');
    EXPECT_EQ(game.getCell(0, 2), TicTacToe::EMPTY_CELL);
}

TEST(TicTacToeTest, StreamAcceptsMaxSize) {
    std::istringstream input(emptyBoardText(100));
    TicTacToe game;
    input >> game;
    EXPECT_TRUE(input);
    EXPECT_EQ(game.getSize(), 100);
}

class StreamFailureTest : public ::testing::TestWithParam<std::string> {};

TEST_P(StreamFailureTest, FailsAndKeepsGameUnchanged) {
    TicTacToe game(3);
    game.setMove(1, 1, 'X');
    const TicTacToe before = game;

    std::istringstream input(GetParam());
    input >> game;

    EXPECT_TRUE(input.fail());
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

cmake_minimum_required(VERSION 3.10)
project(TicTacToeLab)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

add_executable(tictactoe_game 
    src/main.cpp 
    src/tictactoe.cpp
)
enable_testing()
include(FetchContent)
FetchContent_Declare(
  googletest
  URL https://github.com/google/googletest/archive/refs/tags/v1.14.0.zip
)
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

add_executable(tictactoe_tests 
    tests/test_tictactoe.cpp 
    src/tictactoe.cpp
)
target_link_libraries(tictactoe_tests GTest::gtest_main)

include(GoogleTest)
gtest_discover_tests(tictactoe_tests)
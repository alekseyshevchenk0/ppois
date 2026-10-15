cmake_minimum_required(VERSION 3.20)

project(TicTacToe LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

option(BUILD_TESTS "Собирать unit-тесты" ON)
option(ENABLE_COVERAGE "Включить покрытие кода тестами" ON)
option(BUILD_DOCS "Генерировать документацию Doxygen" ON)

# Общие настройки компиляции
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    add_compile_options(-Wall -Wextra)
endif()

# Библиотека игры
add_library(tictactoe STATIC
    src/tictactoe.cpp
)

target_include_directories(tictactoe
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)

# Пользовательское приложение
add_executable(tictactoe_ui
    src/main.cpp
)

target_link_libraries(tictactoe_ui
    PRIVATE
        tictactoe
)

# Unit-тесты
if(BUILD_TESTS)
    enable_testing()

    find_package(GTest REQUIRED)
    find_package(Threads REQUIRED)

    add_executable(run_tests
        tests/test_tictactoe.cpp
    )

    target_link_libraries(run_tests
        PRIVATE
            tictactoe
            GTest::gtest
            Threads::Threads
    )

    add_test(
        NAME tictactoe_tests
        COMMAND run_tests
    )
endif()

# Покрытие кода тестами: GCC / Clang
if(ENABLE_COVERAGE)
    if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU"
       OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")

        # Инструментация библиотеки
        target_compile_options(tictactoe PRIVATE
            --coverage
            -O0
            -g
        )

        # Инструментация приложения
        target_compile_options(tictactoe_ui PRIVATE
            --coverage
            -O0
            -g
        )
        target_link_options(tictactoe_ui PRIVATE --coverage)

        # Инструментация тестов
        if(BUILD_TESTS)
            target_compile_options(run_tests PRIVATE
                --coverage
                -O0
                -g
            )
            target_link_options(run_tests PRIVATE --coverage)
        endif()

    else()
        message(WARNING
            "Покрытие кода поддерживается только для GCC и Clang."
        )
    endif()
endif()

# Документация Doxygen — независимо от покрытия и тестов
if(BUILD_DOCS)
    find_package(Doxygen QUIET)

    if(DOXYGEN_FOUND)
        set(DOXYGEN_OUTPUT_DIRECTORY
            "${CMAKE_CURRENT_BINARY_DIR}/docs"
        )
        set(DOXYGEN_HTML_OUTPUT "html")
        set(DOXYGEN_GENERATE_HTML YES)
        set(DOXYGEN_GENERATE_LATEX NO)
        set(DOXYGEN_EXTRACT_ALL YES)
        set(DOXYGEN_RECURSIVE NO)
        set(DOXYGEN_QUIET YES)
        set(DOXYGEN_PROJECT_NAME "TicTacToe")

        doxygen_add_docs(docs
            "${CMAKE_CURRENT_SOURCE_DIR}/include/tictactoe.hpp"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/tictactoe.cpp"
            COMMENT "Генерация документации Doxygen"
        )

        message(STATUS
            "Документация: ${DOXYGEN_OUTPUT_DIRECTORY}/html/index.html"
        )
    else()
        message(WARNING
            "Doxygen не найден. Установи его командой: "
            "sudo dnf install doxygen graphviz"
        )
    endif()
endif()
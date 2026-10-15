cmake_minimum_required(VERSION 3.20)
project(Polynomial LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

option(BUILD_TESTS "Собирать unit-тесты (нужен GoogleTest)" ON)
option(ENABLE_COVERAGE "Собирать с инструментацией для gcov (GCC/Clang)" OFF)

add_library(polynomial STATIC src/polynomial.cpp)
target_include_directories(polynomial PUBLIC include)
if(NOT MSVC)
    target_compile_options(polynomial PRIVATE -Wall -Wextra)
endif()

add_executable(poly_ui src/main.cpp)
target_link_libraries(poly_ui PRIVATE polynomial)

if(ENABLE_COVERAGE)
    target_compile_options(polynomial PUBLIC --coverage -O0)
    target_link_options(polynomial PUBLIC --coverage)
endif()

if(BUILD_TESTS)
    enable_testing()
    find_package(GTest REQUIRED)
    find_package(Threads REQUIRED)

    add_executable(run_tests tests/test_polynomial.cpp)
    target_link_libraries(run_tests PRIVATE polynomial GTest::gtest Threads::Threads)
    add_test(NAME polynomial_tests COMMAND run_tests)
endif()

find_package(Doxygen QUIET)
if(DOXYGEN_FOUND)
    set(DOXYGEN_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/docs")
    set(DOXYGEN_OUTPUT_LANGUAGE Russian)
    set(DOXYGEN_EXTRACT_PRIVATE YES)
    set(DOXYGEN_GENERATE_LATEX NO)
    doxygen_add_docs(docs include COMMENT "Генерация документации Doxygen")
endif()

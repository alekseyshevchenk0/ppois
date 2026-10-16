cmake_minimum_required(VERSION 3.20)

project(Polynomial LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

option(BUILD_TESTS "Собирать unit-тесты" ON)
option(ENABLE_COVERAGE "Включить покрытие кода тестами" OFF)
option(BUILD_DOCS "Генерировать документацию Doxygen" ON)

if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    add_compile_options(-Wall -Wextra -Wpedantic)
endif()

add_library(polynomial STATIC
    src/polynomial.cpp
)

target_include_directories(polynomial
    PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include
)

add_executable(poly_ui
    src/main.cpp
)

target_link_libraries(poly_ui PRIVATE polynomial)

if(BUILD_TESTS)
    enable_testing()

    find_package(GTest REQUIRED)

    add_executable(run_tests
        tests/test_polynomial.cpp
    )

    target_link_libraries(run_tests
        PRIVATE polynomial GTest::gtest
    )

    add_test(
        NAME polynomial_tests
        COMMAND run_tests
    )
endif()

if(ENABLE_COVERAGE)
    if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
        foreach(target polynomial poly_ui)
            target_compile_options(${target}
                PRIVATE --coverage -O0 -g
            )
            target_link_options(${target}
                PRIVATE --coverage
            )
        endforeach()

        if(BUILD_TESTS)
            target_compile_options(run_tests
                PRIVATE --coverage -O0 -g
            )
            target_link_options(run_tests
                PRIVATE --coverage
            )
        endif()
    else()
        message(WARNING
            "Покрытие поддерживается только для GCC и Clang."
        )
    endif()
endif()

if(BUILD_DOCS)
    find_package(Doxygen QUIET)

    if(DOXYGEN_FOUND)
        set(DOXYGEN_OUTPUT_DIRECTORY
            "${CMAKE_BINARY_DIR}/docs"
        )
        set(DOXYGEN_HTML_OUTPUT "html")
        set(DOXYGEN_GENERATE_HTML YES)
        set(DOXYGEN_GENERATE_LATEX NO)
        set(DOXYGEN_OUTPUT_LANGUAGE Russian)
        set(DOXYGEN_EXTRACT_ALL YES)
        set(DOXYGEN_WARN_IF_UNDOCUMENTED YES)
        set(DOXYGEN_QUIET NO)

        doxygen_add_docs(docs
            "${CMAKE_CURRENT_SOURCE_DIR}/include"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/polynomial.cpp"
            COMMENT "Генерация документации Doxygen"
        )
    else()
        message(WARNING
            "Doxygen не найден. Установи его: "
            "sudo dnf install doxygen graphviz"
        )
    endif()
endif()
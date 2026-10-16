# PPOIS Labs

## Structure

| Lab | Language | Contents | Docs |
|-----|----------|----------|------|
| 1 | C++ | [TicTacToe](./lab1/TicTacToe), [Polynomial](./lab1/Polynomial) | Doxygen, [Documentation](#documentation) |

Each project has the same layout:

```text
include/   class declarations (.hpp)
src/       class implementation and console menu (main.cpp)
tests/     unit tests (GoogleTest)
```

## Requirements

- C++17 compiler (g++)
- [CMake](https://cmake.org/) 3.20+
- [GoogleTest](https://github.com/google/googletest) — unit tests
- [gcovr](https://gcovr.com/) — code coverage
- [cppcheck](https://cppcheck.sourceforge.io/) — static analysis
- [Doxygen](https://www.doxygen.nl/) — documentation

## Build and run

From the project directory:

```bash
cmake -B build
cmake --build build
```

Code coverage:

```bash
cmake -B build -DCMAKE_BUILD_TYPE=Debug -DBUILD_TESTS=ON -DENABLE_COVERAGE=ON
cmake --build build
ctest --test-dir build --output-on-failure
gcovr --root . --object-directory build --filter 'src/' --exclude 'src/main.cpp' --txt-metric line --txt-metric branch
```

## Documentation

Generated with [Doxygen](https://www.doxygen.nl/).

The HTML documentation is generated in `docs/html`. Open `docs/html/index.html` in a browser.

## Releases

Project archives for Linux are published in [Releases](https://github.com/alekseyshevchenk0/ppois/releases).
# PPOIS Labs

## Structure

| Lab | Language | Contents | Docs |
|-----|----------|----------|------|
| 1 | C++ | [TicTacToe](./lab1/TicTacToe), [Polynomial](./lab1/Polynomial) | Doxygen, [Documentation](#documentation) |
| 2 | Python | [Audio Collection](./lab2) | [lab2/README.md](./lab2/README.md) |

Each lab 1 project has the same layout:

```text
include/   class declarations (.hpp)
src/       class implementation and console menu (main.cpp)
tests/     unit tests (GoogleTest)
```

Lab 2 layout:

```text
audio_collection/   domain model: classes, constants, custom exceptions
cli/                console interface
tests/              unit tests (pytest)
```

## Requirements

### Lab 1 (C++)

- C++17 compiler (g++)
- [CMake](https://cmake.org/) 3.20+
- [GoogleTest](https://github.com/google/googletest) — unit tests
- [gcovr](https://gcovr.com/) — code coverage
- [cppcheck](https://cppcheck.sourceforge.io/) — static analysis
- [Doxygen](https://www.doxygen.nl/) — documentation

### Lab 2 (Python)

- Python 3.10+
- [pytest](https://pytest.org/) and [pytest-cov](https://pytest-cov.readthedocs.io/) — unit tests and coverage
- [flake8](https://flake8.pycqa.org/) — static analysis
- [PyInstaller](https://pyinstaller.org/) — building the release executable (used in CI only)

The Python tools are listed in `lab2/requirements-dev.txt`.

## Build and run

### Lab 1

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
gcovr --root . --object-directory build --filter 'src/' --exclude 'src/main.cpp' --txt-metric line
```

### Lab 2

From the `lab2` directory (Linux / macOS):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

On Windows (PowerShell) activate the environment with `.venv\Scripts\Activate.ps1`.

Run the console application:

```bash
python -m cli
```

Tests with coverage (the build fails if coverage is below 90%) and static analysis:

```bash
python -m pytest
flake8 .
```

## Documentation

### Lab 1

Generated with [Doxygen](https://www.doxygen.nl/).

The HTML documentation is generated in `docs/html`. Open `docs/html/index.html` in a browser.

### Lab 2

Documented in [lab2/README.md](./lab2/README.md): all classes with their fields and
behaviours, associations between classes, custom exceptions, the console menu and
development instructions.

## Releases

Project archives for Linux are published in [Releases](https://github.com/alekseyshevchenk0/ppois/releases).


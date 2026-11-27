# Merge sort. Bozo sort. Directed graph (orthogonal adjacency list)

## Implemented functionality

- Merge sort and Bozo sort for lists and user-defined objects.
- A generic directed graph implemented using an orthogonal adjacency list.
- Graph operations for adding, removing, and checking vertices and edges.
- Vertex and edge degree calculations.
- Forward, reverse, bidirectional, and const iterator variants.
- Removal of vertices and edges through iterators.
- Graph copying, assignment, clearing, and comparison operators.
- A console menu for demonstrating the sorting algorithms and graph operations.
- Unit tests written with `pytest` and test coverage measured with `pytest-cov`.

## Requirements

- Python 3.10 or newer
- Dependencies listed in `requirements-dev.txt`

## Installation

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell, activate it with:

```powershell
.venv\Scripts\Activate.ps1
```

Install the development dependencies:

```bash
pip install -r requirements-dev.txt
```

## Run the application

```bash
python main.py
```

Use the console menu to run Merge sort and Bozo sort or to explore the directed graph. In the graph menu, select **18. Bidirectional iterator movement** to interactively move to the next or previous vertex or edge:

- `n` — move to the next element;
- `p` — move to the previous element;
- `0` — return to the graph menu.

## Run tests

Run the test suite:

```bash
pytest -v
```

Run tests with coverage:

```bash
pytest --cov=graph --cov=sorting --cov=models --cov-report=term-missing
```

## Code style

Check the project with Flake8:

```bash
flake8 .
```

Bozo sort has a configurable maximum number of shuffles (`max_attempts`) because the algorithm is extremely inefficient for practical input sizes.

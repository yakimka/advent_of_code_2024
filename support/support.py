from __future__ import annotations

import argparse
import contextlib
import heapq
import os.path
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import deque
from functools import partial
from typing import Any, Callable, Generator, Hashable, Iterable, TextIO, TypeVar

HERE = os.path.dirname(os.path.abspath(__file__))


def _get_cookie_headers() -> dict[str, str]:
    with open(os.path.join(HERE, "../.env")) as f:
        contents = f.read().strip()
    return {"Cookie": contents, "User-Agent": "Merry Christmas!"}


def get_input(year: int, day: int) -> str:
    url = f"https://adventofcode.com/{year}/day/{day}/input"
    req = urllib.request.Request(url, headers=_get_cookie_headers())
    return urllib.request.urlopen(req).read().decode()


def get_year_day() -> tuple[int, int]:
    cwd = os.getcwd()
    day_s = os.path.basename(cwd)
    year_s = os.path.basename(os.path.dirname(cwd))

    if not day_s.startswith("day") or not year_s.startswith("advent_of_code_"):
        raise AssertionError(f"unexpected working dir: {day_s=} {year_s=}")
    year_index = len("advent_of_code_")
    day_index = len("day")
    return int(year_s[year_index:]), int(day_s[day_index:])


def download_input() -> int:
    parser = argparse.ArgumentParser()
    parser.parse_args()

    year, day = get_year_day()

    for i in range(5):
        try:
            s = get_input(year, day)
        except urllib.error.URLError as e:
            print(f"zzz: not ready yet: {e}")
            time.sleep(1)
        else:
            break
    else:
        raise SystemExit("timed out after attempting many times")

    with open("input.txt", "w") as f:
        f.write(s)

    lines = s.splitlines()
    if len(lines) > 10:
        for line in lines[:10]:
            print(line)
        print("...")
    else:
        print(lines[0][:80])
        print("...")

    return 0


TOO_QUICK = re.compile("You gave an answer too recently.*to wait.")
WRONG = re.compile(r"That's not the right answer.*?\.")
RIGHT = "That's the right answer!"
ALREADY_DONE = re.compile(r"You don't seem to be solving.*\?")


def _post_answer(year: int, day: int, part: int, answer: int) -> str:
    params = urllib.parse.urlencode({"level": part, "answer": answer})
    req = urllib.request.Request(
        f"https://adventofcode.com/{year}/day/{day}/answer",
        method="POST",
        data=params.encode(),
        headers=_get_cookie_headers(),
    )
    resp = urllib.request.urlopen(req)

    return resp.read().decode()


def submit_solution() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--part", type=int, required=True)
    args = parser.parse_args()

    year, day = get_year_day()
    answer = int("".join(char for char in sys.stdin.read() if char.isdigit()))

    print(f"answer: {answer}")

    contents = _post_answer(year, day, args.part, answer)

    for error_regex in (WRONG, TOO_QUICK, ALREADY_DONE):
        error_match = error_regex.search(contents)
        if error_match:
            print(f"\033[41m{error_match[0]}\033[m")
            return 1

    if RIGHT in contents:
        print(f"\033[42m{RIGHT}\033[m")
        return 0
    else:
        # unexpected output?
        print(contents)
        return 1


def submit_25_pt2() -> int:
    parser = argparse.ArgumentParser()
    parser.parse_args()

    year, day = get_year_day()

    assert day == 25, day
    contents = _post_answer(year, day, part=2, answer=0)

    if "Congratulations!" in contents:
        print("\033[42mCongratulations!\033[m")
        return 0
    else:
        print(contents)
        return 1


def humanized_seconds(seconds: float) -> str:
    """Convert seconds to human-readable format."""

    if seconds >= 1:
        return f"{seconds:.2f}s"
    elif seconds >= 0.001:
        return f"{seconds * 1000:.0f}ms"
    elif seconds >= 0.000_001:
        return f"{seconds * 1_000_000:.0f}μs"
    else:
        return f"{seconds * 1_000_000_000:.0f}ns"


@contextlib.contextmanager
def timed(label: str) -> Generator[None, None, None]:
    start = time.perf_counter()
    try:
        yield
    finally:
        end = time.perf_counter()
        print(f"{label}: {humanized_seconds(end - start)}")


def print_matrix(matrix: list[list[Any]], file: TextIO | None = None) -> None:
    if not matrix or not matrix[0]:
        print("Empty matrix")
        return

    # Find the maximum length of any item in the matrix for formatting.
    max_item_len = max(len(str(item)) for row in matrix for item in row)

    # Determine the width for row and column labels.
    row_label_width = len(str(len(matrix) - 1))
    col_label_width = max(max_item_len, len(str(len(matrix[0]) - 1)))

    # Print column headers.
    col_headers = [" " * row_label_width] + [
        f"{i:<{col_label_width}}" for i in range(len(matrix[0]))
    ]
    if file is None:
        # For cases when printing in pytest or etc.
        print()
    print(" ".join(col_headers), file=file)

    # Print each row with its label.
    for i, row in enumerate(matrix):
        row_str = [f"{i:<{row_label_width}}"] + [
            f"{str(item):<{col_label_width}}" for item in row
        ]
        print(" ".join(row_str), file=file)


# ========================== helpers ==========================
def iter_lines_as_numbers(s: str) -> Generator[int, None, None]:
    for line in s.strip().splitlines():
        yield int(line)


class Range:
    __slots__ = ("start", "end")

    def __init__(self, start: int, end: int) -> None:
        self.start = start
        self.end = end
        if self.start >= self.end:
            raise ValueError(f"{self.start=} must be < {self.end=}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.start}, {self.end})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Range):
            return NotImplemented
        return self.start == other.start and self.end == other.end

    def __contains__(self, n: int) -> bool:
        return self.start <= n < self.end

    def __len__(self) -> int:
        return self.end - self.start

    def has_intersection(self, other: Range) -> bool:
        return self.start < other.end and other.start < self.end

    def intersection(self, other: Range) -> Range | None:
        if not self.has_intersection(other):
            return None
        return Range(max(self.start, other.start), min(self.end, other.end))

    def remainder(self, other: Range) -> list[Range]:
        intersection = self.intersection(other)
        if intersection is None:
            return []

        result = []
        if self.start < intersection.start:
            result.append(Range(self.start, intersection.start))
        if intersection.end < self.end:
            result.append(Range(intersection.end, self.end))
        return result


Coords = tuple[int, int]
inf_coords = (float("inf"), float("inf"))
T = TypeVar("T")


def make_matrix_from_input(
    s: str, *, split_by: str = "", cast_func: Callable[[str], T] = str
) -> tuple[list[list[T]], int, int]:
    matrix = []
    for line in s.strip().splitlines():
        if split_by:
            line = line.split(split_by)
        if cast_func is not str:
            matrix.append([cast_func(item) for item in line])
        else:
            matrix.append(list(line))

    m_len = len(matrix)
    n_len = len(matrix[0])
    return matrix, m_len, n_len


FilterFunc = Callable[[Iterable[Coords]], Generator[Coords, None, None]]


def neighbors_cross(
    m: int, n: int, *, max_bounds: Coords = inf_coords
) -> Generator[Coords, None, None]:
    neighbors = (
        (m, n - 1),
        (m - 1, n),
        (m + 1, n),
        (m, n + 1),
    )
    yield from filter_neighbors(neighbors, max_bounds=max_bounds)


def filter_neighbors(
    neighbors: Iterable[Coords], *, max_bounds: Coords = inf_coords
) -> Generator[Coords, None, None]:
    yield from (
        (m, n)
        for m, n in neighbors
        if 0 <= m <= max_bounds[0] and 0 <= n <= max_bounds[1]
    )


def neighbors_diag(
    m: int, n: int, *, max_bounds: Coords = inf_coords
) -> Generator[Coords, None, None]:
    neighbors = (
        (m - 1, n - 1),
        (m + 1, n - 1),
        (m - 1, n + 1),
        (m + 1, n + 1),
    )
    yield from filter_neighbors(neighbors, max_bounds=max_bounds)


def neighbors_cross_diag(
    m: int, n: int, *, max_bounds: Coords = inf_coords
) -> Generator[Coords, None, None]:
    yield from neighbors_cross(m, n, max_bounds=max_bounds)
    yield from neighbors_diag(m, n, max_bounds=max_bounds)


def cartesian_shortest_path(coords1: Coords, coords2: Coords) -> int:
    return abs(coords1[0] - coords2[0]) + abs(coords1[1] - coords2[1])


def cartesian_next_coords(x: int, y: int, direction: str, size: int = 1) -> Coords:
    if direction == "up":
        return x - size, y
    elif direction == "down":
        return x + size, y
    elif direction == "left":
        return x, y - size
    elif direction == "right":
        return x, y + size
    else:
        raise ValueError(f"Unknown direction {direction}")


def next_coords(
    m: int, n: int, direction: str, max_bounds: tuple[int, int] = inf_coords
) -> Coords | None:
    if direction == "up":
        next_m, next_n = m - 1, n
    elif direction == "down":
        next_m, next_n = m + 1, n
    elif direction == "left":
        next_m, next_n = m, n - 1
    elif direction == "right":
        next_m, next_n = m, n + 1
    else:
        raise ValueError(f"Unknown direction {direction}")

    if 0 > next_m or 0 > next_n or next_m > max_bounds[0] or next_n > max_bounds[1]:
        return None

    return next_m, next_n


def num_of_next_coords(
    m: int, n: int, direction: str, max_bounds: tuple[int, int] = inf_coords
) -> int:
    if direction == "up":
        return m
    elif direction == "down":
        return max_bounds[0] - m
    elif direction == "left":
        return n
    elif direction == "right":
        return max_bounds[1] - n
    else:
        raise ValueError(f"Unknown direction {direction}")


TC = TypeVar("TC")


def max_bounds_closure(func: TC, matrix: list[list[Any]]) -> TC:
    max_bounds = (len(matrix) - 1, len(matrix[0]) - 1)
    return partial(func, max_bounds=max_bounds)


HT = TypeVar("HT", bound=Hashable)


def bfs(graph: dict[HT, dict[HT, int]], source: HT) -> dict[HT, HT]:
    queue = deque([source])
    prev = {source: None}

    while queue:
        u = queue.popleft()
        for vertex, val in graph[u].items():
            if vertex not in prev:
                queue.append(vertex)
                prev[vertex] = u
    return prev


def dijkstra(
    graph: dict[HT, dict[HT, int]], source: HT
) -> tuple[dict[HT, int], dict[HT, HT]]:
    dist = {source: 0}
    prev = {source: None}
    pq = [(0, source)]
    while pq:
        _, u = heapq.heappop(pq)
        for vertex, val in graph[u].items():
            if vertex not in dist or dist[u] + val < dist[vertex]:
                dist[vertex] = dist[u] + val
                prev[vertex] = u
                heapq.heappush(pq, (dist[vertex], vertex))
    return dist, prev


def a_star(
    graph: dict[HT, dict[HT, int]],
    source: HT,
    target: HT,
    heuristic: Callable[[HT, HT], int],
) -> tuple[dict[HT, int], dict[HT, HT]]:
    """
    A* algorithm implementation.

    heuristic function must be admissible (never overestimate the distance to the goal).
    https://en.wikipedia.org/wiki/A*_search_algorithm#Admissibility
    for example, Manhattan distance is admissible.
    >>> def heuristic(candidate, target):
    ...     (x1, y1) = candidate
    ...     (x2, y2) = target
    ...     return abs(x1 - x2) + abs(y1 - y2)

    :param graph: graph in format {vertex: {neighbor: cost}}
    :param source: source vertex
    :param target: target vertex
    :param heuristic: heuristic function
    :return: tuple of distance and previous vertex
    """
    dist = {source: 0}
    prev = {source: None}
    pq = [(0, source)]

    while pq:
        _, current = heapq.heappop(pq)

        if current == target:
            break

        for vertex, val in graph[current].items():
            new_cost = dist[current] + val
            if vertex not in dist or new_cost < dist[vertex]:
                dist[vertex] = new_cost
                priority = new_cost + heuristic(vertex, target)
                heapq.heappush(pq, (priority, vertex))
                prev[vertex] = current

    return dist, prev

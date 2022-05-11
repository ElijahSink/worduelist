import time
from collections import defaultdict
from typing import DefaultDict, NamedTuple, Optional

"""
A solution to this problem will be a list of tuples, 
indicating the optimal sequence of swaps to make 
`puzzle` look like `solution`.
For example, it could be: 
[(1, 20), (7, 4), (9, 21), (19, 5), (2, 3), (12, 15), (8, 17), (15, 16), (4, 6), (13, 5)]
"""


class Swap(NamedTuple):
    src: int  # [0-sz]
    dest: int  # [0-sz]


class ScoredSwap(NamedTuple):
    src: int  # [0-sz]
    dest: int  # [0-sz]
    double: bool  # whether this swap is doubly productive

    def scoreless(self) -> Swap:
        return Swap(self.src, self.dest)


class WaffleSolver:
    correct_pos_map: DefaultDict[str, list[int]]
    puzzle: str
    solution: str
    max_swaps: int
    max_time: float
    start_time: float

    def __init__(
        self, puzzle: str, solution: str, max_swaps: int, max_time: float
    ) -> None:
        self.puzzle = puzzle
        self.solution = solution
        self.max_swaps = max_swaps
        self.max_time = max_time
        assert sorted(puzzle) == sorted(solution)

        self.correct_pos_map = defaultdict(list)
        for i, c in enumerate(solution):
            self.correct_pos_map[c].append(i)

    def get_best_swap_for_pos(self, pos_a: int) -> ScoredSwap:
        """
        given a position in puzzle, suggest where it ought to be swapped to
        if it's already in the correct position, return -1
        if this swap is doubly productive, return True, otherwise False
        """
        best_pos = -1
        for pos_b in self.correct_pos_map[self.puzzle[pos_a]]:
            # so we have a possible spot where the letter should go

            # let's ensure that this location isn't already populated
            # by the correct letter (if there are two of the same letter)
            if self.puzzle[pos_b] != self.solution[pos_b]:

                # let's check if this swap is doubly productive
                if self.puzzle[pos_b] == self.solution[pos_a]:
                    return ScoredSwap(pos_a, pos_b, True)  # doubly productive! do it

                best_pos = pos_b  # don't return immediately because there could be a better solution later

        return ScoredSwap(pos_a, best_pos, False)

    def puzzle_is_solved(self) -> bool:
        return self.puzzle == self.solution

    def get_incorrect_positions(self) -> tuple[int]:
        """
        all the indexes where puzzle[i] != solution[i]
        """
        incorrect = tuple(
            filter(
                lambda i: self.puzzle[i] != self.solution[i], range(len(self.puzzle))
            )
        )
        return incorrect

    def perform_swap(self, swap: Swap) -> None:
        a, b = sorted(swap)

        p = self.puzzle
        self.puzzle = p[:a] + p[b] + p[a + 1 : b] + p[a] + p[b + 1 :]

    def time_expired(self) -> bool:
        return time.time() - self.start_time > self.max_time

    def __solve(self, swaps_so_far: list[Swap] = []) -> Optional[list[Swap]]:
        print(swaps_so_far)
        if self.puzzle_is_solved():
            return swaps_so_far

        if len(swaps_so_far) >= self.max_swaps or self.time_expired():
            return None

        current_puzzle = self.puzzle[:]  # to restore after mutations

        possible_swaps = sorted(
            filter(
                lambda swap: swap.dest != -1,
                (
                    self.get_best_swap_for_pos(pos)
                    for pos in self.get_incorrect_positions()
                ),
            ),
            key=lambda swap: swap.double,
            reverse=True,
        )

        for scored_swap in possible_swaps:
            swap = scored_swap.scoreless()
            self.perform_swap(swap)
            solution_path = self.__solve(swaps_so_far + [swap])
            self.puzzle = current_puzzle
            if solution_path:
                return solution_path

    def solve(self):
        self.start_time = time.time()
        solution = self.__solve()
        print(f"Elapsed time: {time.time() - self.start_time}")
        return solution


def list_solution(sol: list[Swap]) -> str:
    return "\n".join([f"Swap {swap.src} with {swap.dest}" for swap in sol])


if __name__ == "__main__":
    puzzle = "FKOLYANIHSNANCIJTIUOT"
    solution = "FUNKYLIAIONICNJHTOAST"
    puzzle = "WEURLAENGLNINREUGOHWE"
    solution = "WHEELRNAOWNERNUGGUILE"
    puzzle = "TAENERGTREPERPSERSDMXIARETALERMNVSCSREVD"
    solution = "PRETENDRXLIEMPRESSMRVCAVERAGEDSTREASTERN"
    puzzle = "CEYASPEMLDPHORURSEUAP"
    solution = "CAMPSUAYROPERDLUSHEEP"

    solver = WaffleSolver(puzzle, solution, 10, 20)
    solution = solver.solve()
    if solution:
        print(f"Solution in {len(solution)} swaps!")
        print(list_solution(solution))
    else:
        print("No solution :(")

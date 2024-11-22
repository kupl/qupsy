from queue import PriorityQueue

from qupsy.language import Pgm


class Worklist:
    def __init__(self) -> None:
        self.current_set: PriorityQueue[tuple[int, int, Pgm]] = PriorityQueue()
        self.overall_set: list[Pgm] = []

    def put(self, *pgms: Pgm) -> None:
        for pgm in pgms:
            if pgm not in self.overall_set:
                self.current_set.put((pgm.cost, pgm.depth, pgm))
                self.overall_set.append(pgm)

    def get(self) -> Pgm:
        return self.current_set.get_nowait()[2]

    def show_set(self) -> None:
        print(self.overall_set)

    def show_pq(self) -> None:
        print(self.current_set.queue)

    def notEmpty(self) -> bool:
        return not self.current_set.empty()

    def num_pgm_left(self) -> int:
        return self.current_set.qsize()

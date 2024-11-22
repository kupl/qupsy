from queue import PriorityQueue

from qupsy.language import Pgm


class Worklist:
    def __init__(self) -> None:
        self.current_set: PriorityQueue[tuple[int, int, Pgm]] = PriorityQueue()
        self.overall_set: list[Pgm] = []

    def put(self, enqueue: list[Pgm]) -> None:
        for element in enqueue:
            if element not in self.overall_set:
                self.current_set.put((element.cost, element.depth, element))
                self.overall_set.append(element)

    def get(self) -> Pgm:
        return self.current_set.get_nowait()[2]

    def show_set(self) -> None:
        print(self.overall_set)

    def show_pq(self) -> None:
        print(self.current_set.queue)

    def notEmpty(self) -> bool:
        return not self.current_set.empty()

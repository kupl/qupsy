from synthesizer.language import Pgm
from queue import PriorityQueue


class Worklist:
    def __init__(self):
        self.current_set = PriorityQueue()
        self.count = 0
        self.overall_set = []

    def put(self, enqueue):
        for element in enqueue:
            if element not in self.overall_set:
                self.count += 1
                self.current_set.put((element.cost, element.depth, self.count, element))
                self.overall_set.append(element)

    def get(self) -> Pgm:
        return self.current_set.get_nowait()[-1]

    def show_set(self):
        print(self.overall_set)

    def show_pq(self):
        print(self.current_set.queue)

    def notEmpty(self) -> bool:
        return self.current_set.not_empty

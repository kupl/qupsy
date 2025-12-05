import copy, time

from synthesizer.language import Pgm, C_hole, Ry, CRy
from synthesizer.worklist import Worklist
from synthesizer.prune import prune_basic
from synthesizer.setup import get_spec, verify
from synthesizer.transition import next, fill_theta

def search_base(filename: str) -> Pgm:
    worklist = Worklist()
    worklist.put([Pgm(C_hole())])
    gates, specification = get_spec(filename)
    loop = 0
    complete = 0
    start = time.time()
    try:
        while worklist.notEmpty() and time.time() - start < 3600:
            loop += 1
            target = worklist.get()
            spec = copy.deepcopy(specification)
            solution = [False] * len(spec)
            if not prune_basic(target):
                for i in range(len(spec)):
                    if target.terminal():
                        complete += 1
                        if target.has_syntax(Ry()) or target.has_syntax(CRy()):
                            for prog in fill_theta(spec[i].n, target, 0):
                                target = prog
                                if verify(target, spec[i]):
                                    solution[i] = True
                                    print(f"Solution matches {i+1}th spec: {prog}")
                                    break
                            if all(solution):
                                print(f"loop: {loop}")
                                print(f"worklist size: {worklist.current_set.qsize()}")
                                return target
                        if verify(target, spec[i]):
                            solution[i] = True
                            print(f"Solution matches {i+1}th spec: {target}")
                        else:
                            break
                        if all(solution):
                            print(f"loop: {loop}")
                            print(f"worklist size: {worklist.current_set.qsize()}")
                            return target
                    else:
                        for i in next(target, spec[i].n, spec[i].bits, gates):
                            worklist.put([i])
                        break
        raise Exception(f"Worklist empty or timeout. Loop: {loop}")
    except Exception as e:
        print(f"exception loop {loop}:{target}\n" + "\033[95m" + f"{str(target)}" + "\033[0m" + "\n-------------------")
        print(f"worklist size: {worklist.current_set.qsize()}")
        raise e

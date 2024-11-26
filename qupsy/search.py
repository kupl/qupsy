from qupsy.language import Pgm
from qupsy.spec import Spec
from qupsy.transition import next
from qupsy.utils import logger
from qupsy.verify import verify
from qupsy.worklist import Worklist


def search(spec: Spec, *, initial_pgm: Pgm | None = None, n: str = "n") -> Pgm:
    worklist = Worklist()
    worklist.put(initial_pgm or Pgm(n))
    while worklist.notEmpty():
        current_pgm = worklist.get()
        logger.debug(f"Current program: {current_pgm}")
        verified: list[bool] = []
        for testcase in spec.testcases:
            if current_pgm.terminated:
                if verify(testcase, current_pgm):
                    verified.append(True)
                    if len(verified) == len(spec.testcases):
                        return current_pgm
                else:
                    break
            else:
                worklist.put(*next(current_pgm, spec.gates))
    raise ValueError("No solution found")

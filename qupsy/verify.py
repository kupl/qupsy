import cirq
import numpy as np
import numpy.typing as npt

from qupsy.language import Pgm


def verify(testcase: tuple[npt.ArrayLike, npt.ArrayLike], pgm: Pgm) -> bool:
    input, output = testcase
    assert isinstance(input, np.ndarray)
    assert isinstance(output, np.ndarray)
    n = int(np.log2(input.size))
    pgm_qc = pgm(n)
    pgm_sv = cirq.final_state_vector(pgm_qc, initial_state=input, qubit_order=cirq.LineQubit.range(n))  # type: ignore
    return cirq.linalg.allclose_up_to_global_phase(output, pgm_sv)  # type: ignore

import cirq, json, numpy as np
from typing import List
from synthesizer.language import *


@dataclass
class Spec:
    n: int
    bits: List[str]
    input: np.ndarray
    output: np.ndarray


class Property:
    pass

class Basis:
    pass

def get_spec(filename: str):
    spec = []
    with open(filename, "r") as file:
        data = json.load(file)
    gates = (
        data["gates"]
        if "gates" in data
        else ["H", "X", "Y", "Z", "S", "CX", "Ry", "CRy"]
    )
    for i in data["examples"]:
        n = int(data["examples"][i]["qubit"])
        bits = (
            data["examples"][i]["bit"].split(", ")
            if "bit" in data["examples"][i]
            else ""
        )
        out_sv = np.fromstring(data["examples"][i]["output"], dtype="complex", sep=",")
        if "input" in data["examples"][i]:
            in_sv = data["examples"][i]["input"]
        else:
            in_sv = "1," + "0," * (2**n - 1)  # default input |0...0>
        spec.append(
            Spec(
                n,
                bits,
                in_sv,
                out_sv,
            )
        )
    return gates, spec


def get_pgm_args(n: int, bits: str) -> str:
    if len(bits) == 0:
        function = f"def pgm(n):\n"
        execution_inst = f"pgm({n})"
        return function, execution_inst
    elif len(bits) == 1:
        function = f"def pgm(n, bit):\n"
        execution_inst = f"pgm({n}, {[bool(int(i)) for i in bits[0]]})"
        return function, execution_inst
    else:
        print(f"Warning : number of bits {bits} is not handled")
        return None


def execute_string(target: Pgm, input: str, n: int, bits: str):
    libraries = "import math, numpy, cirq\n\n"
    set_parameter, call_pgm = get_pgm_args(n, bits)
    input = f"input = [{input}]"
    qbits = "qbits = cirq.LineQubit.range(n)"
    init_qc = "qc = cirq.Circuit()"
    program = str(target)
    return_val = (
        "return cirq.final_state_vector(qc, initial_state=input, qubit_order=qbits)"
    )
    code = (
        libraries
        + set_parameter
        + indent(input, TAB)
        + "\n"
        + indent(init_qc, TAB)
        + "\n"
        + indent(qbits, TAB)
        + "\n"
        + indent(program, TAB)
        + "\n"
        + indent(return_val, TAB)
    )
    # print(code)
    exec(code, globals())
    try:
        res = eval(call_pgm)
    except Exception as e:
        # print(f"Error: {e}")
        # print(str(target))
        # print("-------------------")
        return None
    return res


def verify(target: Pgm, spec: Spec) -> bool:
    input, output, n, bits = spec.input, spec.output, spec.n, spec.bits
    res = execute_string(target, input, n, bits)
    if not isinstance(res, np.ndarray):
        return False
    return cirq.linalg.allclose_up_to_global_phase(res, output)

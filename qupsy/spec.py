import json
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import numpy as np
import numpy.typing as npt

from qupsy.language import CX, CRy, Gate, H, Ry, X
from qupsy.utils import logger

GATE_MAP: dict[str, type[Gate]] = {
    "H": H,
    "X": X,
    "Ry": Ry,
    "CX": CX,
    "CRy": CRy,
}


@dataclass
class Spec:
    gates: list[type[Gate]]
    testcases: list[tuple[npt.ArrayLike, npt.ArrayLike]]

    def __str__(self) -> str:
        testcases_string: list[str] = []
        for input, output in self.testcases:
            input_str = str(input).splitlines()
            input_str = input_str[0] + " ...]" if len(input_str) > 1 else input_str[0]
            output_str = str(output).splitlines()
            output_str = output_str[0] + " ...]" if len(output_str) > 1 else output_str[0]

            testcases_string.append(f"        ( Input: {input_str},\n         Output: {output_str}),")
        return f"""Spec(
    gates: [{", ".join(map(lambda g: g.__name__, self.gates))}],
    testcases: [
{"\n".join(testcases_string)}
    ],
)"""


def parse_spec(spec: Path | str) -> Spec:
    if isinstance(spec, str):
        spec = Path(spec)
    data = json.loads(spec.read_text())
    gates = cast(list[str], data.get("gates", ["H", "X", "Ry", "CX", "CRy"]))
    gates = [GATE_MAP[gate] for gate in gates]

    testcases: list[tuple[npt.ArrayLike, npt.ArrayLike]] = []
    for tc in data["testcases"].values():
        output = np.fromstring(tc["output"], dtype="complex", sep=",")
        input = tc["input"] if "input" in tc else (np.concat([[1], np.zeros_like(output[1:])]))
        testcases.append((input, output))

        logger.debug("Parsed output: %s", output)
        logger.debug("Parsed input: %s", input)

    return Spec(gates, testcases)

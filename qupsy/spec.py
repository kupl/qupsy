import json
from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict

import numpy as np
import numpy.typing as npt

from qupsy.language import GATE_MAP, Gate


class Testcase(TypedDict):
    input: str | None
    output: str


class SpecData(TypedDict):
    gates: list[str] | None
    testcases: dict[str, Testcase]


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
            output_str = (
                output_str[0] + " ...]" if len(output_str) > 1 else output_str[0]
            )

            testcases_string.append(
                f"        ( Input: {input_str},\n         Output: {output_str}),"
            )
        return """Spec(
    gates: [{}],
    testcases: [
{}
    ],
)""".format(
            ", ".join(map(lambda g: g.__name__, self.gates)),
            "\n".join(testcases_string),
        )


def make_spec(data: SpecData) -> Spec:
    gates = data["gates"] or ["H", "X", "Ry", "CX", "CRy"]
    gates = [GATE_MAP[gate] for gate in gates]
    testcases: list[tuple[npt.ArrayLike, npt.ArrayLike]] = []
    for tc in data["testcases"].values():
        output = np.fromstring(tc["output"], dtype="complex", sep=",")
        input = tc["input"] or (np.concat([[1], np.zeros_like(output[1:])]))
        testcases.append((input, output))
        # logger.debug("Parsed output: %s", output)
        # logger.debug("Parsed input: %s", input)
    return Spec(gates, testcases)


def parse_spec(spec: Path | str) -> Spec:
    if isinstance(spec, str):
        spec = Path(spec)
    raw_data = json.loads(spec.read_text())
    data: SpecData = {"gates": None, "testcases": {}}
    data["gates"] = raw_data.get("gates", None)
    for k, v in raw_data["testcases"].items():
        data["testcases"][k] = {"input": v.get("input", None), "output": v["output"]}
    return make_spec(data)

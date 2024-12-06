import numpy as np

from qupsy.language import CX, H
from qupsy.spec import Spec, SpecData, make_spec


def test_parse_spec_from_raw_data():
    raw_spec: SpecData = {
        "gates": ["H", "CX"],
        "testcases": {
            "1": {
                "input": None,
                "output": "0.70710677,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.70710677",
            },
            "2": {
                "input": None,
                "output": "0.70710677, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.70710677",
            },
            "3": {"input": None, "output": "0.70710677,0,0,0,0,0,0,0.70710677"},
        },
    }
    spec = make_spec(raw_spec)
    assert spec.gates == [H, CX]
    assert len(spec.testcases) == 3
    for input, output in spec.testcases:
        assert isinstance(input, np.ndarray)
        assert isinstance(output, np.ndarray)
        input_size: int = np.log2(input.size)
        output_size: int = np.log2(output.size)
        assert input_size == output_size
        input_equal_to_one: int = 0
        for i in input:
            input_equal_to_one += np.abs(i) ** 2
        assert np.isclose(input_equal_to_one, 1)
        output_equal_to_one = 0
        for i in output:
            output_equal_to_one += np.abs(i) ** 2
        assert np.isclose(output_equal_to_one, 1)


def test_parse_spec_from_json_data():
    raw_spec: SpecData = {
        "gates": ["H", "CX"],
        "testcases": {
            "1": {
                "input": None,
                "output": "0.70710677,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.70710677",
            },
            "2": {
                "input": None,
                "output": "0.70710677, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.70710677",
            },
            "3": {"input": None, "output": "0.70710677,0,0,0,0,0,0,0.70710677"},
        },
    }
    spec = make_spec(raw_spec)
    assert spec.gates == [H, CX]
    assert len(spec.testcases) == 3
    assert isinstance(spec, Spec)

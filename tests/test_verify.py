from qupsy.language import CX, ForCmd, GateCmd, H, Integer, Pgm, SeqCmd, Var
from qupsy.spec import SpecData, make_spec
from qupsy.verify import verify


def test_verify():
    ghz = Pgm(
        "n",
        SeqCmd(
            GateCmd(H(Integer(0))),
            ForCmd("i0", Integer(1), Var("n"), GateCmd(CX(Integer(0), Var("i0")))),
        ),
    )
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
    testcases = spec.testcases
    for testcase in testcases:
        assert verify(testcase, ghz)

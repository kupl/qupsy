from qupsy.language import CX, ForCmd, GateCmd, H, Integer, Pgm, SeqCmd, Var
from qupsy.spec import parse_spec
from qupsy.verify import verify


def test_verify():
    ghz = Pgm(
        "n",
        SeqCmd(
            GateCmd(H(Integer(0))),
            ForCmd("i0", Integer(1), Var("n"), GateCmd(CX(Integer(0), Var("i0")))),
        ),
    )
    spec = parse_spec("benchmarks/ghz.json")
    testcases = spec.testcases
    for testcase in testcases:
        assert verify(testcase, ghz)

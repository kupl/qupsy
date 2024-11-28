from qupsy.language import CX, ForCmd, GateCmd, H, Integer, Pgm, SeqCmd, Var
from qupsy.parser import parse


def test_parser_ghz():
    pgm = """
def pgm(n):
    H(0)
    for i0 in range(1, n):
        CX(0, i0)
"""
    parsed = parse(pgm)
    assert parsed == Pgm(
        "n",
        SeqCmd(
            GateCmd(H(Integer(0))),
            ForCmd("i0", Integer(1), Var("n"), GateCmd(CX(Integer(0), Var("i0")))),
        ),
    )

from qupsy.language import (
    CX,
    Add,
    CRy,
    ForCmd,
    GateCmd,
    H,
    Integer,
    Pgm,
    SeqCmd,
    Sub,
    Var,
    X,
)
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


def test_parser_inc():
    pgm = """
def pgm(n):
    X(0)
    for i0 in range(0,(n - 1)):
        CRy(i0, (i0 + 1), 1, (n - i0))
        """.strip()

    parsed = parse(pgm)
    assert parsed == Pgm(
        "n",
        SeqCmd(
            GateCmd(X(Integer(0))),
            ForCmd(
                "i0",
                Integer(0),
                Sub(Var("n"), Integer(1)),
                GateCmd(
                    CRy(
                        Var("i0"),
                        Add(Var("i0"), Integer(1)),
                        Integer(1),
                        Sub(Var("n"), Var("i0")),
                    )
                ),
            ),
        ),
    )

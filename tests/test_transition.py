from qupsy.language import (
    ALL_AEXPS,
    ALL_GATES,
    CX,
    Add,
    Aexp,
    Cmd,
    ForCmd,
    Gate,
    GateCmd,
    H,
    HoleAexp,
    Integer,
    Pgm,
    SeqCmd,
    Var,
)
from qupsy.transition import next


def test_hole_cmd_len():
    pgm = Pgm("n")
    nexts = next(pgm)
    assert len(nexts) == 3


def test_hole_cmd():
    pgm = Pgm("n")
    command_types: list[type[Cmd]] = [SeqCmd, ForCmd, GateCmd]
    for pgm in next(pgm):
        assert type(pgm.body) in command_types
        command_types.remove(type(pgm.body))
    assert len(command_types) == 0


def tests_hole_gate():
    pgm = Pgm("n", GateCmd())
    gate_types: list[type[Gate]] = ALL_GATES.copy()
    for pgm in next(pgm):
        assert isinstance(pgm.body, GateCmd)
        assert type(pgm.body.gate) in gate_types
        gate_types.remove(type(pgm.body.gate))
    assert len(gate_types) == 1


def test_hole_aexp1():
    pgm = Pgm("n", GateCmd(H()))
    aexp_types: list[type[Aexp]] = ALL_AEXPS.copy()
    pgms = next(pgm)
    for pgm in pgms:
        assert isinstance(pgm.body, GateCmd)
        assert isinstance(pgm.body.gate, H)
        assert type(pgm.body.gate.qreg) in aexp_types
        if type(pgm.body.gate.qreg) not in [Integer, Var]:
            aexp_types.remove(type(pgm.body.gate.qreg))
    assert len(aexp_types) == 3


def test_hole_aexp2():
    pgm = Pgm("n", GateCmd(CX()))
    aexp_types: list[type[Aexp]] = ALL_AEXPS.copy()
    pgms = next(pgm)
    for pgm in pgms:
        assert isinstance(pgm.body, GateCmd)
        assert isinstance(pgm.body.gate, CX)
        assert type(pgm.body.gate.qreg1) in aexp_types
        if type(pgm.body.gate.qreg1) not in [Integer, Var]:
            aexp_types.remove(type(pgm.body.gate.qreg1))
    assert len(aexp_types) == 3


def test_hole_aexp3():
    pgm = Pgm("n", GateCmd(CX(Integer(0))))
    aexp_types: list[type[Aexp]] = ALL_AEXPS.copy()
    pgms = next(pgm)
    for pgm in pgms:
        assert isinstance(pgm.body, GateCmd)
        assert isinstance(pgm.body.gate, CX)
        assert type(pgm.body.gate.qreg2) in aexp_types
        if type(pgm.body.gate.qreg2) not in [Integer, Var]:
            aexp_types.remove(type(pgm.body.gate.qreg2))
    assert len(aexp_types) == 3


def test_next_aexp():
    pgm = Pgm("n", GateCmd(CX(Integer(0), Add())))
    aexp_types: list[type[Aexp]] = ALL_AEXPS.copy()
    pgms = next(pgm)
    for pgm in pgms:
        assert isinstance(pgm.body, GateCmd)
        assert isinstance(pgm.body.gate, CX)
        assert isinstance(pgm.body.gate.qreg2, Add)
        assert type(pgm.body.gate.qreg2.a) in aexp_types
        if type(pgm.body.gate.qreg2.a) not in [Integer, Var]:
            aexp_types.remove(type(pgm.body.gate.qreg2.a))
        assert isinstance(pgm.body.gate.qreg2.b, HoleAexp)
    assert len(aexp_types) == 3


def test_ghz_next():
    pgm0 = Pgm("n")
    pgm1 = Pgm("n", SeqCmd())
    pgm2 = Pgm("n", SeqCmd(GateCmd()))
    pgm3 = Pgm("n", SeqCmd(GateCmd(H())))
    pgm4 = Pgm("n", SeqCmd(GateCmd(H(Integer(0)))))
    pgm5 = Pgm("n", SeqCmd(GateCmd(H(Integer(0))), ForCmd("i0")))
    pgm6 = Pgm("n", SeqCmd(GateCmd(H(Integer(0))), ForCmd("i0", Integer(1))))
    pgm7 = Pgm("n", SeqCmd(GateCmd(H(Integer(0))), ForCmd("i0", Integer(1), Var("n"))))
    pgm8 = Pgm(
        "n",
        SeqCmd(GateCmd(H(Integer(0))), ForCmd("i0", Integer(1), Var("n"), GateCmd())),
    )
    pgm9 = Pgm(
        "n",
        SeqCmd(
            GateCmd(H(Integer(0))),
            ForCmd("i0", Integer(1), Var("n"), GateCmd(CX())),
        ),
    )
    pgm10 = Pgm(
        "n",
        SeqCmd(
            GateCmd(H(Integer(0))),
            ForCmd("i0", Integer(1), Var("n"), GateCmd(CX(Integer(0)))),
        ),
    )
    pgm11 = Pgm(
        "n",
        SeqCmd(
            GateCmd(H(Integer(0))),
            ForCmd("i0", Integer(1), Var("n"), GateCmd(CX(Integer(0), Var("i0")))),
        ),
    )
    assert pgm1 in next(pgm0)
    assert pgm2 in next(pgm1)
    assert pgm3 in next(pgm2)
    assert pgm4 in next(pgm3)
    assert pgm5 in next(pgm4)
    assert pgm6 in next(pgm5)
    assert pgm7 in next(pgm6)
    assert pgm8 in next(pgm7)
    assert pgm9 in next(pgm8)
    assert pgm10 in next(pgm9)
    assert pgm11 in next(pgm10)
    assert (
        str(pgm11)
        == """
def pgm(n):
    H(0)
    for i0 in range(1,n):
        CX(0, i0)
    """.strip()
    )

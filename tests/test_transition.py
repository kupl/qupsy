from qupsy.language import (
    ALL_AEXPS,
    ALL_GATES,
    CX,
    Aexp,
    Cmd,
    ForCmd,
    Gate,
    GateCmd,
    H,
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

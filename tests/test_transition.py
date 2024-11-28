from qupsy.language import (
    ALL_AEXPS,
    ALL_GATES,
    CX,
    Add,
    Aexp,
    Cmd,
    CRy,
    ForCmd,
    Gate,
    GateCmd,
    H,
    HoleAexp,
    Integer,
    Pgm,
    SeqCmd,
    Sub,
    Var,
    X,
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


def test_inc_next():
    pgm0 = Pgm("n")
    pgm1 = Pgm("n", SeqCmd())
    pgm2 = Pgm("n", SeqCmd(GateCmd()))
    pgm3 = Pgm("n", SeqCmd(GateCmd(X())))
    pgm4 = Pgm("n", SeqCmd(GateCmd(X(Integer(0)))))
    pgm5 = Pgm("n", SeqCmd(GateCmd(X(Integer(0))), ForCmd("i0")))
    pgm6 = Pgm("n", SeqCmd(GateCmd(X(Integer(0))), ForCmd("i0", Integer(0))))
    pgm7 = Pgm("n", SeqCmd(GateCmd(X(Integer(0))), ForCmd("i0", Integer(0), Sub())))
    pgm8 = Pgm(
        "n",
        SeqCmd(GateCmd(X(Integer(0))), ForCmd("i0", Integer(0), Sub(Var("n")))),
    )
    pgm9 = Pgm(
        "n",
        SeqCmd(
            GateCmd(X(Integer(0))), ForCmd("i0", Integer(0), Sub(Var("n"), Integer(1)))
        ),
    )
    pgm10 = Pgm(
        "n",
        SeqCmd(
            GateCmd(X(Integer(0))),
            ForCmd("i0", Integer(0), Sub(Var("n"), Integer(1)), GateCmd()),
        ),
    )
    pgm11 = Pgm(
        "n",
        SeqCmd(
            GateCmd(X(Integer(0))),
            ForCmd("i0", Integer(0), Sub(Var("n"), Integer(1)), GateCmd(CRy())),
        ),
    )
    pgm12 = Pgm(
        "n",
        SeqCmd(
            GateCmd(X(Integer(0))),
            ForCmd(
                "i0",
                Integer(0),
                Sub(Var("n"), Integer(1)),
                GateCmd(CRy(Var("i0"))),
            ),
        ),
    )
    pgm13 = Pgm(
        "n",
        SeqCmd(
            GateCmd(X(Integer(0))),
            ForCmd(
                "i0",
                Integer(0),
                Sub(Var("n"), Integer(1)),
                GateCmd(CRy(Var("i0"), Add())),
            ),
        ),
    )
    pgm14 = Pgm(
        "n",
        SeqCmd(
            GateCmd(X(Integer(0))),
            ForCmd(
                "i0",
                Integer(0),
                Sub(Var("n"), Integer(1)),
                GateCmd(
                    CRy(Var("i0"), Add(Var("i0"))),
                ),
            ),
        ),
    )
    pgm15 = Pgm(
        "n",
        SeqCmd(
            GateCmd(X(Integer(0))),
            ForCmd(
                "i0",
                Integer(0),
                Sub(Var("n"), Integer(1)),
                GateCmd(
                    CRy(Var("i0"), Add(Var("i0"), Integer(1))),
                ),
            ),
        ),
    )
    pgm16 = Pgm(
        "n",
        SeqCmd(
            GateCmd(X(Integer(0))),
            ForCmd(
                "i0",
                Integer(0),
                Sub(Var("n"), Integer(1)),
                GateCmd(
                    CRy(Var("i0"), Add(Var("i0"), Integer(1)), Integer(1)),
                ),
            ),
        ),
    )
    pgm17 = Pgm(
        "n",
        SeqCmd(
            GateCmd(X(Integer(0))),
            ForCmd(
                "i0",
                Integer(0),
                Sub(Var("n"), Integer(1)),
                GateCmd(
                    CRy(Var("i0"), Add(Var("i0"), Integer(1)), Integer(1), Sub()),
                ),
            ),
        ),
    )
    pgm18 = Pgm(
        "n",
        SeqCmd(
            GateCmd(X(Integer(0))),
            ForCmd(
                "i0",
                Integer(0),
                Sub(Var("n"), Integer(1)),
                GateCmd(
                    CRy(
                        Var("i0"), Add(Var("i0"), Integer(1)), Integer(1), Sub(Var("n"))
                    ),
                ),
            ),
        ),
    )
    pgm19 = Pgm(
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
                    ),
                ),
            ),
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
    assert pgm12 in next(pgm11)
    assert pgm13 in next(pgm12)
    assert pgm14 in next(pgm13)
    assert pgm15 in next(pgm14)
    assert pgm16 in next(pgm15)
    assert pgm17 in next(pgm16)
    assert pgm18 in next(pgm17)
    assert pgm19 in next(pgm18)
    assert (
        str(pgm19)
        == """
def pgm(n):
    X(0)
    for i0 in range(0,(n - 1)):
        CRy(i0, (i0 + 1), 1, (n - i0))
        """.strip()
    )

from qupsy.language import ALL_GATES, Cmd, ForCmd, Gate, GateCmd, Pgm, SeqCmd
from qupsy.transition import next


def test_hole_command_becomes_three_different_commands():
    pgm = Pgm("n")
    nexts = next(pgm)
    assert len(nexts) == 3


def test_transition_holecmd():
    pgm = Pgm("n")
    command_types: list[type[Cmd]] = [SeqCmd, ForCmd, GateCmd]
    for pgm in next(pgm):
        assert type(pgm.body) in command_types
        command_types.remove(type(pgm.body))
    assert len(command_types) == 0


def test_transition_gatecmd():
    pgm = Pgm("n", GateCmd())
    gate_types: list[type[Gate]] = ALL_GATES
    for pgm in next(pgm):
        assert isinstance(pgm.body, GateCmd)
        assert type(pgm.body.gate) in gate_types
        gate_types.remove(type(pgm.body.gate))
    assert len(gate_types) == 1

from qupsy.language import GateCmd, H, HoleAexp, HoleCmd, HoleGate, Pgm, SeqCmd, X
from qupsy.worklist import Worklist


def test_worklist():
    worklist = Worklist()
    assert not worklist.notEmpty()


def test_add_same_pgm():
    worklist = Worklist()
    pgm = Pgm(HoleCmd())
    worklist.put(pgm, pgm)
    assert worklist.num_pgm_left() == 1


def test_get_pgm():
    worklist = Worklist()
    pgm1 = Pgm(HoleCmd())
    pgm2 = Pgm(GateCmd(HoleGate()))
    worklist.put(pgm1, pgm2)
    assert worklist.get() == pgm2


def test_add_same_cost():
    worklist = Worklist()
    pgm1 = Pgm(SeqCmd(GateCmd(H(HoleAexp())), GateCmd(H(HoleAexp()))))
    pgm2 = Pgm(SeqCmd(GateCmd(X(HoleAexp())), GateCmd(X(HoleAexp()))))
    worklist.put(pgm1, pgm2)
    assert worklist.get() == pgm1

from qupsy.language import GateCmd, H, HoleAexp, HoleCmd, HoleGate, Pgm, SeqCmd, X
from qupsy.worklist import Worklist


def test_worklist():
    worklist = Worklist()
    assert not worklist.notEmpty()


def test_add_same_pgm():
    worklist = Worklist()
    pgm = Pgm("n", HoleCmd())
    worklist.put(pgm, pgm)
    assert worklist.num_pgm_left() == 1


def test_get_pgm():
    worklist = Worklist()
    pgm1 = Pgm("n", HoleCmd())
    pgm2 = Pgm("n", GateCmd(HoleGate()))
    worklist.put(pgm1, pgm2)
    assert worklist.get() == pgm2


def test_add_same_cost():
    worklist = Worklist()
    pgm1 = Pgm("n", SeqCmd(GateCmd(H(HoleAexp())), GateCmd(H(HoleAexp()))))
    pgm2 = Pgm("n", SeqCmd(GateCmd(X(HoleAexp())), GateCmd(X(HoleAexp()))))
    worklist.put(pgm1, pgm2)
    assert worklist.get() == pgm1

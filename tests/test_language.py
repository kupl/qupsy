from qupsy.language import Div, GateCmd, HoleCmd, Integer, Mul, Pgm, Ry, SeqCmd


def test_pgm():
    pgm = Pgm("n")
    assert isinstance(pgm.body, HoleCmd)


def test_seq_cmd():
    seq = SeqCmd()
    assert isinstance(seq.pre, HoleCmd)
    assert isinstance(seq.post, HoleCmd)


def test_str():
    pgm = GateCmd(Ry(Integer(0), Integer(1), Integer(3)))
    assert str(pgm) == "Ry(0, 1, 3)"


def test_cost0():
    pgm = Pgm("n")
    assert pgm.cost == pgm.body.cost


def test_cost1():
    pgm = Pgm("n", GateCmd(Ry(Integer(0), Integer(1), Integer(3))))
    assert pgm.cost == 2


def test_depth():
    pgm = Pgm("n")
    assert pgm.depth == pgm.body.depth


def test_children():
    pgm = Div(Integer(2), Integer(3))
    children = pgm.children
    assert children == [Integer(2), Integer(3)]


def test_terminated():
    pgm = Pgm("n")
    assert pgm.terminated == False


def test_call():
    pgm = Mul(Integer(2), Integer(3))
    res = pgm.__call__({"n": 5})
    assert res == 6

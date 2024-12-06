from qupsy.language import GateCmd, HoleCmd, Integer, Pgm, Ry, SeqCmd


def test_pgm_create_with_empty_body():
    pgm = Pgm("n")
    assert isinstance(pgm.body, HoleCmd)


def test_pgm_cost0():
    pgm = Pgm("n")
    assert pgm.cost == pgm.body.cost


def test_pgm_cost1():
    pgm = Pgm("n", GateCmd(Ry(Integer(0), Integer(1), Integer(3))))
    assert pgm.cost == 2


def test_pgm_depth():
    pgm = Pgm("n")
    assert pgm.depth == pgm.body.depth


def test_seq_cmd_wo_pre_and_post():
    seq = SeqCmd()
    assert isinstance(seq.pre, HoleCmd)
    assert isinstance(seq.post, HoleCmd)

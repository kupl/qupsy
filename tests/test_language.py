from qupsy.language import HoleCmd, Pgm, SeqCmd


def test_pgm_create_with_empty_body():
    pgm = Pgm()
    assert isinstance(pgm.body, HoleCmd)


def test_pgm_to_str():
    pgm = Pgm()
    assert str(pgm) == str(pgm.body)


def test_pgm_cost():
    pgm = Pgm()
    assert pgm.cost == pgm.body.cost


def test_pgm_depth():
    pgm = Pgm()
    assert pgm.depth == pgm.body.depth


def test_seq_cmd_wo_pre_and_post():
    seq = SeqCmd()
    assert isinstance(seq.pre, HoleCmd)
    assert isinstance(seq.post, HoleCmd)

from pathlib import Path

from qupsy.language import CX, ForCmd, GateCmd, H, Integer, Pgm, SeqCmd, Var
from qupsy.search import search
from qupsy.spec import parse_spec

DATA_DIR = Path(__file__).parent / "data"


def test_search_ghz_last_step():
    init_pgm = Pgm(
        "n",
        SeqCmd(
            GateCmd(H(Integer(0))),
            ForCmd("i0", Integer(1), Var("n"), GateCmd(CX(Integer(0)))),
        ),
    )
    final_pgm = Pgm(
        "n",
        SeqCmd(
            GateCmd(H(Integer(0))),
            ForCmd("i0", Integer(1), Var("n"), GateCmd(CX(Integer(0), Var("i0")))),
        ),
    )
    spec = parse_spec(DATA_DIR / "ghz.json")
    synthesized_pgm = search(spec, initial_pgm=init_pgm)
    assert synthesized_pgm == final_pgm

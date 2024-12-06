from qupsy.language import CX, ForCmd, GateCmd, H, Integer, Pgm, SeqCmd, Var
from qupsy.search import search
from qupsy.spec import make_spec, SpecData


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
    raw_spec: SpecData = {
        "gates": ["H", "CX"],
        "testcases": {
            "1": {
                "input": None,
                "output": "0.70710677,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.70710677",
            },
            "2": {
                "input": None,
                "output": "0.70710677, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.70710677",
            },
            "3": {"input": None, "output": "0.70710677,0,0,0,0,0,0,0.70710677"},
        },
    }
    spec = make_spec(raw_spec)
    synthesized_pgm = search(spec, initial_pgm=init_pgm)
    assert synthesized_pgm == final_pgm


def test_search_ghz_second_last_step():
    init_pgm = Pgm(
        "n",
        SeqCmd(
            GateCmd(H(Integer(0))),
            ForCmd("i0", Integer(1), Var("n"), GateCmd(CX())),
        ),
    )
    final_pgm = Pgm(
        "n",
        SeqCmd(
            GateCmd(H(Integer(0))),
            ForCmd("i0", Integer(1), Var("n"), GateCmd(CX(Integer(0), Var("i0")))),
        ),
    )
    raw_spec: SpecData = {
        "gates": ["H", "CX"],
        "testcases": {
            "1": {
                "input": None,
                "output": "0.70710677,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.70710677",
            },
            "2": {
                "input": None,
                "output": "0.70710677, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.70710677",
            },
            "3": {"input": None, "output": "0.70710677,0,0,0,0,0,0,0.70710677"},
        },
    }
    spec = make_spec(raw_spec)
    synthesized_pgm = search(spec, initial_pgm=init_pgm)
    assert synthesized_pgm == final_pgm

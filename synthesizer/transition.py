from typing import List, Union, Dict
import sympy as sp
import itertools

from synthesizer.language import *

loop_vars = [I(), J()]
sym_n = sp.symbols("n")
sym_i = sp.symbols("i")
sym_j = sp.symbols("j")


def fill_hole(
    target: Hole, bits: List[List[bool]], gates: List[str], loop_depth: int
) -> List[Pgm]:

    def inst_hole():
        insts = [
            G_hole(),
            Seq(C_hole(), C_hole()),
            If(Bit(loop_vars[loop_depth - 1]), C_hole(), Skip()),
        ]
        # 1 is the maximum loop depth
        if loop_depth < 3:
            insts.append(For(loop_vars[loop_depth], Integer(0), A_hole(), C_hole()))
            insts.append(For(loop_vars[loop_depth], Integer(1), A_hole(), C_hole()))
        return insts

    def gate_hole():
        possible_gates = []
        if "H" in gates:
            possible_gates.append(H(A_hole()))
        if "X" in gates:
            possible_gates.append(X(A_hole()))
        if "Ry" in gates:
            possible_gates.append(Ry(None, None, A_hole()))
        if "CX" in gates:
            possible_gates.append(CX(A_hole(), A_hole()))
        if "CRy" in gates:
            possible_gates.append(CRy(None, None, A_hole(), A_hole()))
        return possible_gates

    def aexp_hole():
        return [
            V_hole(),
            Z_hole(),
            Add(A_hole(), A_hole()),
            Sub(A_hole(), A_hole()),
            Div(A_hole(), Z_hole()),
            Mul(A_hole(), A_hole()),
        ]

    def bit_hole():
        return [
            Equal(A_hole(), A_hole()),
            NEqual(B_hole(), B_hole()),
            Less(A_hole(), A_hole()),
            LessEqual(A_hole(), A_hole()),
        ]
        return [Bit()] if len(bits) == 1 else []

    def var_hole():
        return loop_vars[:loop_depth] + [N()]

    def int_hole():
        return [Integer(0), Integer(1), Integer(2)]

    cases = {
        C_hole: inst_hole,
        G_hole: gate_hole,
        A_hole: aexp_hole,
        B_hole: bit_hole,
        V_hole: var_hole,
        Z_hole: int_hole,
    }
    return cases[type(target)]()


def next(target: Pgm, n: int, bits: List[str], gates: List[str]) -> List[Pgm]:

    def program_case(target: Pgm, loop_depth: int, loop_range: Dict[str, int]):
        res = []
        for i in cases[type(target.inst)](target.inst, loop_depth, loop_range):
            res.append(Pgm(i))
        return res

    def lst_case(target: Seq, loop_depth: int, loop_range: Dict[str, int]):
        res = []
        if target.left.terminal():
            for i in cases[type(target.right)](target.right, loop_depth, loop_range):
                res.append(Seq(target.left, i))
        else:
            for i in cases[type(target.left)](target.left, loop_depth, loop_range):
                res.append(Seq(i, target.right))
        return res

    def for_case(target: For, loop_depth: int, loop_range: Dict[str, int]):
        res = []
        loop_depth += 1
        if target.start.terminal():
            if target.end.terminal():
                if target.end.has_syntax(target.var):
                    return []  # invalid range
                exec(
                    f"def end_val(n):\n" + indent(f"return {str(target.end)}", TAB),
                    globals(),
                )
                end = eval(f"end_val({n})")
                if int(str(target.start)) >= end or end < 0 or end > n:
                    return []  # redundant range
                loop_range[f"{str(loop_vars[loop_depth-1])}"] = {
                    "start": str(target.start),
                    "end": str(Sub(target.end, Integer(1))),
                }  # range(N) 이면 N-1까지
                for i in cases[type(target.body)](target.body, loop_depth, loop_range):
                    res.append(For(target.var, target.start, target.end, i).simplify())
            else:  # end is not terminal
                for i in cases[type(target.end)](target.end, loop_depth, loop_range):
                    res.append(For(target.var, target.start, i, target.body))
        else:  # start is not terminal
            for i in cases[type(target.start)](target.start, loop_depth, loop_range):
                res.append(For(target.var, i, target.end, target.body))
        return res

    def if_case(target: If, loop_depth: int, loop_range: Dict[str, int]):
        res = []
        if target.cond.terminal():
            if target.then.terminal():
                for i in cases[type(target.else_)](
                    target.else_, loop_depth, loop_range
                ):
                    res.append(If(target.cond, target.then, i).simplify())
            else:  # then is not terminal
                for i in cases[type(target.then)](target.then, loop_depth, loop_range):
                    res.append(If(target.cond, i, target.else_))
        else:  # cond is not terminal
            for i in cases[type(target.cond)](target.cond, loop_depth, loop_range):
                res.append(If(i, target.then, target.else_))
        return res

    def singleQ_gate(
        target: Union[H, X, Ry], loop_depth: int, loop_range: Dict[str, int]
    ):
        res = []
        for i in cases[type(target.qreg)](target.qreg, loop_depth, loop_range):
            if i.terminal():
                if loop_depth != 0 and not i.has_syntax(loop_vars[loop_depth - 1]):
                    continue
                # 0 <= qreg < n
                if basic_constraints(i, n, loop_range):
                    res.append(type(target)(qreg=i))
            else:
                res.append(type(target)(qreg=i))
        return res

    def multiQ_gate(
        target: Union[CX, CRy], loop_depth: int, loop_range: Dict[str, int]
    ):
        res = []
        if target.qreg1.terminal():
            for i in cases[type(target.qreg2)](target.qreg2, loop_depth, loop_range):
                if i.terminal():
                    if (
                        loop_depth != 0
                        and not i.has_syntax(loop_vars[loop_depth - 1])
                        and not target.qreg1.has_syntax(loop_vars[loop_depth - 1])
                    ):
                        continue
                    # target != control & 0 <= qreg < n
                    if i != target.qreg1 and basic_constraints(i, n, loop_range):
                        res.append(type(target)(qreg1=target.qreg1, qreg2=i))
                else:
                    res.append(type(target)(qreg1=target.qreg1, qreg2=i))
        else:  # qreg1 is not terminal
            for i in cases[type(target.qreg1)](target.qreg1, loop_depth, loop_range):
                if i.terminal():
                    # 0 <= qreg < n
                    if basic_constraints(i, n, loop_range):
                        res.append(type(target)(qreg1=i, qreg2=target.qreg2))
                else:
                    res.append(type(target)(qreg1=i, qreg2=target.qreg2))
        return res

    def aexp_case(
        target: Union[Div, Mul, Add, Sub],
        loop_depth: int,
        loop_range: Dict[str, int],
    ):
        res = []
        if target.left.terminal():
            for i in cases[type(target.right)](target.right, loop_depth, loop_range):
                if (
                    not (target.left.has_syntax(Integer()) and i.has_syntax(Integer()))
                    and not (target.left.has_syntax(N()) and i.has_syntax(N()))
                    and not (
                        target.left.has_syntax(I()) and target.right.has_syntax(I())
                    )
                    and not (
                        target.left.has_syntax(J()) and target.right.has_syntax(J())
                    )
                ):  # avoid using int/n/i/j/k in aexp more than once (TODO: 나중에 수정할수도 있음 e.g. 2 * n - 1)
                    try:
                        res.append(type(target)(target.left, i).simplify())
                    except ZeroDivisionError:
                        pass
        else:  # left is not terminal
            for i in cases[type(target.left)](target.left, loop_depth, loop_range):
                try:
                    res.append(type(target)(i, target.right).simplify())
                except ZeroDivisionError:
                    pass
        return res

    def itself(
        target: Union[Integer, I, J, N, Bit, Skip],
        loop_depth: int,
        loop_range: Dict[str, int],
    ):
        return []

    def hole_case(
        target: Union[C_hole, G_hole, A_hole, V_hole, Z_hole],
        loop_depth: int,
        loop_range: Dict[str, int],
    ):
        return fill_hole(target, bits, gates, loop_depth)

    cases = {
        C_hole: hole_case,
        G_hole: hole_case,
        A_hole: hole_case,
        B_hole: hole_case,
        V_hole: hole_case,
        Z_hole: hole_case,
        Pgm: program_case,
        Seq: lst_case,
        For: for_case,
        If: if_case,
        H: singleQ_gate,
        X: singleQ_gate,
        Ry: singleQ_gate,
        CX: multiQ_gate,
        CRy: multiQ_gate,
        Add: aexp_case,
        Sub: aexp_case,
        Mul: aexp_case,
        Div: aexp_case,
        Integer: itself,
        I: itself,
        J: itself,
        N: itself,
        Bit: itself,
        Skip: itself,
    }
    return cases[type(target)](target, loop_depth=0, loop_range={})


# exp가 0 <= exp < n 조건을 만족하면 True
def basic_constraints(exp: Aexp, n: int, loop_range: dict[str, dict[str, int]]) -> bool:

    exp_low = str(exp)
    if exp_low.find("i") >= 0:
        exp_low = exp_low.replace("i", loop_range["i"]["start"])
    if exp_low.find("j") >= 0:
        j_start = loop_range["j"]["start"].replace(
            "i", loop_range["i"]["start"]
        )  # j range에 i가 사용된 경우
        exp_low = exp_low.replace("j", j_start)
    if exp_low.find("k") >= 0:
        k_start = loop_range["k"]["start"].replace(
            "i", loop_range["i"]["start"]
        )  # k range에 i가 사용된 경우
        k_start = k_start.replace(
            "j", loop_range["j"]["start"]
        )  # k range에 j가 사용된 경우
        exp_low = exp_low.replace("k", k_start)
    if exp_low.find("n") >= 0:
        exp_low = exp_low.replace("n", f"{n}")

    exp_high = str(exp)
    if exp_high.find("i") >= 0:  # i가 있는 경우
        exp_high = exp_high.replace(
            "i", loop_range["i"]["end"]
        )  # i를 range의 end로 대체
    if exp_high.find("j") >= 0:
        j_end = loop_range["j"]["end"].replace(
            "i", loop_range["i"]["end"]
        )  # j range에 i가 사용된 경우
        exp_high = exp_high.replace("j", j_end)
    if exp_high.find("k") >= 0:
        k_end = loop_range["k"]["end"].replace(
            "j", loop_range["j"]["end"]
        )  # k range에 j가 사용된 경우
        k_end = k_end.replace("i", loop_range["i"]["end"])  # k range에 i가 사용된 경우
        exp_high = exp_high.replace("k", k_end)
    if exp_high.find("n") >= 0:
        exp_high = exp_high.replace("n", f"{n}")

    if (
        eval(exp_low) >= 0
        and eval(exp_low) < n
        and eval(exp_high) >= 0
        and eval(exp_high) < n
    ):
        return True
    else:
        return False


def fill_theta(n: int, target: Pgm, loop_depth: int) -> List[Pgm]:
    symbol = [sym_i, sym_j]

    def program_case(target: Pgm, loop_depth: int):
        res = []
        for i in cases[type(target.inst)](target.inst, loop_depth)[0]:
            res.append(Pgm(i))
        return res, loop_depth

    def lst_case(target: Seq, loop_depth: int):
        res = []
        for i in cases[type(target.left)](target.left, loop_depth)[0]:
            for j in cases[type(target.right)](target.right, loop_depth)[0]:
                res.append(Seq(i, j))
        return res, loop_depth

    def for_case(target: For, loop_depth: int):
        loop_depth += 1
        res = []
        for i in cases[type(target.body)](target.body, loop_depth)[0]:
            res.append(For(target.var, target.start, target.end, i))
        return res, loop_depth

    def if_case(target: If, loop_depth: int):
        res = []
        for i in cases[type(target.then)](target.then, loop_depth)[0]:
            for j in cases[type(target.else_)](target.else_, loop_depth)[0]:
                res.append(If(target.cond, i, j))
        return res, loop_depth

    def ry_case(target: Ry, loop_depth: int):
        res = []
        for i in generate_exp(n, symbol[:loop_depth]):
            res.append(Ry(str(1), str(i), target.qreg))
        return res, loop_depth

    def cry_case(target: CRy, loop_depth: int):
        res = []
        for i in generate_exp(n, symbol[:loop_depth]):
            res.append(CRy(str(1), str(i), target.qreg1, target.qreg2))
        return res, loop_depth

    def else_case(target, loop_depth):
        return [target], loop_depth

    cases = {
        Pgm: program_case,
        Seq: lst_case,
        For: for_case,
        If: if_case,
        Ry: ry_case,
        CRy: cry_case,
        H: else_case,
        X: else_case,
        CX: else_case,
        Skip: else_case,
    }

    return cases[type(target)](target, loop_depth)[0]


def generate_exp(n: int, variables: List[sp.Symbol]) -> List[sp.Expr]:

    COEFFS = [2, 1, 0, -1, -2]
    vars_to_generate = variables + [sym_n] + [1]  # list of variables + n + constant
    coeff_candidates = list(itertools.product(*([COEFFS] * len(vars_to_generate))))
    res = []

    for coeffs in coeff_candidates:
        alg_exp = 0
        for coeff, var in zip(coeffs, vars_to_generate):
            alg_exp += coeff * var
        i = n - 1  # eval 함수에서 i를 사용하기 위함
        if (
            alg_exp not in res and not eval(str(alg_exp)) <= 0
        ):  # loop depth 1인 경우만 처리
            res.append(alg_exp)
    return res

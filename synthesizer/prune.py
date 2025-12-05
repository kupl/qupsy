from typing import Union

from synthesizer.language import *

transition_debug = False


def prune_basic(target: Pgm) -> bool:
    lst_count, for_count, if_count, aexp_count = [0] * 4

    def program_case(target: Pgm):
        return cases[type(target.inst)](target.inst)

    def lst_case(target: Seq):
        nonlocal lst_count
        lst_count += 1
        if lst_count > 3:
            if transition_debug:
                print("lst count")
            return True
        return cases[type(target.left)](target.left) or cases[type(target.right)](
            target.right
        )

    def if_case(target: If):
        nonlocal if_count
        if_count += 1
        if if_count > 3:
            if transition_debug:
                print("if count")
            return True
        return (
            cases[type(target.cond)](target.cond)
            or cases[type(target.then)](target.then)
            or cases[type(target.else_)](target.else_)
        )

    def for_case(target: For):
        nonlocal for_count
        for_count += 1
        if for_count > 1:  # for loop 한 번으로 제한
            if transition_debug:
                print("for count")
            return True
        if target.body.terminal() and not target.body.has_syntax(
            I()
        ):  # for loop 내부에 hole 없으면서, I 없는 경우
            return True
        return (
            cases[type(target.var)](target.var)
            or cases[type(target.start)](target.start)
            or cases[type(target.end)](target.end)
            or cases[type(target.body)](target.body)
        )

    def single_gate(target: Union[H, X, Ry]):
        return cases[type(target.qreg)](target.qreg)

    def controlled_gate(target: Union[CX, CRy]):
        return cases[type(target.qreg1)](target.qreg1) or cases[type(target.qreg2)](
            target.qreg2
        )

    def aexp_case(target: Union[Div, Mul, Add, Sub]):
        nonlocal aexp_count
        aexp_count += 1
        if aexp_count > 11:
            if transition_debug:
                print("aexp count")  # aexp 깊이 제한
            return True
        # aexp에 N, I, A_hole 사용 강제
        if not isinstance(target.left, Hole) and target.left == target.right:
            if transition_debug:
                print("left == right")  # left, right 같음
            return True
        res = False
        if isinstance(target, Div):
            res = res or div_case(target)
        if isinstance(target, Mul):
            res = res or mul_case(target)
        if isinstance(target, Sub):
            res = res or sub_case(target)
        if isinstance(target, Add):
            res = res or add_case(target)
        return res

    def div_case(target: Div):
        nonlocal aexp_count
        if isinstance(target.left, Div) or isinstance(target.right, Div):
            if transition_debug:
                print("same op in op")
            return True
        return cases[type(target.left)](target.left) or cases[type(target.right)](
            target.right
        )

    def mul_case(target: Mul):
        nonlocal aexp_count
        if not isinstance(target.left, Hole) and (target.left == target.right):
            if transition_debug:
                print("left == right")  # left, right 같음
            return True
        if isinstance(target.left, Mul) or isinstance(target.right, Mul):
            if transition_debug:
                print("same op in op")
            return True
        return cases[type(target.left)](target.left) or cases[type(target.right)](
            target.right
        )

    def sub_case(target: Sub):
        nonlocal aexp_count
        if isinstance(target.left, Sub) or isinstance(target.right, Sub):
            if transition_debug:
                print("same op in op")
            return True
        return cases[type(target.left)](target.left) or cases[type(target.right)](
            target.right
        )

    def add_case(target: Add):
        nonlocal aexp_count
        if not isinstance(target.left, Hole) and (target.left == target.right):
            if transition_debug:
                print("left == right")  # left, right 같음
            return True
        return cases[type(target.left)](target.left) or cases[type(target.right)](
            target.right
        )

    def false_case(target: Union[Integer, Skip, Var, Hole]):
        return False

    cases = {
        Pgm: program_case,
        Seq: lst_case,
        If: if_case,
        For: for_case,
        H: single_gate,
        X: single_gate,
        Ry: single_gate,
        CX: controlled_gate,
        CRy: controlled_gate,
        Div: aexp_case,
        Mul: aexp_case,
        Sub: aexp_case,
        Add: aexp_case,
        Bit: false_case,
        Integer: false_case,
        Skip: false_case,
        I: false_case,
        J: false_case,
        N: false_case,
        C_hole: false_case,
        G_hole: false_case,
        A_hole: false_case,
        V_hole: false_case,
        Z_hole: false_case,
    }
    return cases[type(target)](target)

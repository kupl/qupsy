from qupsy.language import (
    ALL_AEXPS,
    ALL_GATES,
    Aexp,
    Cmd,
    ForCmd,
    Gate,
    GateCmd,
    HoleAexp,
    HoleCmd,
    HoleGate,
    Integer,
    Pgm,
    SeqCmd,
    Var,
)


class TransitionVisitor:
    def __init__(self) -> None:
        self.n = ""
        self.for_depth = 0

    def visit_HoleAexp(self, aexp: HoleAexp) -> list[Aexp]:
        return (
            [a() for a in ALL_AEXPS if a not in (HoleAexp, Integer, Var)]
            + [Integer(i) for i in range(3)]  # 0,1,2
            + [Var(f"i{i}") for i in range(self.for_depth)]
            + [Var(self.n)]
        )

    def visit_Aexp(self, aexp: Aexp) -> list[Aexp]:
        visitor_name = f"visit_{aexp.__class__.__name__}"
        visitor = getattr(self, visitor_name, None)
        if visitor is not None:
            return visitor(aexp)

        for i, child in enumerate(aexp.children):
            if child.terminated:
                continue
            next_children = self.visit_Aexp(child)
            pre_args = aexp.children[:i]
            post_args = aexp.children[i + 1 :]
            ret: list[Aexp] = []
            for next_child in next_children:
                ret.append(
                    aexp.__class__(
                        *(a.copy() for a in pre_args),
                        next_child,  # type: ignore
                        *(a.copy() for a in post_args),
                    )
                )
            return ret
        return []

    def visit_HoleGate(self, gate: HoleGate) -> list[Gate]:
        return [g() for g in ALL_GATES if g != HoleGate]

    def visit_Gate(self, gate: Gate) -> list[Gate]:
        visitor_name = f"visit_{gate.__class__.__name__}"
        visitor = getattr(self, visitor_name, None)
        if visitor is not None:
            return visitor(gate)

        for i, child in enumerate(gate.children):
            if child.terminated:
                continue
            next_children = self.visit_Aexp(child)
            pre_args = gate.children[:i]
            post_args = gate.children[i + 1 :]
            ret: list[Gate] = []
            for next_child in next_children:
                ret.append(
                    gate.__class__(
                        *(a.copy() for a in pre_args),
                        next_child,  # type: ignore
                        *(a.copy() for a in post_args),
                    )
                )
            return ret
        return []

    def visit_HoleCmd(self, cmd: HoleCmd) -> list[Cmd]:
        return [SeqCmd(), ForCmd(var=f"i{self.for_depth}"), GateCmd()]

    def visit_SeqCmd(self, cmd: SeqCmd) -> list[Cmd]:
        if not cmd.pre.terminated:
            pres = self.visit_Cmd(cmd.pre)
            ret: list[Cmd] = []
            for pre in pres:
                ret.append(SeqCmd(pre=pre, post=cmd.post.copy()))
            return ret
        if not cmd.post.terminated:
            posts = self.visit_Cmd(cmd.post)
            ret: list[Cmd] = []
            for post in posts:
                ret.append(SeqCmd(pre=cmd.pre.copy(), post=post))
            return ret
        return []

    def visit_ForCmd(self, cmd: ForCmd) -> list[Cmd]:
        if not cmd.start.terminated:
            starts = self.visit_Aexp(cmd.start)
            ret: list[Cmd] = []
            for start in starts:
                ret.append(
                    ForCmd(
                        var=cmd.var,
                        start=start,
                        end=cmd.end.copy(),
                        body=cmd.body.copy(),
                    )
                )
            return ret
        if not cmd.end.terminated:
            ends = self.visit_Aexp(cmd.end)
            ret: list[Cmd] = []
            for end in ends:
                ret.append(
                    ForCmd(
                        var=cmd.var,
                        start=cmd.start.copy(),
                        end=end,
                        body=cmd.body.copy(),
                    )
                )
            return ret
        if not cmd.body.terminated:
            self.for_depth += 1
            bodies = self.visit_Cmd(cmd.body)
            self.for_depth -= 1
            ret: list[Cmd] = []
            for body in bodies:
                ret.append(
                    ForCmd(
                        var=cmd.var,
                        start=cmd.start.copy(),
                        end=cmd.end.copy(),
                        body=body,
                    )
                )
            return ret
        return []

    def visit_GateCmd(self, cmd: GateCmd) -> list[Cmd]:
        gates = self.visit_Gate(cmd.gate)
        return [GateCmd(gate) for gate in gates]

    def visit_Cmd(self, cmd: Cmd) -> list[Cmd]:
        if isinstance(cmd, HoleCmd):
            return self.visit_HoleCmd(cmd)
        if isinstance(cmd, SeqCmd):
            return self.visit_SeqCmd(cmd)
        if isinstance(cmd, ForCmd):
            return self.visit_ForCmd(cmd)
        if isinstance(cmd, GateCmd):
            return self.visit_GateCmd(cmd)
        raise TypeError(f"Unknown command type: {type(cmd)}")

    def visit(self, pgm: Pgm) -> list[Pgm]:
        self.n = pgm.n
        bodies = self.visit_Cmd(pgm.body)
        return [Pgm(pgm.n, body) for body in bodies]


def next(pgm: Pgm) -> list[Pgm]:
    visitor = TransitionVisitor()
    return visitor.visit(pgm)

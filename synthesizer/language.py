from __future__ import annotations
from dataclasses import dataclass
from textwrap import indent

# simplify 함수는 ZeroDivisionError 발생 가능
TAB = "    "


@dataclass
class Pgm:
    inst: Instruction = None

    def __str__(self) -> str:
        return str(self.inst)

    def __repr__(self) -> str:
        return f"Pgm({self.inst})"

    def __lt__(self, other: "Pgm") -> bool:
        return self.cost < other.cost

    @property
    def cost(self) -> int:
        return self.inst.cost

    @property
    def depth(self) -> int:
        return 1 + self.inst.depth

    def terminal(self) -> bool:
        return self.inst.terminal()

    def has_syntax(self, syntax) -> bool:
        if isinstance(syntax, Pgm):
            return True
        return self.inst.has_syntax(syntax)

    def continued(self, syntax) -> bool:
        if isinstance(syntax, Pgm):
            return self.inst.continued(syntax.inst)
        return False

    def simplify(self):
        return Pgm(self.inst.simplify())


######### Instruction #########
class Instruction:
    pass


@dataclass
class Seq(Instruction):
    left: Instruction = None
    right: Instruction = None

    def __str__(self) -> str:
        return f"{str(self.left)}\n{str(self.right)}"

    def __repr__(self) -> str:
        return f"Seq({self.left}, {self.right})"

    @property
    def cost(self) -> int:
        return 5 + self.left.cost + self.right.cost

    @property
    def depth(self) -> int:
        return 1 + max(self.left.depth, self.right.depth)

    def terminal(self) -> bool:
        return self.left.terminal() and self.right.terminal()

    def has_syntax(self, syntax) -> bool:
        if isinstance(syntax, Seq):
            return True
        return self.left.has_syntax(syntax) or self.right.has_syntax(syntax)

    def continued(self, syntax) -> bool:
        if isinstance(syntax, Seq):
            return self.left.continued(syntax.left) and self.right.continued(
                syntax.right
            )
        return False

    def simplify(self):
        return Seq(self.left.simplify(), self.right.simplify())


@dataclass
class For(Instruction):
    var: Var = None
    start: Integer = None
    end: Integer = None
    body: Instruction = None

    def __str__(self) -> str:
        return f"for {str(self.var)} in range({str(self.start)}, {str(self.end)}):\n{indent(str(self.body),TAB)}"

    def __repr__(self) -> str:
        return f"For({self.var}, {self.start}, {self.end}, {self.body})"

    @property
    def cost(self) -> int:
        return 3 + self.var.cost + self.start.cost + self.end.cost + self.body.cost

    @property
    def depth(self) -> int:
        return 1 + max(self.start.depth, self.end.depth, self.body.depth)

    def terminal(self) -> bool:
        return (
            self.var.terminal()
            and self.start.terminal()
            and self.end.terminal()
            and self.body.terminal()
        )

    def has_syntax(self, syntax) -> bool:
        if isinstance(syntax, For):
            return True
        return (
            self.var.has_syntax(syntax)
            or self.start.has_syntax(syntax)
            or self.end.has_syntax(syntax)
            or self.body.has_syntax(syntax)
        )

    def continued(self, syntax) -> bool:
        if isinstance(syntax, For):
            return (
                self.var.continued(syntax.var)
                and self.start.continued(syntax.start)
                and self.end.continued(syntax.end)
                and self.body.continued(syntax.body)
            )
        return False

    def simplify(self):
        return For(
            self.var.simplify(),
            self.start.simplify(),
            self.end.simplify(),
            self.body.simplify(),
        )


@dataclass
class If(Instruction):
    cond: Bexp = None
    then: Instruction = None
    else_: Instruction = None

    def __str__(self) -> str:
        if self.else_ == Skip():
            return f"if {str(self.cond)}:\n{indent(str(self.then),TAB)}"
        return f"if {str(self.cond)}:\n{indent(str(self.then),TAB)}\nelse:\n{indent(str(self.else_),TAB)}"

    def __repr__(self) -> str:
        return f"If({self.cond}, {self.then}, {self.else_})"

    @property
    def cost(self) -> int:
        return 30 + self.cond.cost + self.then.cost + self.else_.cost

    @property
    def depth(self) -> int:
        return 1 + max(self.then.depth, self.else_.depth)

    def terminal(self) -> bool:
        return self.cond.terminal() and self.then.terminal() and self.else_.terminal()

    def has_syntax(self, syntax) -> bool:
        if isinstance(syntax, If):
            return True
        return (
            self.cond.has_syntax(syntax)
            or self.then.has_syntax(syntax)
            or self.else_.has_syntax(syntax)
        )

    def continued(self, syntax) -> bool:
        if isinstance(syntax, If):
            return (
                self.cond.continued(syntax.cond)
                and self.then.continued(syntax.then)
                and self.else_.continued(syntax.else_)
            )
        return False

    def simplify(self):
        if (
            not self.then.has_syntax(C_hole())
            and not self.then.has_syntax(G_hole())
            and not self.then.has_syntax(A_hole())
            and self.then.simplify() == self.else_.simplify()
        ):
            return self.then.simplify()
        return If(self.cond.simplify(), self.then.simplify(), self.else_.simplify())


@dataclass
class Skip(Instruction):

    def __str__(self) -> str:
        return "pass"

    def __repr__(self) -> str:
        return "Skip()"

    @property
    def cost(self) -> int:
        return 1

    @property
    def depth(self) -> int:
        return 1

    def terminal(self) -> bool:
        return True

    def has_syntax(self, syntax) -> bool:
        return isinstance(syntax, Skip)

    def continued(self, syntax) -> bool:
        return isinstance(syntax, Skip)

    def simplify(self):
        return Skip()


######### Gates #########
class Gate(Instruction):
    pass


@dataclass
class H(Gate):
    qreg: Aexp = None

    def __str__(self) -> str:
        return f"qc.append(cirq.H(qbits[{str(self.qreg)}]))"

    def __repr__(self) -> str:
        return f"H({self.qreg})"

    @property
    def cost(self) -> int:
        return 2 + self.qreg.cost

    @property
    def depth(self) -> int:
        return 1 + self.qreg.depth

    def terminal(self) -> bool:
        return self.qreg.terminal()

    def has_syntax(self, syntax) -> bool:
        if isinstance(syntax, H):
            return True
        return self.qreg.has_syntax(syntax)

    def continued(self, syntax) -> bool:
        if isinstance(syntax, H):
            return self.qreg.continued(syntax.qreg)
        return False

    def simplify(self):
        return H(self.qreg.simplify())


@dataclass
class X(Gate):
    qreg: Aexp = None

    def __str__(self) -> str:
        return f"qc.append(cirq.X(qbits[{str(self.qreg)}]))"

    def __repr__(self) -> str:
        return f"X({self.qreg})"

    @property
    def cost(self) -> int:
        return 2 + self.qreg.cost

    @property
    def depth(self) -> int:
        return 1 + self.qreg.depth

    def terminal(self) -> bool:
        return self.qreg.terminal()

    def has_syntax(self, syntax) -> bool:
        if isinstance(syntax, X):
            return True
        return self.qreg.has_syntax(syntax)

    def continued(self, syntax) -> bool:
        if isinstance(syntax, X):
            return self.qreg.continued(syntax.qreg)
        return False

    def simplify(self):
        return X(self.qreg.simplify())


@dataclass
class Y(Gate):
    pass


@dataclass
class Z(Gate):
    pass


@dataclass
class Ry(Gate):
    p: Aexp = None
    q: Aexp = None
    qreg: Aexp = None

    def __str__(self) -> str:
        if self.p is None and self.q is None:
            return f"qc.append(cirq.Ry(rads=2*np.arccos(math.sqrt(□)))(qbits[{str(self.qreg)}]))"
        return (
            "qc.append(cirq.Ry(rads=2*np.arccos(math.sqrt("
            + self.p
            + "/("
            + self.q
            + f"))))(qbits[{str(self.qreg)}]))"
        )

    def __repr__(self) -> str:
        return f"Ry({self.p}, {self.q}, {self.qreg})"

    @property
    def cost(self) -> int:
        return 2 + self.p.cost + self.q.cost + self.qreg.cost

    @property
    def depth(self) -> int:
        return 1 + max(self.p.depth, self.q.depth, self.qreg.depth)

    def terminal(self) -> bool:
        return self.qreg.terminal()

    def has_syntax(self, syntax) -> bool:
        if isinstance(syntax, Ry):
            return True
        return self.qreg.has_syntax(syntax)

    def continued(self, syntax) -> bool:
        if isinstance(syntax, Ry):
            return self.qreg.continued(syntax.qreg)
        return False

    def simplify(self):
        return Ry(self.p.simplify(), self.q.simplify(), self.qreg.simplify())


@dataclass
class CX(Gate):
    qreg1: Aexp = None
    qreg2: Aexp = None

    def __str__(self) -> str:
        return f"qc.append(cirq.CX(qbits[{str(self.qreg1)}], qbits[{str(self.qreg2)}]))"

    def __repr__(self) -> str:
        return f"CX({self.qreg1}, {self.qreg2})"

    @property
    def cost(self) -> int:
        return 2 + self.qreg1.cost + self.qreg2.cost

    @property
    def depth(self) -> int:
        return 1 + max(self.qreg1.depth, self.qreg2.depth)

    def terminal(self) -> bool:
        return self.qreg1.terminal() and self.qreg2.terminal()

    def has_syntax(self, syntax) -> bool:
        if isinstance(syntax, CX):
            return True
        return self.qreg1.has_syntax(syntax) or self.qreg2.has_syntax(syntax)

    def continued(self, syntax) -> bool:
        if isinstance(syntax, CX):
            return self.qreg1.continued(syntax.qreg1) and self.qreg2.continued(
                syntax.qreg2
            )
        return False

    def simplify(self):
        return CX(self.qreg1.simplify(), self.qreg2.simplify())


@dataclass
class CY(Gate):
    pass


@dataclass
class CZ(Gate):
    pass


@dataclass
class CRy(Gate):
    p: Aexp = None
    q: Aexp = None
    qreg1: Aexp = None
    qreg2: Aexp = None

    def __str__(self) -> str:
        if self.p is None and self.q is None:
            return f"qc.append(cirq.Ry(rads=2*np.arccos(math.sqrt(□/□)))).controlled(num_controls=1)(qbits[{str(self.qreg1)}],qbits[{str(self.qreg2)}]))"
        return (
            "qc.append(cirq.Ry(rads=2*np.arccos(math.sqrt("
            + self.p
            + "/("
            + self.q
            + f")))).controlled(num_controls=1)(qbits[{str(self.qreg1)}],qbits[{str(self.qreg2)}]))"
        )

    def __repr__(self) -> str:
        return f"CRy({self.p}, {self.q}, {self.qreg1}, {self.qreg2})"

    @property
    def cost(self) -> int:
        return 2 + self.qreg1.cost + self.qreg2.cost

    @property
    def depth(self) -> int:
        return 1 + max(self.qreg1.depth, self.qreg2.depth)

    def terminal(self) -> bool:
        return self.qreg1.terminal() and self.qreg2.terminal()

    def has_syntax(self, syntax) -> bool:
        if isinstance(syntax, CRy):
            return True
        return self.qreg1.has_syntax(syntax) or self.qreg2.has_syntax(syntax)

    def continued(self, syntax) -> bool:
        if isinstance(syntax, CRy):
            return self.qreg1.continued(syntax.qreg1) and self.qreg2.continued(
                syntax.qreg2
            )
        return False

    def simplify(self):
        return CRy(self.p, self.q, self.qreg1.simplify(), self.qreg2.simplify())


######### Aexp #########
class Aexp:
    pass


@dataclass
class Add(Aexp):
    left: Aexp = None
    right: Aexp = None

    def __str__(self) -> str:
        return f"({str(self.left)} + {str(self.right)})"

    def __repr__(self) -> str:
        return f"Add({self.left}, {self.right})"

    @property
    def cost(self) -> int:
        return 3 + self.left.cost + self.right.cost

    @property
    def depth(self) -> int:
        return 1 + max(self.left.depth, self.right.depth)

    def terminal(self) -> bool:
        return self.left.terminal() and self.right.terminal()

    def has_syntax(self, syntax) -> bool:
        if isinstance(syntax, Add):
            return True
        return self.left.has_syntax(syntax) or self.right.has_syntax(syntax)

    def continued(self, syntax) -> bool:
        if isinstance(syntax, Add):
            return self.left.continued(syntax.left) or self.right.continued(
                syntax.right
            )
        return False

    def simplify(self):
        if self.left == Integer(0):
            return self.right.simplify()
        elif self.right == Integer(0):
            return self.left.simplify()
        else:
            return Add(self.left.simplify(), self.right.simplify())


@dataclass
class Sub(Aexp):
    left: Aexp = None
    right: Aexp = None

    def __str__(self) -> str:
        return f"({str(self.left)} - {str(self.right)})"

    def __repr__(self) -> str:
        return f"Sub({self.left}, {self.right})"

    @property
    def cost(self) -> int:
        return 3 + self.left.cost + self.right.cost

    @property
    def depth(self) -> int:
        return 1 + max(self.left.depth, self.right.depth)

    def terminal(self) -> bool:
        return self.left.terminal() and self.right.terminal()

    def has_syntax(self, syntax) -> bool:
        if isinstance(syntax, Sub):
            return True
        return self.left.has_syntax(syntax) or self.right.has_syntax(syntax)

    def continued(self, syntax) -> bool:
        if isinstance(syntax, Sub):
            return self.left.continued(syntax.left) or self.right.continued(
                syntax.right
            )
        return False

    def simplify(self):
        if self.right == Integer(0):
            return self.left.simplify()
        elif not isinstance(self.left, Hole) and self.left == self.right:
            return Integer(0)
        else:
            return Sub(self.left.simplify(), self.right.simplify())


@dataclass
class Div(Aexp):
    left: Aexp = None
    right: Aexp = None

    def __str__(self) -> str:
        return f"({str(self.left)} // {str(self.right)})"

    def __repr__(self) -> str:
        return f"Div({self.left}, {self.right})"

    @property
    def cost(self) -> int:
        return 3 + self.left.cost + self.right.cost

    @property
    def depth(self) -> int:
        return 1 + max(self.left.depth, self.right.depth)

    def terminal(self) -> bool:
        return self.left.terminal() and self.right.terminal()

    def has_syntax(self, syntax) -> bool:
        if isinstance(syntax, Div):
            return True
        return self.left.has_syntax(syntax) or self.right.has_syntax(syntax)

    def continued(self, syntax) -> bool:
        if isinstance(syntax, Div):
            return self.left.continued(syntax.left) or self.right.continued(
                syntax.right
            )
        return False

    def simplify(self):
        if self.right == Integer(0):
            raise ZeroDivisionError
        elif self.right == Integer(1):
            return self.left.simplify()
        elif self.left == Integer(0):
            return Integer(0)
        elif not isinstance(self.left, Hole) and self.left == self.right:
            return Integer(1)
        else:
            return Div(self.left.simplify(), self.right.simplify())


@dataclass
class Mul(Aexp):
    left: Aexp = None
    right: Aexp = None

    def __str__(self) -> str:
        return f"({str(self.left)} * {str(self.right)})"

    def __repr__(self) -> str:
        return f"Mul({self.left}, {self.right})"

    @property
    def cost(self) -> int:
        return 3 + self.left.cost + self.right.cost

    @property
    def depth(self) -> int:
        return 1 + max(self.left.depth, self.right.depth)

    def terminal(self) -> bool:
        return self.left.terminal() and self.right.terminal()

    def has_syntax(self, syntax) -> bool:
        if isinstance(syntax, Mul):
            return True
        return self.left.has_syntax(syntax) or self.right.has_syntax(syntax)

    def continued(self, syntax) -> bool:
        if isinstance(syntax, Mul):
            return self.left.continued(syntax.left) or self.right.continued(
                syntax.right
            )
        return False

    def simplify(self):
        if self.left == Integer(1):
            return self.right.simplify()
        elif self.right == Integer(1):
            return self.left.simplify()
        elif self.left == Integer(0) or self.right == Integer(0):
            return Integer(0)
        else:
            return Mul(self.left.simplify(), self.right.simplify())


######### Bexp #########
class Bexp:
    pass


@dataclass
class Equal(Bexp):
    left: Aexp = None
    right: Aexp = None

    def __str__(self) -> str:
        return f"({str(self.left)} == {str(self.right)})"

    def __repr__(self) -> str:
        return f"Equal({self.left}, {self.right})"

    @property
    def cost(self) -> int:
        return 3 + self.left.cost + self.right.cost

    @property
    def depth(self) -> int:
        return 1 + max(self.left.depth, self.right.depth)

    def terminal(self) -> bool:
        return self.left.terminal() and self.right.terminal()

    def has_syntax(self, syntax) -> bool:
        if isinstance(syntax, Equal):
            return True
        return self.left.has_syntax(syntax) or self.right.has_syntax(syntax)

    def continued(self, syntax) -> bool:
        if isinstance(syntax, Equal):
            return self.left.continued(syntax.left) or self.right.continued(
                syntax.right
            )
        return False

    def simplify(self):
        if self.left == self.right:
            return Integer(1)
        else:
            return Equal(self.left.simplify(), self.right.simplify())


@dataclass
class NEqual(Bexp):
    left: Aexp = None
    right: Aexp = None

    def __str__(self) -> str:
        return f"({str(self.left)} != {str(self.right)})"

    def __repr__(self) -> str:
        return f"NEqual({self.left}, {self.right})"

    @property
    def cost(self) -> int:
        return 3 + self.left.cost + self.right.cost

    @property
    def depth(self) -> int:
        return 1 + max(self.left.depth, self.right.depth)

    def terminal(self) -> bool:
        return self.left.terminal() and self.right.terminal()

    def has_syntax(self, syntax) -> bool:
        if isinstance(syntax, NEqual):
            return True
        return self.left.has_syntax(syntax) or self.right.has_syntax(syntax)

    def continued(self, syntax) -> bool:
        if isinstance(syntax, NEqual):
            return self.left.continued(syntax.left) or self.right.continued(
                syntax.right
            )
        return False

    def simplify(self):
        if self.left == self.right:
            return Integer(0)
        else:
            return NEqual(self.left.simplify(), self.right.simplify())


@dataclass
class Less(Bexp):
    left: Aexp = None
    right: Aexp = None

    def __str__(self) -> str:
        return f"({str(self.left)} < {str(self.right)})"

    def __repr__(self) -> str:
        return f"Less({self.left}, {self.right})"

    @property
    def cost(self) -> int:
        return 3 + self.left.cost + self.right.cost

    @property
    def depth(self) -> int:
        return 1 + max(self.left.depth, self.right.depth)

    def terminal(self) -> bool:
        return self.left.terminal() and self.right.terminal()

    def has_syntax(self, syntax) -> bool:
        if isinstance(syntax, Less):
            return True
        return self.left.has_syntax(syntax) or self.right.has_syntax(syntax)

    def continued(self, syntax) -> bool:
        if isinstance(syntax, Less):
            return self.left.continued(syntax.left) or self.right.continued(
                syntax.right
            )
        return False

    def simplify(self):
        if self.left == self.right:
            return Integer(0)
        else:
            return Less(self.left.simplify(), self.right.simplify())


@dataclass
class LessEqual(Bexp):
    left: Aexp = None
    right: Aexp = None

    def __str__(self) -> str:
        return f"({str(self.left)} <= {str(self.right)})"

    def __repr__(self) -> str:
        return f"LessEqual({self.left}, {self.right})"

    @property
    def cost(self) -> int:
        return 3 + self.left.cost + self.right.cost

    @property
    def depth(self) -> int:
        return 1 + max(self.left.depth, self.right.depth)

    def terminal(self) -> bool:
        return self.left.terminal() and self.right.terminal()

    def has_syntax(self, syntax) -> bool:
        if isinstance(syntax, LessEqual):
            return True
        return self.left.has_syntax(syntax) or self.right.has_syntax(syntax)

    def continued(self, syntax) -> bool:
        if isinstance(syntax, LessEqual):
            return self.left.continued(syntax.left) or self.right.continued(
                syntax.right
            )
        return False

    def simplify(self):
        if self.left == self.right:
            return Integer(1)
        else:
            return LessEqual(self.left.simplify(), self.right.simplify())


######### Integer #########
@dataclass
class Integer(Aexp):
    value: int = None

    def __str__(self) -> str:
        if type(self.value) == int:
            return f"{self.value}"
        return f"{str(self.value)}"

    def __repr__(self) -> str:
        return f"Integer({self.value})"

    @property
    def cost(self) -> int:
        return 1

    @property
    def depth(self) -> int:
        if type(self.value) == int:
            return 2
        return 1 + self.value.depth

    def terminal(self) -> bool:
        if type(self.value) == int:
            return True
        return self.value.terminal()

    def has_syntax(self, syntax) -> bool:
        if isinstance(syntax, Integer):
            return True
        if type(self.value) == int:
            return self.value == syntax
        return self.value.has_syntax(syntax)

    def continued(self, syntax) -> bool:
        if isinstance(syntax, Integer):
            return self == syntax
        return False

    def simplify(self):
        return Integer(self.value)


######### Var #########
class Var(Aexp):
    pass


@dataclass
class N(Var):

    def __str__(self) -> str:
        return "n"

    def __repr__(self) -> str:
        return "N()"

    @property
    def cost(self) -> int:
        return 0

    @property
    def depth(self) -> int:
        return 1

    def terminal(self) -> bool:
        return True

    def has_syntax(self, syntax) -> bool:
        return isinstance(syntax, N)

    def continued(self, syntax) -> bool:
        return isinstance(syntax, N)

    def simplify(self):
        return N()


@dataclass
class I(Var):

    def __str__(self) -> str:
        return "i"

    def __repr__(self) -> str:
        return "I()"

    @property
    def cost(self) -> int:
        return 0

    @property
    def depth(self) -> int:
        return 1

    def terminal(self) -> bool:
        return True

    def has_syntax(self, syntax) -> bool:
        return isinstance(syntax, I)

    def continued(self, syntax) -> bool:
        return isinstance(syntax, I)

    def simplify(self):
        return I()


@dataclass
class J(Var):

    def __str__(self) -> str:
        return "j"

    def __repr__(self) -> str:
        return "J()"

    @property
    def cost(self) -> int:
        return 0

    @property
    def depth(self) -> int:
        return 1

    def terminal(self) -> bool:
        return True

    def has_syntax(self, syntax) -> bool:
        return isinstance(syntax, J) or isinstance(syntax, N)

    def continued(self, syntax) -> bool:
        return isinstance(syntax, J)

    def simplify(self):
        return J()


@dataclass
class Bit(Var):
    index: Var = None

    def __str__(self) -> str:
        if self.index is None:
            return "bit"
        return f"bit[{str(self.index)}]"

    def __repr__(self) -> str:
        if self.index is None:
            return "Bit()"
        return f"Bit({self.index})"

    @property
    def cost(self) -> int:
        if self.index is None:
            return 0
        return self.index.cost

    @property
    def depth(self) -> int:
        if self.index is None:
            return 1
        return 1 + self.index.depth

    def terminal(self) -> bool:
        if self.index is None:
            return True
        return self.index.terminal()

    def has_syntax(self, syntax) -> bool:
        if isinstance(syntax, Bit) or self.index is None:
            return True
        return self.index.has_syntax(syntax)

    def continued(self, syntax) -> bool:
        if isinstance(syntax, Bit) or self.index is None:
            return self.index.continued(syntax.index)
        return False

    def simplify(self):
        if self.index is None:
            return Bit()
        return Bit(self.index.simplify())


######### Hole #########
class Hole:
    pass


@dataclass
class C_hole(Instruction, Hole):

    def __str__(self) -> str:
        return "□_c"

    def __repr__(self) -> str:
        return "C_hole()"

    @property
    def cost(self) -> int:
        return 5

    @property
    def depth(self) -> int:
        return 1

    def terminal(self) -> bool:
        return False

    def has_syntax(self, syntax) -> bool:
        return isinstance(syntax, C_hole)

    def continued(self, syntax) -> bool:
        return isinstance(syntax, Instruction)

    def simplify(self):
        return C_hole()


@dataclass
class G_hole(Gate, Hole):

    def __str__(self) -> str:
        return "□_g"

    def __repr__(self) -> str:
        return "G_hole()"

    @property
    def cost(self) -> int:
        return 3

    @property
    def depth(self) -> int:
        return 1

    def terminal(self) -> bool:
        return False

    def has_syntax(self, syntax) -> bool:
        return isinstance(syntax, G_hole)

    def continued(self, syntax) -> bool:
        return isinstance(syntax, Gate)

    def simplify(self):
        return G_hole()


@dataclass
class A_hole(Aexp, Hole):

    def __str__(self) -> str:
        return "□_a"

    def __repr__(self) -> str:
        return "A_hole()"

    @property
    def cost(self) -> int:
        return 3

    @property
    def depth(self) -> int:
        return 1

    def terminal(self) -> bool:
        return False

    def has_syntax(self, syntax) -> bool:
        return isinstance(syntax, A_hole)

    def continued(self, syntax) -> bool:
        return isinstance(syntax, Aexp)

    def simplify(self):
        return A_hole()


@dataclass
class B_hole(Bit, Hole):

    def __str__(self) -> str:
        return "□_b"

    def __repr__(self) -> str:
        return "B_hole()"

    @property
    def cost(self) -> int:
        return 3

    @property
    def depth(self) -> int:
        return 1

    def terminal(self) -> bool:
        return False

    def has_syntax(self, syntax) -> bool:
        return isinstance(syntax, B_hole)

    def continued(self, syntax) -> bool:
        return isinstance(syntax, Bit)

    def simplify(self):
        return B_hole()


@dataclass
class V_hole(Var, Hole):

    def __str__(self) -> str:
        return "□_v"

    def __repr__(self) -> str:
        return "V_hole()"

    @property
    def cost(self) -> int:
        return 3

    @property
    def depth(self) -> int:
        return 1

    def terminal(self) -> bool:
        return False

    def has_syntax(self, syntax) -> bool:
        return isinstance(syntax, V_hole)

    def continued(self, syntax) -> bool:
        return isinstance(syntax, Var)

    def simplify(self):
        return V_hole()


@dataclass
class Z_hole(Integer, Hole):

    def __str__(self) -> str:
        return "□_i"

    def __repr__(self) -> str:
        return "Z_hole()"

    @property
    def cost(self) -> int:
        return 3

    @property
    def depth(self) -> int:
        return 1

    def terminal(self) -> bool:
        return False

    def has_syntax(self, syntax) -> bool:
        return isinstance(syntax, Z_hole)

    def continued(self, syntax) -> bool:
        return isinstance(syntax, Integer)

    def simplify(self):
        return Z_hole()

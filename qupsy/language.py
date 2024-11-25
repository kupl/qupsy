from __future__ import annotations

from abc import ABC, abstractmethod
from textwrap import indent

TAB = "    "


class Aexp(ABC):

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass

    @property
    @abstractmethod
    def cost(self) -> int:
        pass

    @property
    @abstractmethod
    def children(self) -> list[Aexp]:
        pass

    @property
    def depth(self) -> int:
        children = self.children
        return 1 + (
            max([child.depth for child in children]) if len(children) > 0 else 0
        )

    @property
    def terminated(self) -> bool:
        for aexp in self.children:
            if not aexp.terminated:
                return False
        return True

    def copy(self) -> Aexp:
        return self.__class__(*[child.copy() for child in self.children])


class Integer(Aexp):
    def __init__(self, value: int) -> None:
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"{self.value}"

    @property
    def cost(self) -> int:
        return 0

    @property
    def children(self) -> list[Aexp]:
        return []

    def copy(self) -> Integer:
        return Integer(self.value)


class Var(Aexp):
    def __init__(self, name: str) -> None:
        self.name = name

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"{self.name}"

    @property
    def cost(self) -> int:
        return 0

    @property
    def children(self) -> list[Aexp]:
        return []

    def copy(self) -> Var:
        return Var(self.name)


class HoleAexp(Aexp):
    def __str__(self) -> str:
        return "□_a"

    def __repr__(self) -> str:
        return "HoleAexp()"

    @property
    def cost(self) -> int:
        return 3

    @property
    def children(self) -> list[Aexp]:
        return []

    @property
    def terminated(self) -> bool:
        return False


class Add(Aexp):
    a: Aexp
    b: Aexp

    def __init__(self, a: Aexp | None = None, b: Aexp | None = None) -> None:
        self.a = a or HoleAexp()
        self.b = b or HoleAexp()

    def __str__(self) -> str:
        return f"{self.a} + {self.b}"

    def __repr__(self) -> str:
        return f"Add({self.a!r}, {self.b!r})"

    @property
    def cost(self) -> int:
        return self.a.cost + self.b.cost + 3

    @property
    def children(self) -> list[Aexp]:
        return [self.a, self.b]


class Sub(Aexp):
    a: Aexp
    b: Aexp

    def __init__(self, a: Aexp | None = None, b: Aexp | None = None) -> None:
        self.a = a or HoleAexp()
        self.b = b or HoleAexp()

    def __str__(self) -> str:
        return f"{self.a} - {self.b}"

    def __repr__(self) -> str:
        return f"Sub({self.a!r}, {self.b!r})"

    @property
    def cost(self) -> int:
        return self.a.cost + self.b.cost + 3

    @property
    def children(self) -> list[Aexp]:
        return [self.a, self.b]


class Mul(Aexp):
    a: Aexp
    b: Aexp

    def __init__(self, a: Aexp | None = None, b: Aexp | None = None) -> None:
        self.a = a or HoleAexp()
        self.b = b or HoleAexp()

    def __str__(self) -> str:
        return f"{self.a} * {self.b}"

    def __repr__(self) -> str:
        return f"Mul({self.a!r}, {self.b!r})"

    @property
    def cost(self) -> int:
        return self.a.cost + self.b.cost + 3

    @property
    def children(self) -> list[Aexp]:
        return [self.a, self.b]


class Div(Aexp):
    a: Aexp
    b: Aexp

    def __init__(self, a: Aexp | None = None, b: Aexp | None = None) -> None:
        self.a = a or HoleAexp()
        self.b = b or HoleAexp()

    def __str__(self) -> str:
        return f"{self.a} // {self.b}"

    def __repr__(self) -> str:
        return f"Div({self.a!r}, {self.b!r})"

    @property
    def cost(self) -> int:
        return self.a.cost + self.b.cost + 3

    @property
    def children(self) -> list[Aexp]:
        return [self.a, self.b]


class Gate(ABC):
    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass

    @property
    @abstractmethod
    def cost(self) -> int:
        pass

    @property
    @abstractmethod
    def children(self) -> list[Aexp]:
        pass

    @property
    def depth(self) -> int:
        children = self.children
        return 1 + (
            max([child.depth for child in children]) if len(children) > 0 else 0
        )

    @property
    def terminated(self) -> bool:
        for aexp in self.children:
            if not aexp.terminated:
                return False
        return True

    def copy(self) -> Gate:
        return self.__class__(*[child.copy() for child in self.children])


class HoleGate(Gate):
    def __str__(self) -> str:
        return "□_g"

    def __repr__(self) -> str:
        return "HoleGate()"

    @property
    def cost(self) -> int:
        return 3

    @property
    def children(self) -> list[Aexp]:
        return []

    @property
    def terminated(self) -> bool:
        return False


class H(Gate):
    qreg: Aexp

    def __init__(self, qreg: Aexp | None = None) -> None:
        self.qreg = qreg or HoleAexp()

    def __str__(self) -> str:
        return f"qc.append(cirq.H(qbits[{self.qreg}]))"

    def __repr__(self) -> str:
        return f"H({self.qreg!r})"

    @property
    def cost(self) -> int:
        return self.qreg.cost + 2

    @property
    def children(self) -> list[Aexp]:
        return [self.qreg]


class X(Gate):
    qreg: Aexp

    def __init__(self, qreg: Aexp | None = None) -> None:
        self.qreg = qreg or HoleAexp()

    def __str__(self) -> str:
        return f"qc.append(cirq.X(qbits[{self.qreg}]))"

    def __repr__(self) -> str:
        return f"X({self.qreg!r})"

    @property
    def cost(self) -> int:
        return self.qreg.cost + 2

    @property
    def children(self) -> list[Aexp]:
        return [self.qreg]


class Ry(Gate):
    qreg: Aexp
    p: Aexp
    q: Aexp

    def __init__(
        self, qreg: Aexp | None = None, p: Aexp | None = None, q: Aexp | None = None
    ) -> None:
        self.qreg = qreg or HoleAexp()
        self.p = p or HoleAexp()
        self.q = q or HoleAexp()

    def __str__(self) -> str:
        return f"qc.append(cirq.Ry(rads=2*np.arccos(math.sqrt({self.p}/{self.q}))))(qbits[{self.qreg}])"

    def __repr__(self) -> str:
        return f"Ry({self.qreg!r}, {self.p!r}, {self.q!r})"

    @property
    def cost(self) -> int:
        return self.qreg.cost + self.p.cost + self.q.cost + 2

    @property
    def children(self) -> list[Aexp]:
        return [self.qreg, self.p, self.q]


class CX(Gate):
    qreg1: Aexp
    qreg2: Aexp

    def __init__(self, qreg1: Aexp | None = None, qreg2: Aexp | None = None) -> None:
        self.qreg1 = qreg1 or HoleAexp()
        self.qreg2 = qreg2 or HoleAexp()

    def __str__(self) -> str:
        return f"qc.append(cirq.CX(qbits[{self.qreg1}], qbits[{self.qreg2}]))"

    def __repr__(self) -> str:
        return f"CX({self.qreg1!r}, {self.qreg2!r})"

    @property
    def cost(self) -> int:
        return self.qreg1.cost + self.qreg2.cost + 2

    @property
    def children(self) -> list[Aexp]:
        return [self.qreg1, self.qreg2]


class CRy(Gate):
    qreg1: Aexp
    qreg2: Aexp
    p: Aexp
    q: Aexp

    def __init__(
        self,
        qreg1: Aexp | None = None,
        qreg2: Aexp | None = None,
        p: Aexp | None = None,
        q: Aexp | None = None,
    ) -> None:
        self.qreg1 = qreg1 or HoleAexp()
        self.qreg2 = qreg2 or HoleAexp()
        self.p = p or HoleAexp()
        self.q = q or HoleAexp()

    def __str__(self) -> str:
        return f"qc.append(cirq.Ry(rads=2*np.arccos(math.sqrt({self.p}/{self.q}))).controlled(num_controls=1)(qbits[{self.qreg1}], qbits[{self.qreg2}])"

    def __repr__(self) -> str:
        return f"CRy({self.qreg1!r}, {self.qreg2!r}, {self.p!r}, {self.q!r})"

    @property
    def cost(self) -> int:
        return self.qreg1.cost + self.qreg2.cost + self.p.cost + self.q.cost + 2

    @property
    def children(self) -> list[Aexp]:
        return [self.qreg1, self.qreg2, self.p, self.q]


class Cmd(ABC):

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass

    @property
    @abstractmethod
    def cost(self) -> int:
        pass

    @property
    @abstractmethod
    def children(self) -> list[Cmd | Gate | Aexp]:
        pass

    @property
    def depth(self) -> int:
        children = self.children
        return 1 + (
            max([child.depth for child in children]) if len(children) > 0 else 0
        )

    @property
    def terminated(self) -> bool:
        for child in self.children:
            if not child.terminated:
                return False
        return True

    def copy(self) -> Cmd:
        return self.__class__(*[child.copy() for child in self.children])


class HoleCmd(Cmd):
    def __str__(self) -> str:
        return "□_c"

    def __repr__(self) -> str:
        return "HoleCmd()"

    @property
    def cost(self) -> int:
        return 5

    @property
    def children(self) -> list[Cmd | Gate | Aexp]:
        return []

    @property
    def terminated(self) -> bool:
        return False


class SeqCmd(Cmd):
    pre: Cmd
    post: Cmd

    def __init__(self, pre: Cmd | None = None, post: Cmd | None = None) -> None:
        self.pre = pre or HoleCmd()
        self.post = post or HoleCmd()

    def __str__(self) -> str:
        return f"{self.pre}\n{self.post}"

    def __repr__(self) -> str:
        return f"SeqCmd({repr(self.pre)}, {repr(self.post)})"

    @property
    def cost(self) -> int:
        return self.pre.cost + self.post.cost + 5

    @property
    def children(self) -> list[Cmd | Gate | Aexp]:
        return [self.pre, self.post]


class ForCmd(Cmd):
    var: str
    start: Aexp
    end: Aexp
    body: Cmd

    def __init__(
        self,
        var: str,
        start: Aexp | None = None,
        end: Aexp | None = None,
        body: Cmd | None = None,
    ) -> None:
        self.var = var
        self.start = start or HoleAexp()
        self.end = end or HoleAexp()
        self.body = body or HoleCmd()

    def __str__(self) -> str:
        return f"for {self.var} in range({self.start}{self.end}):\n{indent(str(self.body), TAB)}"

    def __repr__(self) -> str:
        return f"For({self.var!r}, {self.start!r}, {self.end!r}, {self.body!r})"

    def copy(self) -> ForCmd:
        return ForCmd(self.var, self.start.copy(), self.end.copy(), self.body.copy())

    @property
    def cost(self) -> int:
        return self.start.cost + self.end.cost + self.body.cost + 3

    @property
    def children(self) -> list[Cmd | Gate | Aexp]:
        return [self.start, self.end, self.body]


class GateCmd(Cmd):
    gate: Gate

    def __init__(self, gate: Gate | None = None) -> None:
        self.gate = gate or HoleGate()

    def __str__(self) -> str:
        return str(self.gate)

    def __repr__(self) -> str:
        return f"{self.gate!r}"

    @property
    def cost(self) -> int:
        return self.gate.cost

    @property
    def children(self) -> list[Cmd | Gate | Aexp]:
        return [self.gate]


class Pgm:
    n: str
    body: Cmd

    def __init__(self, n: str, body: Cmd | None = None) -> None:
        self.n = n
        self.body = body or HoleCmd()

    def __str__(self) -> str:
        return str(self.body)

    def __repr__(self) -> str:
        return f"Pgm({repr(self.body)})"

    def __lt__(self, other: Pgm) -> bool:
        return self.cost < other.cost

    @property
    def cost(self) -> int:
        return self.body.cost

    @property
    def depth(self) -> int:
        return self.body.depth


ALL_AEXPS: list[type[Aexp]] = [
    a
    for a in globals().values()
    if isinstance(a, type) and issubclass(a, Aexp) and a != Aexp
]
ALL_GATES: list[type[Gate]] = [
    g
    for g in globals().values()
    if isinstance(g, type) and issubclass(g, Gate) and g != Gate
]
GATE_MAP: dict[str, type[Gate]] = {g.__name__: g for g in ALL_GATES}

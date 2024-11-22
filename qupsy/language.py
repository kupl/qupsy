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
    def depth(self) -> int:
        pass


class HoleAexp(Aexp):
    def __str__(self) -> str:
        return "□_a"

    def __repr__(self) -> str:
        return "HoleAexp()"

    @property
    def cost(self) -> int:
        return 3

    @property
    def depth(self) -> int:
        return 1


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
    def depth(self) -> int:
        return max(self.a.depth, self.b.depth) + 1


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
    def depth(self) -> int:
        return max(self.a.depth, self.b.depth) + 1


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
    def depth(self) -> int:
        return max(self.a.depth, self.b.depth) + 1


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
    def depth(self) -> int:
        return max(self.a.depth, self.b.depth) + 1


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
    def depth(self) -> int:
        pass


class HoleGate(Gate):
    def __str__(self) -> str:
        return "□_g"

    def __repr__(self) -> str:
        return "HoleGate()"

    @property
    def cost(self) -> int:
        return 3

    @property
    def depth(self) -> int:
        return 1


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
    def depth(self) -> int:
        return self.qreg.depth + 1


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
    def depth(self) -> int:
        return self.qreg.depth + 1


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
    def depth(self) -> int:
        return max(self.qreg.depth, self.p.depth, self.q.depth) + 1


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
    def depth(self) -> int:
        return max(self.qreg1.depth, self.qreg2.depth) + 1


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
    def depth(self) -> int:
        return max(self.qreg1.depth, self.qreg2.depth, self.p.depth, self.q.depth) + 1


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
    def depth(self) -> int:
        pass


class HoleCmd(Cmd):
    def __str__(self) -> str:
        return "□_c"

    def __repr__(self) -> str:
        return "HoleCmd()"

    @property
    def cost(self) -> int:
        return 5

    @property
    def depth(self) -> int:
        return 1


class SeqCmd(Cmd):
    pre: Cmd
    post: Cmd

    def __init__(self, pre: Cmd | None = None, post: Cmd | None = None) -> None:
        self.pre = pre or HoleCmd()
        self.post = post or HoleCmd()

    def __str__(self) -> str:
        return f"{self.pre}\n{self.post}"

    def __repr__(self) -> str:
        return f"SeqCmd({self.pre:!r}, {self.post:!r})"

    @property
    def cost(self) -> int:
        return self.pre.cost + self.post.cost + 5

    @property
    def depth(self) -> int:
        return max(self.pre.depth, self.post.depth) + 1


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

    @property
    def cost(self) -> int:
        return self.start.cost + self.end.cost + self.body.cost + 3

    @property
    def depth(self) -> int:
        return self.body.depth + 1


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
    def depth(self) -> int:
        return self.gate.depth


class Pgm:
    body: Cmd

    def __init__(self, body: Cmd | None = None) -> None:
        self.body = body or HoleCmd()

    def __str__(self) -> str:
        return str(self.body)

    def __repr__(self) -> str:
        return f"Pgm({self.body:!r})"

    def __lt__(self, other: Pgm) -> bool:
        return self.cost < other.cost

    @property
    def cost(self) -> int:
        return self.body.cost

    @property
    def depth(self) -> int:
        return self.body.depth


GATE_MAP: dict[str, type[Gate]] = {
    g.__name__: g
    for g in globals().values()
    if isinstance(g, type) and issubclass(g, Gate)
}

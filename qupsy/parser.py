from __future__ import annotations

from abc import ABC, abstractmethod

from plare.lexer import Lexer
from plare.parser import Parser
from plare.token import Token

from qupsy.language import (
    GATE_MAP,
    Aexp,
    Cmd,
    ForCmd,
    Gate,
    GateCmd,
    HoleAexp,
    HoleCmd,
    Integer,
    Pgm,
    SeqCmd,
    Var,
)


class LPAREN(Token):
    pass


class RPAREN(Token):
    pass


class COLON(Token):
    pass


class COMMA(Token):
    pass


class PLUS(Token):
    pass


class MINUS(Token):
    pass


class TIMES(Token):
    pass


class DIVIDE(Token):
    pass


class NEWLINE(Token):
    pass


class INDENT(Token):
    pass


class DEDENT(Token):
    pass


class DEF(Token):
    pass


class HOLE(Token):
    pass


class FOR(Token):
    pass


class IN(Token):
    pass


class RANGE(Token):
    pass


class ID(Token):
    def __init__(self, value: str, *, lineno: int, offset: int) -> None:
        super().__init__(value, lineno=lineno, offset=offset)
        self.value = value


class DIGIT(Token):
    def __init__(self, value: str, *, lineno: int, offset: int) -> None:
        super().__init__(value, lineno=lineno, offset=offset)
        self.value = int(value)


class Tree:
    pass


class PgmTree(Tree):
    def __init__(self, pgm: ID, n: ID, body: CmdTree) -> None:
        self.pgm = pgm.value
        self.n = n.value
        self.body = body

    @property
    def parsed(self) -> Pgm:
        return Pgm(self.n, self.body.parsed)


class CmdTree(Tree, ABC):
    @property
    @abstractmethod
    def parsed(self) -> Cmd:
        pass


class GateCmdTree(CmdTree):
    def __init__(self, gate: GateTree) -> None:
        self.gate = gate.parsed

    @property
    def parsed(self) -> Cmd:
        return GateCmd(self.gate)


class ForCmdTree(CmdTree):
    def __init__(self, var: ID, start: AexpTree, end: AexpTree, body: CmdTree):
        self.var = var.value
        self.start = start.parsed
        self.end = end.parsed
        self.body = body.parsed

    @property
    def parsed(self) -> Cmd:
        return ForCmd(self.var, self.start, self.end, self.body)


class HoleCmdTree(CmdTree):
    @property
    def parsed(self) -> Cmd:
        return HoleCmd()


class SeqCmdTree(CmdTree):
    def __init__(self, pre: CmdTree, post: CmdTree):
        self.pre = pre.parsed
        self.post = post.parsed

    @property
    def parsed(self) -> Cmd:
        return SeqCmd(self.pre, self.post)


class GateTree(Tree):
    def __init__(self, gate: ID, args: ListTree) -> None:
        self.gate = GATE_MAP[gate.value]
        self.args = args.parsed

    @property
    def parsed(self) -> Gate:
        return self.gate(*self.args)


class AexpTree(Tree, ABC):
    @property
    @abstractmethod
    def parsed(self) -> Aexp:
        pass


class HoleAexpTree(AexpTree):
    @property
    def parsed(self) -> Aexp:
        return HoleAexp()


class IntegerTree(AexpTree):
    def __init__(self, value: DIGIT) -> None:
        self.value = value.value

    @property
    def parsed(self) -> Aexp:
        return Integer(self.value)


class VarTree(AexpTree):
    def __init__(self, var: ID) -> None:
        self.var = var.value

    @property
    def parsed(self) -> Aexp:
        return Var(self.var)


class AddTree(AexpTree):
    def __init__(self, left: AexpTree, right: AexpTree) -> None:
        self.left = left.parsed
        self.right = right.parsed

    @property
    def parsed(self) -> Aexp:
        return self.left + self.right


class SubTree(AexpTree):
    def __init__(self, left: AexpTree, right: AexpTree) -> None:
        self.left = left.parsed
        self.right = right.parsed

    @property
    def parsed(self) -> Aexp:
        return self.left - self.right


class MulTree(AexpTree):
    def __init__(self, left: AexpTree, right: AexpTree) -> None:
        self.left = left.parsed
        self.right = right.parsed

    @property
    def parsed(self) -> Aexp:
        return self.left * self.right


class DivTree(AexpTree):
    def __init__(self, left: AexpTree, right: AexpTree) -> None:
        self.left = left.parsed
        self.right = right.parsed

    @property
    def parsed(self) -> Aexp:
        return self.left // self.right


class ListTree(Tree):
    def __init__(self, head: AexpTree, tail: ListTree | None = None) -> None:
        self.head = head.parsed
        self.tail = tail.parsed if tail is not None else []

    @property
    def parsed(self) -> list[Aexp]:
        return [self.head] + self.tail


class State:
    def __init__(self) -> None:
        self.indentation = [""]
        self.line_started = False
        self.line_ended = False


def indent_dedent_match(
    matched: str, state: State, lineno: int, offset: int
) -> Token | list[Token] | str:
    if state.line_started:
        return "line"
    else:
        state.line_started = True
        if matched == state.indentation[-1]:
            return "line"
        elif matched.startswith(state.indentation[-1]):
            state.indentation.append(matched)
            return INDENT(matched, lineno=lineno, offset=offset)
        else:
            dedents = list[Token]()
            while matched != state.indentation[-1]:
                state.indentation.pop()
                if len(state.indentation) == 0:
                    raise ValueError("Invalid indentation")
                dedents.append(DEDENT(matched, lineno=lineno, offset=offset))
            return dedents


def newline(matched: str, state: State, lineno: int, offset: int) -> Token | str:
    if state.line_ended:
        state.line_ended = False
        state.line_started = False
        return "start_of_line"
    else:
        state.line_ended = True
        return NEWLINE(matched, lineno=lineno, offset=offset)


def remaining_dedents(
    matched: str, state: State, lineno: int, offset: int
) -> list[Token]:
    ret = list[Token]()
    if not state.line_ended:
        state.line_ended = True
        ret.append(NEWLINE(matched, lineno=lineno, offset=offset))
    while len(state.indentation) > 1:
        state.indentation.pop()
        ret.append(DEDENT(matched, lineno=lineno, offset=offset))
    return ret


lexer: Lexer[State] | None = None


def build_lexer() -> Lexer[State]:
    global lexer

    if lexer is None:
        lexer = Lexer(
            {
                "start": [
                    (r"[ \t\n]*\n", "start_of_line"),
                    (r"", "start_of_line"),
                ],
                "start_of_line": [
                    (r"[ \t]*", indent_dedent_match),
                ],
                "line": [
                    # Whitespace is ignored
                    (r"[ \t\n]*\Z", remaining_dedents),
                    (r"[ \t\n]*\n", "end_of_line"),
                    (r"[ \t]+", "line"),
                    # Keywords
                    (r"def", DEF),
                    (r"for", FOR),
                    (r"in", IN),
                    (r"range", RANGE),
                    # Punctuation
                    (r",", COMMA),
                    (r"\(", LPAREN),
                    (r"\)", RPAREN),
                    (r":", COLON),
                    # Operators
                    (r"\+", PLUS),
                    (r"-", MINUS),
                    (r"\*", TIMES),
                    (r"//", DIVIDE),
                    # Identifiers
                    (r"[a-zA-Z][a-zA-Z0-9]*", ID),
                    # Literals
                    (r"0|([1-9][0-9]*)", DIGIT),
                    (r"_", HOLE),
                ],
                "end_of_line": [
                    (r"", newline),
                ],
            },
            State,
        )
    return lexer


parser: Parser[Tree] | None = None


def build_parser() -> Parser[Tree]:
    global parser

    if parser is None:
        parser = Parser(
            {
                "pgm": [
                    (
                        [
                            DEF,
                            ID,
                            LPAREN,
                            ID,
                            RPAREN,
                            COLON,
                            NEWLINE,
                            INDENT,
                            "cmd_seq",
                            DEDENT,
                        ],
                        PgmTree,
                        [1, 3, 8],
                    ),
                ],
                "cmd_seq": [
                    (["cmd", "cmd_seq"], SeqCmdTree, [0, 1]),
                    (["cmd"], None, [0]),
                ],
                "cmd": [
                    ([HOLE, NEWLINE], HoleCmdTree, []),
                    (
                        [
                            FOR,
                            ID,
                            IN,
                            RANGE,
                            LPAREN,
                            "aexp",
                            COMMA,
                            "aexp",
                            RPAREN,
                            COLON,
                            NEWLINE,
                            INDENT,
                            "cmd_seq",
                            DEDENT,
                        ],
                        ForCmdTree,
                        [1, 5, 7, 12],
                    ),
                    (["gate", NEWLINE], GateCmdTree, [0]),
                ],
                "gate": [
                    ([ID, LPAREN, "aexp_list", RPAREN], GateTree, [0, 2]),
                ],
                "aexp_list": [
                    (["aexp", COMMA, "aexp_list"], ListTree, [0, 2]),
                    (["aexp"], ListTree, [0]),
                ],
                "aexp": [
                    ([HOLE], HoleAexpTree, []),
                    ([DIGIT], IntegerTree, [0]),
                    ([ID], VarTree, [0]),
                    (["aexp", PLUS, "aexp"], AddTree, [0, 2]),
                    (["aexp", MINUS, "aexp"], SubTree, [0, 2]),
                    (["aexp", TIMES, "aexp"], MulTree, [0, 2]),
                    (["aexp", DIVIDE, "aexp"], DivTree, [0, 2]),
                ],
            }
        )

    return parser


def parse(source: str) -> Pgm:
    lexer = build_lexer()
    parser = build_parser()

    lexbuf = lexer.lex("start", source)
    parse_tree = parser.parse("pgm", lexbuf)

    if not isinstance(parse_tree, PgmTree):
        raise ValueError("Invalid parse tree")

    return parse_tree.parsed

from __future__ import annotations

from abc import ABC, abstractmethod

from plare.lexer import Lexer
from plare.parser import Parser
from plare.token import Token

from qupsy.language import Cmd, HoleCmd, Pgm, SeqCmd


class LPAREN(Token):
    pass


class RPAREN(Token):
    pass


class COLON(Token):
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


class ID(Token):
    def __init__(self, value: str, *, lineno: int, offset: int) -> None:
        super().__init__(value, lineno=lineno, offset=offset)
        self.value = value


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
                    #
                    (r"def", DEF),
                    (r"\(", LPAREN),
                    (r"\)", RPAREN),
                    (r":", COLON),
                    (r"[a-zA-Z][a-zA-Z0-9_]*", ID),
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
                    # TODO: ForCmdTree, GateCmdTree
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

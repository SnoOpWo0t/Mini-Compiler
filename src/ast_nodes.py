from dataclasses import dataclass
from typing import Any, List, Optional, Tuple
#Abstract Syntax Tree

@dataclass
class Program:
    decls: List[Any]


@dataclass
class Function:
    ret: str
    name: str
    params: List[Tuple[str, str]]
    body: Any


@dataclass
class VarDecl:
    type: str
    name: str
    init: Optional[Any]
    line: int


@dataclass
class Block:
    stmts: List[Any]


@dataclass
class ExprStmt:
    expr: Any


@dataclass
class If:
    cond: Any
    then: Any
    els: Optional[Any]


@dataclass
class While:
    cond: Any
    body: Any


@dataclass
class For:
    init: Optional[Any]
    cond: Optional[Any]
    step: Optional[Any]
    body: Any


@dataclass
class Return:
    value: Optional[Any]


@dataclass
class Printf:
    args: List[Any]


@dataclass
class Assign:
    name: str
    value: Any


@dataclass
class BinOp:
    op: str
    left: Any
    right: Any


@dataclass
class Unary:
    op: str
    expr: Any


@dataclass
class Call:
    name: str
    args: List[Any]


@dataclass
class ArrayDecl:
    type: str
    name: str
    size: int
    line: int


@dataclass
class ArrayRef:
    """Array element read used as an expression:  a[i]"""
    name: str
    index: Any


@dataclass
class ArrayAssign:
    """Array element write:  a[i] = expr"""
    name: str
    index: Any
    value: Any


@dataclass
class Var:
    name: str


@dataclass
class IntLit:
    value: int


@dataclass
class FloatLit:
    value: float


@dataclass
class StringLit:
    value: str


def ast_str(node, indent=0):
    pad = "  " * indent
    if not hasattr(node, "__dataclass_fields__"):
        return pad + repr(node)
    out = [pad + type(node).__name__]
    for fname in node.__dataclass_fields__:
        v = getattr(node, fname)
        if hasattr(v, "__dataclass_fields__"):
            out.append(pad + f"  {fname}:")
            out.append(ast_str(v, indent + 2))
        elif isinstance(v, list):
            if not v:
                out.append(pad + f"  {fname}: []")
                continue
            out.append(pad + f"  {fname}: [")
            for it in v:
                if hasattr(it, "__dataclass_fields__"):
                    out.append(ast_str(it, indent + 2))
                else:
                    out.append("  " * (indent + 2) + repr(it))
            out.append(pad + "  ]")
        else:
            out.append(pad + f"  {fname}: {v!r}")
    return "\n".join(out)

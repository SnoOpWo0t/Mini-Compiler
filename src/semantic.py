import ast_nodes as A
from symbol_table import Symbol, SymbolTable


class Semantic:
    """Phase 3 — builds scoped symbol table, checks types / scopes."""

    def __init__(self):
        self.st = SymbolTable()
        self.errors = []
        self.current_func_ret = None

    def analyze(self, prog: A.Program):
        # pass 1: collect function signatures so calls can resolve before defs
        for d in prog.decls:
            if isinstance(d, A.Function):
                ok = self.st.insert(Symbol(
                    d.name, d.ret, "func", "global", 0, params=d.params
                ))
                if not ok:
                    self.errors.append(f"Redeclaration of function {d.name!r}")
        # pass 2: walk every declaration body
        for d in prog.decls:
            self.visit(d)
        return self.errors

    def visit(self, n):
        method = getattr(self, "v_" + type(n).__name__, None)
        if method is None:
            return None
        return method(n)

    @staticmethod
    def _coercible(dst, src):
        """Implicit conversions allowed: int<->char, int->float."""
        if dst == src:
            return True
        if dst == "float" and src == "int":
            return True
        if dst == "char" and src == "int":
            return True
        if dst == "int"  and src == "char":
            return True
        return False

    # ----- declarations ------------------------------------------------------

    def v_Function(self, n: A.Function):
        self.current_func_ret = n.ret
        self.st.enter(n.name)
        for ptype, pname in n.params:
            ok = self.st.insert(Symbol(
                pname, ptype, "param", n.name, 0, address=f"param_{pname}"
            ))
            if not ok:
                self.errors.append(
                    f"Duplicate parameter {pname!r} in function {n.name!r}"
                )
        self.visit(n.body)
        self.st.exit()
        self.current_func_ret = None

    def v_ArrayDecl(self, n):
        scope = self.st.current_scope()
        addr  = f"{scope}_{n.name}"
        ok = self.st.insert(Symbol(
            n.name, n.type, "array", scope, n.line, address=addr,
            is_array=True, size=n.size,
        ))
        if not ok:
            self.errors.append(f"Line {n.line}: redeclaration of {n.name!r}")
        if n.size <= 0:
            self.errors.append(
                f"Line {n.line}: array {n.name!r} size must be positive"
            )

    def v_ArrayRef(self, n):
        sym = self.st.lookup(n.name)
        if not sym:
            self.errors.append(f"Undeclared array {n.name!r}")
            return None
        if not getattr(sym, "is_array", False):
            self.errors.append(f"{n.name!r} is not an array")
            return None
        idx_t = self.visit(n.index)
        if idx_t and idx_t not in ("int", "char"):
            self.errors.append(
                f"Array index for {n.name!r} must be int, got {idx_t}"
            )
        return sym.type   # element type

    def v_ArrayAssign(self, n):
        sym = self.st.lookup(n.name)
        if not sym:
            self.errors.append(f"Undeclared array {n.name!r}")
            return None
        if not getattr(sym, "is_array", False):
            self.errors.append(f"{n.name!r} is not an array")
            return None
        idx_t = self.visit(n.index)
        if idx_t and idx_t not in ("int", "char"):
            self.errors.append(
                f"Array index for {n.name!r} must be int, got {idx_t}"
            )
        val_t = self.visit(n.value)
        if val_t and sym.type != val_t and not self._coercible(sym.type, val_t):
            self.errors.append(
                f"Type mismatch: cannot assign {val_t} to "
                f"{sym.type}[] element {n.name!r}"
            )
        return sym.type

    def v_VarDecl(self, n: A.VarDecl):
        scope = self.st.current_scope()
        addr = f"{scope}_{n.name}"
        ok = self.st.insert(Symbol(
            n.name, n.type, "var", scope, n.line, address=addr
        ))
        if not ok:
            self.errors.append(f"Line {n.line}: redeclaration of {n.name!r}")
        if n.init is not None:
            t = self.visit(n.init)
            if t and t != n.type and not self._coercible(n.type, t):
                self.errors.append(
                    f"Line {n.line}: type mismatch: cannot assign {t} to "
                    f"{n.type} {n.name!r}"
                )

    # ----- statements --------------------------------------------------------

    def v_Block(self, n: A.Block):
        for s in n.stmts:
            self.visit(s)

    def v_ExprStmt(self, n: A.ExprStmt):
        self.visit(n.expr)

    def v_If(self, n: A.If):
        self.visit(n.cond)
        self.visit(n.then)
        if n.els is not None:
            self.visit(n.els)

    def v_While(self, n: A.While):
        self.visit(n.cond)
        self.visit(n.body)

    def v_For(self, n: A.For):
        if n.init is not None: self.visit(n.init)
        if n.cond is not None: self.visit(n.cond)
        if n.step is not None: self.visit(n.step)
        self.visit(n.body)

    def v_Return(self, n: A.Return):
        if n.value is None:
            return
        t = self.visit(n.value)
        if self.current_func_ret == "void":
            self.errors.append("void function returns a value")
        elif t and t != self.current_func_ret and not self._coercible(
            self.current_func_ret, t
        ):
            self.errors.append(
                f"Return type mismatch: expected {self.current_func_ret}, got {t}"
            )

    def v_Printf(self, n: A.Printf):
        for a in n.args:
            self.visit(a)

    # ----- expressions -------------------------------------------------------

    def v_Assign(self, n: A.Assign):
        sym = self.st.lookup(n.name)
        if not sym:
            self.errors.append(f"Undeclared identifier {n.name!r}")
            return None
        rt = self.visit(n.value)
        if rt and sym.type != rt and not self._coercible(sym.type, rt):
            self.errors.append(f"Type mismatch: {sym.type} {sym.name} = {rt}")
        return sym.type

    def v_BinOp(self, n: A.BinOp):
        lt = self.visit(n.left)
        rt = self.visit(n.right)
        if n.op in ("<", ">", "<=", ">=", "==", "!=", "&&", "||"):
            return "int"
        if "float" in (lt, rt):
            return "float"
        return lt or rt or "int"

    def v_Unary(self, n: A.Unary):
        return self.visit(n.expr)

    def v_Var(self, n: A.Var):
        sym = self.st.lookup(n.name)
        if not sym:
            self.errors.append(f"Undeclared identifier {n.name!r}")
            return None
        return sym.type

    def v_IntLit(self, n):    return "int"
    def v_FloatLit(self, n):  return "float"
    def v_StringLit(self, n): return "string"

    def v_Call(self, n: A.Call):
        sym = self.st.lookup(n.name)
        if not sym:
            self.errors.append(f"Call to undefined function {n.name!r}")
            return None
        if sym.kind != "func":
            self.errors.append(f"{n.name!r} is not a function")
            return None
        if len(n.args) != len(sym.params):
            self.errors.append(
                f"Function {sym.name!r} expects {len(sym.params)} args, "
                f"got {len(n.args)}"
            )
        for a in n.args:
            self.visit(a)
        return sym.type

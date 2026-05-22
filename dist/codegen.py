from typing import List 

import ast_nodes as A 

class TacGenerator :
    def __init__ (self ):
        self .code :List [str ]=[]
        self .tcount =0 
        self .lcount =0 

    def new_temp (self ):
        self .tcount +=1 
        return f"t{self .tcount }"

    def new_label (self ):
        self .lcount +=1 
        return f"L{self .lcount }"

    def emit (self ,*parts ):
        self .code .append (" ".join (str (p )for p in parts ))

    def gen (self ,prog :A .Program ):
        for d in prog .decls :
            self .visit (d )
        return self .code 

    def visit (self ,n ):
        return getattr (self ,"g_"+type (n ).__name__ )(n )

    def g_Function (self ,n :A .Function ):
        self .emit (f"func {n .name }:")
        for ptype ,pname in n .params :
            self .emit (f"  param {ptype } {pname }")
        self .visit (n .body )
        self .emit (f"endfunc {n .name }")

    def g_VarDecl (self ,n :A .VarDecl ):
        if n .init is not None :
            v =self .visit (n .init )
            self .emit (f"  {n .name } = {v }")
        else :
            self .emit (f"  decl {n .type } {n .name }")

    def g_ArrayDecl (self ,n ):
        self .emit (f"  decl {n .type }[{n .size }] {n .name }")

    def g_ArrayRef (self ,n ):
        idx =self .visit (n .index )
        t =self .new_temp ()
        self .emit (f"  {t } = {n .name }[{idx }]")
        return t 

    def g_ArrayAssign (self ,n ):
        idx =self .visit (n .index )
        val =self .visit (n .value )
        self .emit (f"  {n .name }[{idx }] = {val }")
        return n .name 

    def g_Block (self ,n :A .Block ):
        for s in n .stmts :
            self .visit (s )

    def g_ExprStmt (self ,n :A .ExprStmt ):
        self .visit (n .expr )

    def g_If (self ,n :A .If ):
        cond =self .visit (n .cond )
        Lelse =self .new_label ()
        Lend =self .new_label ()
        self .emit (f"  ifFalse {cond } goto {Lelse }")
        self .visit (n .then )
        self .emit (f"  goto {Lend }")
        self .emit (f"{Lelse }:")
        if n .els is not None :
            self .visit (n .els )
        self .emit (f"{Lend }:")

    def g_While (self ,n :A .While ):
        Lstart =self .new_label ()
        Lend =self .new_label ()
        self .emit (f"{Lstart }:")
        c =self .visit (n .cond )
        self .emit (f"  ifFalse {c } goto {Lend }")
        self .visit (n .body )
        self .emit (f"  goto {Lstart }")
        self .emit (f"{Lend }:")

    def g_For (self ,n :A .For ):
        if n .init is not None :
            self .visit (n .init )
        Lstart =self .new_label ()
        Lend =self .new_label ()
        self .emit (f"{Lstart }:")
        if n .cond is not None :
            c =self .visit (n .cond )
            self .emit (f"  ifFalse {c } goto {Lend }")
        self .visit (n .body )
        if n .step is not None :
            self .visit (n .step )
        self .emit (f"  goto {Lstart }")
        self .emit (f"{Lend }:")

    def g_Return (self ,n :A .Return ):
        if n .value is not None :
            v =self .visit (n .value )
            self .emit (f"  return {v }")
        else :
            self .emit ("  return")

    def g_Printf (self ,n :A .Printf ):
        for a in n .args :
            v =self .visit (a )
            self .emit (f"  print {v }")

    def g_Assign (self ,n :A .Assign ):
        v =self .visit (n .value )
        self .emit (f"  {n .name } = {v }")
        return n .name 

    def g_BinOp (self ,n :A .BinOp ):
        l =self .visit (n .left )
        r =self .visit (n .right )
        t =self .new_temp ()
        self .emit (f"  {t } = {l } {n .op } {r }")
        return t 

    def g_Unary (self ,n :A .Unary ):
        e =self .visit (n .expr )
        t =self .new_temp ()
        self .emit (f"  {t } = {n .op } {e }")
        return t 

    def g_Var (self ,n :A .Var ):
        return n .name 

    def g_IntLit (self ,n :A .IntLit ):
        return str (n .value )

    def g_FloatLit (self ,n :A .FloatLit ):
        return str (n .value )

    def g_StringLit (self ,n :A .StringLit ):
        return n .value 

    def g_Call (self ,n :A .Call ):
        args =[self .visit (a )for a in n .args ]
        for a in args :
            self .emit (f"  push {a }")
        t =self .new_temp ()
        self .emit (f"  {t } = call {n .name }, {len (args )}")
        return t 

OP_TO_ASM ={
"+":"ADD","-":"SUB","*":"MUL","/":"DIV","%":"MOD",
"<":"CMPLT",">":"CMPGT","<=":"CMPLE",">=":"CMPGE",
"==":"CMPEQ","!=":"CMPNE","&&":"AND","||":"OR",
}

def tac_to_asm (tac ):
    asm =[]
    for line in tac :
        s =line .strip ()
        if not s :
            continue 

        if s .endswith (":")and not s .startswith ("func "):
            asm .append (s )
            continue 

        if s .startswith ("func "):
            asm .append ("")
            asm .append (s [5 :].rstrip (":")+":")
            asm .append ("  PUSH BP")
            asm .append ("  MOV BP, SP")
            continue 

        if s .startswith ("endfunc"):
            asm .append ("  POP BP")
            asm .append ("  RET")
            continue 

        if s .startswith ("param "):
            asm .append (f"  ; {s }")
            continue 

        if s .startswith ("decl "):
            asm .append (f"  ; {s }")
            continue 

        if s .startswith ("ifFalse"):
            _ ,var ,_ ,lbl =s .split ()
            asm .append (f"  MOV AX, {var }")
            asm .append (f"  CMP AX, 0")
            asm .append (f"  JE {lbl }")
            continue 

        if s .startswith ("goto"):
            asm .append (f"  JMP {s .split ()[1 ]}")
            continue 

        if s .startswith ("return"):
            parts =s .split (maxsplit =1 )
            if len (parts )>1 :
                asm .append (f"  MOV AX, {parts [1 ]}")
            asm .append ("  POP BP")
            asm .append ("  RET")
            continue 

        if s .startswith ("print "):
            asm .append (f"  MOV AX, {s [6 :]}")
            asm .append ("  CALL print")
            continue 

        if s .startswith ("push "):
            asm .append (f"  PUSH {s [5 :]}")
            continue 

        if "="in s :
            lhs ,rhs =[p .strip ()for p in s .split ("=",1 )]

            if rhs .startswith ("call "):
                _ ,rest =rhs .split (" ",1 )
                fname ,nargs =[x .strip ()for x in rest .split (",")]
                asm .append (f"  CALL {fname }")
                if int (nargs )>0 :
                    asm .append (f"  ADD SP, {int (nargs )*4 }")
                asm .append (f"  MOV {lhs }, AX")
                continue 

            parts =rhs .split ()
            if len (parts )==1 :
                asm .append (f"  MOV AX, {parts [0 ]}")
                asm .append (f"  MOV {lhs }, AX")
            elif len (parts )==2 :
                op ,a =parts 
                if op =="-":
                    asm .append (f"  MOV AX, 0")
                    asm .append (f"  SUB AX, {a }")
                else :
                    asm .append (f"  MOV AX, {a }")
                    asm .append (f"  NOT AX")
                asm .append (f"  MOV {lhs }, AX")
            elif len (parts )==3 :
                a ,op ,b =parts 
                mnem =OP_TO_ASM .get (op ,"OP_"+op )
                asm .append (f"  MOV AX, {a }")
                asm .append (f"  MOV BX, {b }")
                asm .append (f"  {mnem } AX, BX")
                asm .append (f"  MOV {lhs }, AX")
            else :
                asm .append (f"  ; {s }")
            continue 

        asm .append (f"  ; {s }")
    return asm 

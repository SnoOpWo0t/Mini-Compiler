import ply .yacc as yacc 

from lexer import tokens 
import ast_nodes as A 

syntax_errors =[]

precedence =(
("right","ASSIGN"),
("left","OR"),
("left","AND"),
("nonassoc","EQ","NE"),
("nonassoc","LT","GT","LE","GE"),
("left","PLUS","MINUS"),
("left","MUL","DIV","MOD"),
("right","UMINUS","NOT"),
("left","LPAREN"),
)

def p_program (p ):
    "program : decl_list"
    p [0 ]=A .Program (decls =p [1 ])

def p_decl_list_many (p ):
    "decl_list : decl_list top_decl"
    p [1 ].append (p [2 ])
    p [0 ]=p [1 ]

def p_decl_list_empty (p ):
    "decl_list :"
    p [0 ]=[]

def p_top_decl_func (p ):
    "top_decl : type ID LPAREN param_list_opt RPAREN block"
    p [0 ]=A .Function (ret =p [1 ],name =p [2 ],params =p [4 ],body =p [6 ])

def p_top_decl_var (p ):
    "top_decl : type ID SEMI"
    p [0 ]=A .VarDecl (type =p [1 ],name =p [2 ],init =None ,line =p .lineno (2 ))

def p_top_decl_var_init (p ):
    "top_decl : type ID ASSIGN expr SEMI"
    p [0 ]=A .VarDecl (type =p [1 ],name =p [2 ],init =p [4 ],line =p .lineno (2 ))

def p_top_decl_array (p ):
    "top_decl : type ID LBRACKET NUMBER RBRACKET SEMI"
    p [0 ]=A .ArrayDecl (type =p [1 ],name =p [2 ],size =p [4 ],line =p .lineno (2 ))

def p_type (p ):
    """type : INT
            | FLOAT
            | VOID
            | CHAR
            | STR_TYPE"""
    p [0 ]=p [1 ]

def p_param_list_opt_empty (p ):
    "param_list_opt :"
    p [0 ]=[]

def p_param_list_opt_some (p ):
    "param_list_opt : param_list"
    p [0 ]=p [1 ]

def p_param_list_one (p ):
    "param_list : param"
    p [0 ]=[p [1 ]]

def p_param_list_many (p ):
    "param_list : param_list COMMA param"
    p [1 ].append (p [3 ])
    p [0 ]=p [1 ]

def p_param (p ):
    "param : type ID"
    p [0 ]=(p [1 ],p [2 ])

def p_block (p ):
    "block : LBRACE stmt_list RBRACE"
    p [0 ]=A .Block (stmts =p [2 ])

def p_stmt_list_empty (p ):
    "stmt_list :"
    p [0 ]=[]

def p_stmt_list_many (p ):
    "stmt_list : stmt_list stmt"
    p [1 ].append (p [2 ])
    p [0 ]=p [1 ]

def p_stmt (p ):
    """stmt : decl_stmt
            | expr_stmt
            | if_stmt
            | while_stmt
            | for_stmt
            | return_stmt
            | printf_stmt
            | block"""
    p [0 ]=p [1 ]

def p_decl_stmt (p ):
    "decl_stmt : type ID SEMI"
    p [0 ]=A .VarDecl (type =p [1 ],name =p [2 ],init =None ,line =p .lineno (2 ))

def p_decl_stmt_init (p ):
    "decl_stmt : type ID ASSIGN expr SEMI"
    p [0 ]=A .VarDecl (type =p [1 ],name =p [2 ],init =p [4 ],line =p .lineno (2 ))

def p_decl_stmt_array (p ):
    "decl_stmt : type ID LBRACKET NUMBER RBRACKET SEMI"
    p [0 ]=A .ArrayDecl (type =p [1 ],name =p [2 ],size =p [4 ],line =p .lineno (2 ))

def p_expr_stmt (p ):
    "expr_stmt : expr SEMI"
    p [0 ]=A .ExprStmt (expr =p [1 ])

def p_if_stmt (p ):
    "if_stmt : IF LPAREN expr RPAREN stmt"
    p [0 ]=A .If (cond =p [3 ],then =p [5 ],els =None )

def p_if_else (p ):
    "if_stmt : IF LPAREN expr RPAREN stmt ELSE stmt"
    p [0 ]=A .If (cond =p [3 ],then =p [5 ],els =p [7 ])

def p_while_stmt (p ):
    "while_stmt : WHILE LPAREN expr RPAREN stmt"
    p [0 ]=A .While (cond =p [3 ],body =p [5 ])

def p_for_stmt (p ):
    "for_stmt : FOR LPAREN for_init for_cond_opt SEMI for_step_opt RPAREN stmt"
    p [0 ]=A .For (init =p [3 ],cond =p [4 ],step =p [6 ],body =p [8 ])

def p_for_init_decl (p ):
    "for_init : decl_stmt"
    p [0 ]=p [1 ]

def p_for_init_expr (p ):
    "for_init : expr SEMI"
    p [0 ]=A .ExprStmt (expr =p [1 ])

def p_for_init_empty (p ):
    "for_init : SEMI"
    p [0 ]=None 

def p_for_cond_opt_some (p ):
    "for_cond_opt : expr"
    p [0 ]=p [1 ]

def p_for_cond_opt_none (p ):
    "for_cond_opt :"
    p [0 ]=None 

def p_for_step_opt_some (p ):
    "for_step_opt : expr"
    p [0 ]=p [1 ]

def p_for_step_opt_none (p ):
    "for_step_opt :"
    p [0 ]=None 

def p_return_stmt (p ):
    "return_stmt : RETURN SEMI"
    p [0 ]=A .Return (value =None )

def p_return_stmt_val (p ):
    "return_stmt : RETURN expr SEMI"
    p [0 ]=A .Return (value =p [2 ])

def p_printf_stmt (p ):
    "printf_stmt : PRINTF LPAREN arg_list RPAREN SEMI"
    p [0 ]=A .Printf (args =p [3 ])

def p_arg_list_one (p ):
    "arg_list : expr"
    p [0 ]=[p [1 ]]

def p_arg_list_many (p ):
    "arg_list : arg_list COMMA expr"
    p [1 ].append (p [3 ])
    p [0 ]=p [1 ]

def p_expr_assign (p ):
    "expr : ID ASSIGN expr"
    p [0 ]=A .Assign (name =p [1 ],value =p [3 ])

def p_expr_array_assign (p ):
    "expr : ID LBRACKET expr RBRACKET ASSIGN expr"
    p [0 ]=A .ArrayAssign (name =p [1 ],index =p [3 ],value =p [6 ])

def p_expr_array_ref (p ):
    "expr : ID LBRACKET expr RBRACKET"
    p [0 ]=A .ArrayRef (name =p [1 ],index =p [3 ])

def p_expr_binop (p ):
    """expr : expr PLUS expr
            | expr MINUS expr
            | expr MUL expr
            | expr DIV expr
            | expr MOD expr
            | expr LT expr
            | expr GT expr
            | expr LE expr
            | expr GE expr
            | expr EQ expr
            | expr NE expr
            | expr AND expr
            | expr OR expr"""
    p [0 ]=A .BinOp (op =p [2 ],left =p [1 ],right =p [3 ])

def p_expr_uminus (p ):
    "expr : MINUS expr %prec UMINUS"
    p [0 ]=A .Unary (op ="-",expr =p [2 ])

def p_expr_not (p ):
    "expr : NOT expr"
    p [0 ]=A .Unary (op ="!",expr =p [2 ])

def p_expr_paren (p ):
    "expr : LPAREN expr RPAREN"
    p [0 ]=p [2 ]

def p_expr_number (p ):
    "expr : NUMBER"
    p [0 ]=A .IntLit (value =p [1 ])

def p_expr_fnum (p ):
    "expr : FNUM"
    p [0 ]=A .FloatLit (value =p [1 ])

def p_expr_string (p ):
    "expr : STRING"
    p [0 ]=A .StringLit (value =p [1 ])

def p_expr_call (p ):
    "expr : ID LPAREN args_opt RPAREN"
    p [0 ]=A .Call (name =p [1 ],args =p [3 ])

def p_expr_var (p ):
    "expr : ID"
    p [0 ]=A .Var (name =p [1 ])

def p_args_opt_some (p ):
    "args_opt : arg_list"
    p [0 ]=p [1 ]

def p_args_opt_none (p ):
    "args_opt :"
    p [0 ]=[]

def p_error (p ):
    if p is None :
        syntax_errors .append ("Syntax error at end of input")
    else :
        syntax_errors .append (
        f"Line {p .lineno }: syntax error near {p .value !r } (token {p .type })"
        )

def build_parser ():
    syntax_errors .clear ()
    return yacc .yacc (debug =False ,write_tables =False ,errorlog =yacc .NullLogger ())

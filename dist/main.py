"""Mini C compiler driver.

Usage:
    python src/main.py input/test_all.c

Runs every compiler phase and writes:
    output/tokens.txt
    output/ast.txt
    output/symbol_table.txt
    output/tac.txt
    output/assembly.asm

A banner per phase is printed to stdout; full content goes to the files.
"""

import os 
import sys 

sys .path .insert (0 ,os .path .dirname (os .path .abspath (__file__ )))

from lexer import tokenize_all ,build_lexer ,render_tokens 
from parser import build_parser ,syntax_errors 
from ast_nodes import ast_str 
from semantic import Semantic 
from codegen import TacGenerator ,tac_to_asm 

HERE =os .path .dirname (os .path .abspath (__file__ ))
PROJECT =os .path .dirname (HERE )
OUT =os .path .join (PROJECT ,"output")
os .makedirs (OUT ,exist_ok =True )

def banner (title ):
    line ="="*60 
    print (f"\n{line }\n  {title }\n{line }")

def write (filename ,text ):
    path =os .path .join (OUT ,filename )
    with open (path ,"w",encoding ="utf-8")as f :
        f .write (text +"\n")
    print (text )
    print (f"\n[written to output/{filename }]")

def main ():
    if len (sys .argv )<2 :
        print ("Usage: python src/main.py <source.c>")
        sys .exit (2 )

    path =sys .argv [1 ]
    if not os .path .isfile (path ):
        print (f"Error: input file not found: {path }")
        sys .exit (2 )

    with open (path ,"r",encoding ="utf-8")as f :
        source =f .read ()

    print (f"Compiling: {path }")

    banner ("Phase 1: Lexical Analysis")
    tokenize_all (source )
    write ("tokens.txt",render_tokens ())

    banner ("Phase 2: Syntax Analysis (AST)")
    lexer =build_lexer ()
    parser =build_parser ()
    ast =parser .parse (source ,lexer =lexer )

    if syntax_errors :
        for e in syntax_errors :
            print (f"  syntax error: {e }")
        write ("ast.txt","Parsing failed.\n"+"\n".join (syntax_errors ))
        print ("Parsing Failed")
        sys .exit (1 )
    write ("ast.txt",ast_str (ast ))
    print ("Parsing Successful")

    banner ("Phase 3: Semantic Analysis + Symbol Table")
    sem =Semantic ()
    sem_errors =sem .analyze (ast )
    sym_text =sem .st .render ()
    if sem_errors :
        sym_text +="\n\nSemantic Errors:\n"
        for e in sem_errors :
            sym_text +=f"  - {e }\n"
    write ("symbol_table.txt",sym_text )

    if sem_errors :
        for e in sem_errors :
            print (f"  semantic error: {e }")
        print ("Compilation halted after Phase 3.")
        sys .exit (1 )
    print ("No semantic errors.")

    banner ("Phase 4: Intermediate Code (TAC)")
    gen =TacGenerator ()
    tac =gen .gen (ast )
    write ("tac.txt","\n".join (tac ))

    banner ("Phase 5: Target Code Generation (Assembly)")
    asm =tac_to_asm (tac )
    write ("assembly.asm","\n".join (asm ))

    banner ("Compilation Successful")
    print (f"All phase outputs written to: {OUT }")
    return 0 

if __name__ =="__main__":
    sys .exit (main ())

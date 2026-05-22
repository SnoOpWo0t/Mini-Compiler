class Symbol :
    __slots__ =("name","type","kind","scope","line","address",
    "params","is_array","size")

    def __init__ (self ,name ,type_ ,kind ,scope ,line ,
    address =None ,params =None ,is_array =False ,size =0 ):
        self .name =name 
        self .type =type_ 
        self .kind =kind 
        self .scope =scope 
        self .line =line 
        self .address =address 
        self .params =params or []
        self .is_array =is_array 
        self .size =size 

class SymbolTable :
    """Scoped symbol table with stack of dicts."""

    def __init__ (self ):
        self .scopes =[{}]
        self .scope_names =["global"]
        self .all =[]

    def enter (self ,name ):
        self .scopes .append ({})
        self .scope_names .append (name )

    def exit (self ):
        self .scopes .pop ()
        self .scope_names .pop ()

    def current_scope (self ):
        return self .scope_names [-1 ]

    def insert (self ,sym ):
        top =self .scopes [-1 ]
        if sym .name in top :
            return False 
        top [sym .name ]=sym 
        self .all .append (sym )
        return True 

    def lookup (self ,name ):
        for s in reversed (self .scopes ):
            if name in s :
                return s [name ]
        return None 

    def render (self ):
        out =[]
        out .append (
        f"{'Name':<14}{'Type':<10}{'Kind':<8}{'Scope':<14}"
        f"{'Line':<6}{'Size':<6}{'Addr'}"
        )
        out .append ("-"*68 )
        for s in self .all :
            addr =s .address if s .address is not None else "-"
            size =str (s .size )if s .is_array else "-"
            type_disp =f"{s .type }[]"if s .is_array else s .type 
            out .append (
            f"{s .name :<14}{type_disp :<10}{s .kind :<8}{s .scope :<14}"
            f"{s .line :<6}{size :<6}{addr }"
            )
        return "\n".join (out )

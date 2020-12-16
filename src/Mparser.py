import scanner
import ply.yacc as yacc
import AST

tokens = scanner.tokens

precedence = (
    ("nonassoc", 'IFX'),
    ("nonassoc", 'ELSE'),
    ("nonassoc", '<', '>', 'LE', 'GE', 'EQ', 'NOTEQ'),
    ("left", '+', '-', 'DOTADD', 'DOTSUB'),
    ("left", '*', '/', 'DOTDIV', 'DOTMULT'),
    ('right', 'UMINUS'),
    ('left', '\'')
)


def p_error(p):
    if p:
        print("Syntax error at line {0}: LexToken({1}, '{2}')".format(p.lineno, p.type, p.value))
    else:
        print("Unexpected end of input")


def p_program(p):
    """program : instructions_opt"""
    p[0] = p[1]

def p_instructions_opt(p):
    """instructions_opt : instructions
                        | empty"""
    p[0] = AST.Instructions(p[1])

def p_empty(p):
    """empty :"""
    p[0] = []


def p_instructions(p):
    """instructions : instructions instruction
                    | instruction"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]


def p_instruction(p):
    """instruction : loop
                   | ifelse
                   | controlflow ';'
                   | assignment ';'
                   | codeblock
                   | print ';'"""
    p[0] = p[1]


def p_print(p):
    """print : PRINT tuple"""
    p[0] = AST.Print(AST.Tuple(p[2]))
    p[0].lineno = p.lineno(1)


def p_tuple(p):
    """tuple : expr ',' tuple
             | expr"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]


def p_codeblock(p):
    """codeblock : '{' instructions_opt '}'"""
    p[0] = AST.Scope(p[2])
    p[0].lineno = p.lineno(1)


def p_controlflow(p):
    """controlflow : BREAK
                   | CONTINUE
                   | RETURN expr
                   | RETURN"""
    p[0] = AST.Controlflow(p[1])
    if len(p) == 3:
        p[0].ret_val = p[2]

    p[0].lineno = p.lineno(1)


def p_loop(p):
    """loop : forloop
            | whileloop"""
    p[0] = p[1]


def p_forloop(p):
    """forloop : FOR ID '=' range instruction"""
    p[0] = AST.ForLoop(AST.Variable(p[2]), p[4], p[5])
    p[0].lineno = p.lineno(1)


def p_range(p):
    """range : expr ':' expr"""
    p[0] = AST.Range(p[1], p[3])
    p[0].lineno = p.lineno(1)


def p_whileloop(p):
    """whileloop : WHILE '(' expr ')' instruction"""
    p[0] = AST.While(p[3], p[5])
    p[0].lineno = p.lineno(1)


def p_ifelse(p):
    """ifelse : IF '(' expr ')' instruction %prec IFX
              | IF '(' expr ')' instruction ELSE instruction"""
    p[0] = AST.IfElse(p[3], p[5])
    if len(p) == 8:
        p[0].else_instructions = p[7]
    p[0].lineno = p.lineno(1)


def p_bin_expr(p):
    """expr : expr '+' expr
            | expr '-' expr
            | expr '*' expr
            | expr '/' expr
            | expr '>' expr
            | expr '<' expr
            | expr EQ expr
            | expr LE expr
            | expr GE expr
            | expr NOTEQ expr
            | expr DOTDIV expr
            | expr DOTADD expr
            | expr DOTMULT expr
            | expr DOTSUB expr"""

    p[0] = AST.BinExpr(p[2], p[1], p[3])
    p[0].lineno = p.lineno(1)


def p_negation_expr(p):
    """expr : '-' expr %prec UMINUS"""
    p[0] = AST.Negation(p[2])
    p[0].lineno = p.lineno(2)


def p_one_expr(p):
    """expr : '(' expr ')'
            | functioncall
            | constant
            | id"""
    if len(p) == 2:
        p[0] = p[1]
        p[0].lineno = p.lineno(1)
    else:
        p[0] = p[2]
        p[0].lineno = p.lineno(2)


def p_transpose_expr(p):
    """expr : expr "'" """
    p[0] = AST.Transpose(p[1])
    p[0].lineno = p.lineno(1)


def p_functioncall(p):
    """functioncall : ZEROS '(' tuple ')'
                    | EYE '(' tuple ')'
                    | ONES '(' tuple ')'"""
    p[0] = AST.Function(p[1], AST.Tuple(p[3]))
    p[0].lineno = p.lineno(1)


def p_constant(p):
    """constant : INTNUM
             | FLOATNUM
             | STRING
             | tensor"""

    if isinstance(p[1], int):
        p[0] = AST.IntNum(p[1])
        p[0].lineno = p.lineno(1)
    elif isinstance(p[1], float):
        p[0] = AST.FloatNum(p[1])
        p[0].lineno = p.lineno(1)
    elif isinstance(p[1], str) and p[1][0] == '"':
        p[0] = AST.StringLiteral(p[1])
        p[0].lineno = p.lineno(1)
    else:
        p[0] = AST.Tensor(p[1])
        p[0].lineno = p.lineno(1)


def p_tensor(p):
    """tensor : '[' tensorelem ']'"""
    p[0] = p[2]


def p_tensorelem(p):
    """tensorelem : constant
                  | tensorelem ',' constant"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_assignment(p):
    """assignment : id '=' expr
                  | id ADDASSIGN expr
                  | id SUBASSIGN expr
                  | id MULASSIGN expr
                  | id DIVASSIGN expr"""
    p[0] = AST.Assignment(p[1], p[2], p[3])
    p[0].lineno = p.lineno(2)


def p_id(p):
    """id    : ID
             | ID '[' index ']'"""
    if len(p) == 2:
        p[0] = AST.Variable(p[1])
    else:
        p[0] = AST.Variable(p[1], index=AST.Index(p[3]))
    p[0].lineno = p.lineno(1)


def p_index(p):
    """index : expr
             | expr ',' index"""
    p[0] = [p[1]]
    if len(p) == 4:
        p[0] += p[3]


parser = yacc.yacc()
scanner = scanner.lexer


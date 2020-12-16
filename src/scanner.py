import ply.lex as lex

reserved = {
    'if': 'IF',
    'else': 'ELSE',
    'for': 'FOR',
    'while': 'WHILE',
    'break': 'BREAK',
    'continue': 'CONTINUE',
    'return': 'RETURN',
    'print': 'PRINT',
    'zeros': 'ZEROS',
    'eye': 'EYE',
    'ones': 'ONES',
}

literals = [
    '+',
    '-',
    '*',
    '/',
    '=',
    '(',
    ')',
    '[',
    ']',
    '{',
    '}',
    "'",
    ';',
    ',',
    '>',
    '<',
    ':'
]

tokens = [
    'LE',
    'GE',
    'EQ',
    'NOTEQ',
    'DOTDIV', #./
    'DOTADD', #.+
    'DOTMULT', #.*
    'DOTSUB', #.-
    'ADDASSIGN',
    'SUBASSIGN',
    'MULASSIGN',
    'DIVASSIGN',
    'ID',
    'FLOATNUM',
    'INTNUM',
    'STRING',
] + list(reserved.values())


t_DOTDIV = r'\./'
t_DOTMULT = r'\.\*'
t_DOTADD = r'\.\+'
t_DOTSUB = r'\.-'
t_LE = r'<='
t_GE = r'>='
t_EQ = r'=='
t_NOTEQ = r'!='
t_ADDASSIGN = r'\+='
t_SUBASSIGN = r'-='
t_MULASSIGN = r'\*='
t_DIVASSIGN = r'/='

def t_ID(t):
    r'[a-zA-Z_]\w*'
    t.type = reserved[t.value] if t.value in reserved else 'ID'
    return t


def t_FLOATNUM(t):
    r'(([1-9][0-9]*|0)\.[0-9]*|\.[0-9]+)(E[0-9]+)?'
    t.value = float(t.value)
    return t


def t_INTNUM(t):
    r'(0|[1-9][0-9]*)(E[0-9]+)?'
    t.value = int(t.value)
    return t


def t_STRING(t):
    r'"[^"]*"'
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore = ' \t'


def t_COMMENT(t):
    r'\#.*'
    pass


# Error handling rule
def t_error(t):
    print(f'Invalid character at line {t.lexer.lineno}')
    print(t.value[:t.value.find('\n')])
    print('^')
    t.lexer.skip(1)


def find_column(text, token):
    line_start = text.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1


lexer = lex.lex()

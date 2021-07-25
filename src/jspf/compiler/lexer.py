from enum import Enum
import re

class Token(Enum):
    UNEXPECTED          = 0
    WHITESPACE          = 1
    NAV                 = 2
    VAL                 = 3
    ROOT                = 4
    REGEX               = 5
    STR_MATCH           = 6
    SET_MATCH           = 7
    SELECT_BEGIN        = 8
    SELECT_END          = 9
    CAP_BEGIN           = 10
    CAP_END             = 11
    NONCAP_POS_BEGIN    = 12
    NONCAP_POS_END      = 13
    NONCAP_NEG_BEGIN    = 14
    NONCAP_NEG_END      = 15
    UNION               = 16
    # Quantifiers are not supported yet
    GREEDY_OPTIONAL     = 0
    GREEDY_ANY          = 0
    GREEDY_EXIST        = 0
    LAZY_OPTIONAL       = 0
    LAZY_ANY            = 0
    LAZY_EXIST          = 0

class Flag(Enum):
    NONE = 0
    CAP_ENABLE = 1
    NONCAP_POS_ENABLE = 2
    NONCAP_NEG_ENABLE = 3

WHITESPACE_RE = re.compile(r'\s+')

def consume_until(prog, idx, ch):
    escape = False
    for i in range(idx+1, len(prog)):
        if escape:
            escape = False
        elif prog[i] == '\\':
            escape = True
        elif prog[i] == ch:
            return (prog[idx:i+1], i+1)
    return None, None

def parse_nav(prog, idx, flag):
    token_type = Token.NAV
    lexeme = '.'
    next_idx = idx+1
    return (token_type, lexeme, next_idx)

def parse_val(prog, idx, flag):
    token_type = Token.VAL
    lexeme = '$'
    next_idx = idx+1
    return (token_type, lexeme, next_idx)

def parse_root(prog, idx, flag):
    token_type = Token.ROOT
    lexeme = '^'
    next_idx = idx+1
    return (token_type, lexeme, next_idx)

def parse_regex(prog, idx, flag):
    token_type = Token.REGEX
    lexeme, next_idx = consume_until(prog, idx, '/')
    if lexeme is None:
        token_type = Token.UNEXPECTED
    return (token_type, lexeme, next_idx)

def parse_str_match(prog, idx, flag):
    token_type = Token.STR_MATCH
    lexeme, next_idx = consume_until(prog, idx, ']')
    if lexeme is None:
        token_type = Token.UNEXPECTED
    return (token_type, lexeme, next_idx)

def parse_set_match(prog, idx, flag):
    token_type = Token.SET_MATCH
    lexeme, next_idx = consume_until(prog, idx, '}')
    if lexeme is None:
        token_type = Token.UNEXPECTED
    return (token_type, lexeme, next_idx)

def parse_select(prog, idx, flag):
    ch = prog[idx]
    (token_type, lexeme, next_idx) = (None, None, None)
    if ch == '<':
        token_type = Token.SELECT_BEGIN
        lexeme = '<'
        next_idx = idx+1
    else:
        token_type = Token.SELECT_END
        lexeme = '>'
        next_idx = idx+1
    return (token_type, lexeme, next_idx)

def parse_bracket_begin(prog, idx, flag):
    (token_type, lexeme, next_idx) = (None, None, None)
    look_ahead = len(prog) > idx+3
    if look_ahead and prog[idx:idx+3] == '(?=':
        token_type = Token.NONCAP_POS_BEGIN
        lexeme = '(?='
        next_idx = idx+3
    elif look_ahead and prog[idx:idx+3] == '(?!':
        token_type = Token.NONCAP_NEG_BEGIN
        lexeme = '(?!'
        next_idx = idx+3
    else:
        token_type = Token.CAP_BEGIN
        lexeme = '('
        next_idx = idx+1
    return (token_type, lexeme, next_idx)

def parse_bracket_end(prog, idx, flag):
    (token_type, lexeme, next_idx) = (None, None, None)
    lexeme = ')'
    next_idx = idx+1
    if flag == Flag.CAP_ENABLE:
        token_type = Token.CAP_END
    elif flag == Flag.NONCAP_POS_ENABLE:
        token_type = Token.NONCAP_POS_END
    elif flag == Flag.NONCAP_NEG_ENABLE:
        token_type = Token.NONCAP_NEG_END
    else:
        token_type = Token.UNEXPECTED
    return (token_type, lexeme, next_idx)

def parse_union(prog, idx, flag):
    token_type = Token.UNION
    lexeme = '|'
    next_idx = idx+1
    return (token_type, lexeme, next_idx)

def parse_quantifier_optional(prog, idx, flag):
    (token_type, lexeme, next_idx) = (None, None, None)
    look_ahead = len(prog) > idx+2
    if look_ahead and prog[idx:idx+2] == '??':
        token_type = Token.LAZY_OPTIONAL
        lexeme = '??'
        next_idx = idx+2
    else:
        token_type = Token.GREEDY_OPTIONAL
        lexeme = '?'
        next_idx = idx+1
    return (token_type, lexeme, next_idx)

def parse_quantifier_any(prog, idx, flag):
    (token_type, lexeme, next_idx) = (None, None, None)
    look_ahead = len(prog) > idx+2
    if look_ahead and prog[idx:idx+2] == '*?':
        token_type = Token.LAZY_OPTIONAL
        lexeme = '*?'
        next_idx = idx+2
    else:
        token_type = Token.GREEDY_OPTIONAL
        lexeme = '*'
        next_idx = idx+1
    return (token_type, lexeme, next_idx)

def parse_quantifier_exist(prog, idx, flag):
    (token_type, lexeme, next_idx) = (None, None, None)
    look_ahead = len(prog) > idx+2
    if look_ahead and prog[idx:idx+2] == '+?':
        token_type = Token.LAZY_OPTIONAL
        lexeme = '+?'
        next_idx = idx+2
    else:
        token_type = Token.GREEDY_OPTIONAL
        lexeme = '+'
        next_idx = idx+1
    return (token_type, lexeme, next_idx)

PARSERS = {
    '.': parse_nav,
    '$': parse_val,
    '^': parse_root,
    '/': parse_regex,
    '[': parse_str_match,
    '{': parse_set_match,
    '<': parse_select,
    '>': parse_select,
    '(': parse_bracket_begin,
    ')': parse_bracket_end,
    '|': parse_union,
    '?': parse_quantifier_optional,
    '*': parse_quantifier_any,
    '+': parse_quantifier_exist,
}

def advance(prog, idx, flag):
    '''
    Analyze the next token in prog[idx:] and return the characters consumed.

    Returns a 3-tuple (token_type, lexeme, next_idx)
    '''
    m = WHITESPACE_RE.match(prog, idx)
    if m is not None:
        return (Token.WHITESPACE, m[0], idx+len(m[0]))

    parser_f = PARSERS.get(prog[idx], None)
    if parser_f is None:
        return (Token.UNEXPECTED, None, None)

    return parser_f(prog, idx, flag)

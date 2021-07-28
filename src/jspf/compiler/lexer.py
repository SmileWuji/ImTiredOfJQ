from jspf.compiler.CompilerError import CompilerError
from enum import Enum
import re

class TokenType(Enum):
    INVALID             = 0
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
    DEFAULT_OPTIONAL    = 17
    DEFAULT_ANY         = 18
    DEFAULT_EXIST       = 19
    GREEDY_OPTIONAL     = 20
    GREEDY_ANY          = 21
    GREEDY_EXIST        = 22
    LAZY_OPTIONAL       = 23
    LAZY_ANY            = 24
    LAZY_EXIST          = 25

class Flag(Enum):
    NONE                = 0
    CAP_ENABLE          = 1
    NONCAP_POS_ENABLE   = 2
    NONCAP_NEG_ENABLE   = 3

class Token:
    def __init__(self, prog, token_type, lexeme, prog_idx):
        super().__init__()
        self.prog = prog
        self.token_type = token_type
        self.lexeme = lexeme
        self.prog_idx = prog_idx

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {str(self.token_type): self.lexeme}

WHITESPACE_RE = re.compile(r'\s+')

BRACKET_END_TOKENS = {TokenType.CAP_END,
                      TokenType.NONCAP_POS_END,
                      TokenType.NONCAP_NEG_END}

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

def tokenize_nav(prog, idx, flag):
    token_type = TokenType.NAV
    lexeme = '.'
    next_idx = idx+1
    return (token_type, lexeme, next_idx)

def tokenize_val(prog, idx, flag):
    token_type = TokenType.VAL
    lexeme = '$'
    next_idx = idx+1
    return (token_type, lexeme, next_idx)

def tokenize_root(prog, idx, flag):
    token_type = TokenType.ROOT
    lexeme = '^'
    next_idx = idx+1
    return (token_type, lexeme, next_idx)

def tokenize_regex(prog, idx, flag):
    token_type = TokenType.REGEX
    lexeme, next_idx = consume_until(prog, idx, '/')
    if lexeme is None:
        token_type = TokenType.INVALID
    return (token_type, lexeme, next_idx)

def tokenize_str_match(prog, idx, flag):
    token_type = TokenType.STR_MATCH
    lexeme, next_idx = consume_until(prog, idx, ']')
    if lexeme is None:
        token_type = TokenType.INVALID
    return (token_type, lexeme, next_idx)

def tokenize_set_match(prog, idx, flag):
    token_type = TokenType.SET_MATCH
    lexeme, next_idx = consume_until(prog, idx, '}')
    if lexeme is None:
        token_type = TokenType.INVALID
    return (token_type, lexeme, next_idx)

def tokenize_select(prog, idx, flag):
    ch = prog[idx]
    (token_type, lexeme, next_idx) = (None, None, None)
    if ch == '<':
        token_type = TokenType.SELECT_BEGIN
        lexeme = '<'
        next_idx = idx+1
    else:
        token_type = TokenType.SELECT_END
        lexeme = '>'
        next_idx = idx+1
    return (token_type, lexeme, next_idx)

def tokenize_bracket_begin(prog, idx, flag):
    (token_type, lexeme, next_idx) = (None, None, None)
    look_ahead = len(prog) > idx+3
    if look_ahead and prog[idx:idx+3] == '(?=':
        token_type = TokenType.NONCAP_POS_BEGIN
        lexeme = '(?='
        next_idx = idx+3
    elif look_ahead and prog[idx:idx+3] == '(?!':
        token_type = TokenType.NONCAP_NEG_BEGIN
        lexeme = '(?!'
        next_idx = idx+3
    else:
        token_type = TokenType.CAP_BEGIN
        lexeme = '('
        next_idx = idx+1
    return (token_type, lexeme, next_idx)

def tokenize_bracket_end(prog, idx, flag):
    (token_type, lexeme, next_idx) = (None, None, None)
    lexeme = ')'
    next_idx = idx+1
    if flag == Flag.CAP_ENABLE:
        token_type = TokenType.CAP_END
    elif flag == Flag.NONCAP_POS_ENABLE:
        token_type = TokenType.NONCAP_POS_END
    elif flag == Flag.NONCAP_NEG_ENABLE:
        token_type = TokenType.NONCAP_NEG_END
    else:
        token_type = TokenType.INVALID
    return (token_type, lexeme, next_idx)

def tokenize_union(prog, idx, flag):
    token_type = TokenType.UNION
    lexeme = '|'
    next_idx = idx+1
    return (token_type, lexeme, next_idx)

def tokenize_quantifier_optional(prog, idx, flag):
    (token_type, lexeme, next_idx) = (None, None, None)
    look_ahead = len(prog) > idx+2
    if look_ahead and prog[idx:idx+2] == '??':
        token_type = TokenType.LAZY_OPTIONAL
        lexeme = '??'
        next_idx = idx+2
    elif look_ahead and prog[idx:idx+2] == '?+':
        token_type = TokenType.GREEDY_OPTIONAL
        lexeme = '?+'
        next_idx = idx+2
    else:
        token_type = TokenType.DEFAULT_OPTIONAL
        lexeme = '?'
        next_idx = idx+1
    return (token_type, lexeme, next_idx)

def tokenize_quantifier_any(prog, idx, flag):
    (token_type, lexeme, next_idx) = (None, None, None)
    look_ahead = len(prog) > idx+2
    if look_ahead and prog[idx:idx+2] == '*?':
        token_type = TokenType.LAZY_ANY
        lexeme = '*?'
        next_idx = idx+2
    elif look_ahead and prog[idx:idx+2] == '*+':
        token_type = TokenType.GREEDY_ANY
        lexeme = '*+'
        next_idx = idx+2
    else:
        token_type = TokenType.DEFAULT_ANY
        lexeme = '*'
        next_idx = idx+1
    return (token_type, lexeme, next_idx)

def tokenize_quantifier_exist(prog, idx, flag):
    (token_type, lexeme, next_idx) = (None, None, None)
    look_ahead = len(prog) > idx+2
    if look_ahead and prog[idx:idx+2] == '+?':
        token_type = TokenType.LAZY_EXIST
        lexeme = '+?'
        next_idx = idx+2
    elif look_ahead and prog[idx:idx+2] == '++':
        token_type = TokenType.GREEDY_EXIST
        lexeme = '++'
        next_idx = idx+2
    else:
        token_type = TokenType.DEFAULT_EXIST
        lexeme = '+'
        next_idx = idx+1
    return (token_type, lexeme, next_idx)

TOKENIZERS = {
    '.': tokenize_nav,
    '$': tokenize_val,
    '^': tokenize_root,
    '/': tokenize_regex,
    '[': tokenize_str_match,
    '{': tokenize_set_match,
    '<': tokenize_select,
    '>': tokenize_select,
    '(': tokenize_bracket_begin,
    ')': tokenize_bracket_end,
    '|': tokenize_union,
    '?': tokenize_quantifier_optional,
    '*': tokenize_quantifier_any,
    '+': tokenize_quantifier_exist,
}

def advance(prog, idx, flag):
    '''
    Analyze the next token in prog[idx:] and return the characters consumed.

    Returns a 3-tuple (token_type, lexeme, next_idx)
    '''
    m = WHITESPACE_RE.match(prog, idx)
    if m is not None:
        return (TokenType.WHITESPACE, m[0], idx+len(m[0]))

    tokenizer_f = TOKENIZERS.get(prog[idx], None)
    if tokenizer_f is None:
        return (TokenType.INVALID, None, None)

    return tokenizer_f(prog, idx, flag)

def pass_lexer(prog):
    tokens = list()
    flags = list()
    flags.append(Flag.NONE)
    idx = 0
    while idx < len(prog):
        (token_type, lexeme, next_idx) = advance(prog, idx, flags[-1])
        if token_type == TokenType.CAP_BEGIN:
            flags.append(Flag.CAP_ENABLE)            
        elif token_type == TokenType.NONCAP_POS_BEGIN:
            flags.append(Flag.NONCAP_POS_ENABLE)
        elif token_type == TokenType.NONCAP_NEG_BEGIN:
            flags.append(Flag.NONCAP_NEG_ENABLE)
        elif token_type in BRACKET_END_TOKENS:
            flags.pop()

        if token_type == TokenType.INVALID:
            raise CompilerError('Invalid token at byte {} "{}..."'.format(
                idx,
                prog[idx:min(len(prog) ,idx+5)]))

        if token_type != TokenType.WHITESPACE:
            node = Token(prog, token_type, lexeme, idx)
            tokens.append(node)

        idx = next_idx

    return tokens

TOKEN_NAMES = {
    TokenType.NAV: '.',
    TokenType.VAL: '$',
    TokenType.ROOT: '^',
    TokenType.REGEX: '/.../',
    TokenType.STR_MATCH: '[...]',
    TokenType.SET_MATCH: '{...}',
    TokenType.SELECT_BEGIN: '<',
    TokenType.SELECT_END: '>',
    TokenType.CAP_BEGIN: '(',
    TokenType.CAP_END: ')',
    TokenType.NONCAP_POS_BEGIN: '(?=',
    TokenType.NONCAP_POS_END: ')',
    TokenType.NONCAP_NEG_BEGIN: '(?!',
    TokenType.NONCAP_NEG_END: ')',
    TokenType.UNION: '|',
    TokenType.DEFAULT_OPTIONAL: '?',
    TokenType.DEFAULT_ANY: '*',
    TokenType.DEFAULT_EXIST: '+',
    TokenType.GREEDY_OPTIONAL: '?+',
    TokenType.GREEDY_ANY: '*+',
    TokenType.GREEDY_EXIST: '++',
    TokenType.LAZY_OPTIONAL: '??',
    TokenType.LAZY_ANY: '*?',
    TokenType.LAZY_EXIST: '+?',
    None: '(lambda)'
}

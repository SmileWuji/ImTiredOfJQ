import jspf.compiler.lexer as lexer

def test_comprehensive_positive():
    prog = r'  ^.[foo]./bar\d+/(?!./baz/).(.{7, ..., 15}|.{100, 105, 110})' +\
           r'(?=./qux/+).*?<.$/^[h-y]+-\d\d$/>'
    flag = lexer.Flag.NONE
    (token_type, lexeme, next_idx) = lexer.advance(prog, 0, flag)
    assert token_type == lexer.TokenType.WHITESPACE

    # Literally, the program reads...
    # Starting at the root, navigate into the key foo.
    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.TokenType.ROOT

    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.TokenType.NAV

    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.TokenType.STR_MATCH

    # Then navigate into the key bar following by one or more digits.
    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.TokenType.NAV

    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.TokenType.REGEX

    # Then look ahead to ensure the next key is not baz.
    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.TokenType.NONCAP_NEG_BEGIN

    flag = lexer.Flag.NONCAP_NEG_ENABLE
    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.TokenType.NAV

    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.TokenType.REGEX

    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.TokenType.NONCAP_NEG_END

    # After looking ahead, navigate into the object
    flag = lexer.Flag.NONE
    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.TokenType.NAV

    # Then, navigate into the 7 to 15 entry of a list (implied), or the 100, 105
    # or 110 entry of a list.
    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.TokenType.CAP_BEGIN

    flag = lexer.Flag.CAP_ENABLE
    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.TokenType.NAV

    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.TokenType.SET_MATCH

    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.TokenType.UNION

    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.TokenType.NAV

    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.TokenType.SET_MATCH

    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.TokenType.CAP_END

    # Look ahead to ensure there exists at least one key named qux down the
    # chain.
    flag = lexer.Flag.NONE
    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.TokenType.NONCAP_POS_BEGIN

    flag = lexer.Flag.NONCAP_POS_ENABLE
    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.TokenType.NAV

    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.TokenType.REGEX

    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.TokenType.DEFAULT_EXIST

    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.TokenType.NONCAP_POS_END

    # After looking ahead, Navigate into any number of containers.
    flag = lexer.Flag.NONE
    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.TokenType.NAV

    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.TokenType.LAZY_ANY

    # Lastly, look for the values matching the pattern /^[h-y]+-\d\d$/
    # Select only the key-value pair of the last navigation down the chain.
    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.TokenType.SELECT_BEGIN

    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.TokenType.NAV

    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.TokenType.VAL

    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.TokenType.REGEX

    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.TokenType.SELECT_END

def test_negative():
    prog = r'Lorem ipsum dolor sit amet, consectetur adipiscing eli'
    flag = lexer.Flag.NONE
    (token_type, lexeme, next_idx) = lexer.advance(prog, 0, flag)
    assert token_type == lexer.TokenType.INVALID

def test_pass_lexer():
    prog = r'  ^.[foo]./bar\d+/(?!./baz/).(.{7, ..., 15}|.{100, 105, 110})' +\
           r'(?=./qux/+).*?<.$/^[h-y]+-\d\d$/>'
    tokens = [
        lexer.TokenType.ROOT,
        lexer.TokenType.NAV,
        lexer.TokenType.STR_MATCH,
        lexer.TokenType.NAV,
        lexer.TokenType.REGEX,
        lexer.TokenType.NONCAP_NEG_BEGIN,
        lexer.TokenType.NAV,
        lexer.TokenType.REGEX,
        lexer.TokenType.NONCAP_NEG_END,
        lexer.TokenType.NAV,
        lexer.TokenType.CAP_BEGIN,
        lexer.TokenType.NAV,
        lexer.TokenType.SET_MATCH,
        lexer.TokenType.UNION,
        lexer.TokenType.NAV,
        lexer.TokenType.SET_MATCH,
        lexer.TokenType.CAP_END,
        lexer.TokenType.NONCAP_POS_BEGIN,
        lexer.TokenType.NAV,
        lexer.TokenType.REGEX,
        lexer.TokenType.DEFAULT_EXIST,
        lexer.TokenType.NONCAP_POS_END,
        lexer.TokenType.NAV,
        lexer.TokenType.LAZY_ANY,
        lexer.TokenType.SELECT_BEGIN,
        lexer.TokenType.NAV,
        lexer.TokenType.VAL,
        lexer.TokenType.REGEX,
        lexer.TokenType.SELECT_END]
    assert list(map(lambda t: t.token_type, lexer.pass_lexer(prog))) == tokens

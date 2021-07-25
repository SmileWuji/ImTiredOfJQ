import jspf.compiler.lexer as lexer

def test_comprehensive_positive():
    prog = r'  ^.[foo]./bar\d+/(?!./baz/).(.{7, ..., 15}|.{100, 105, 110})' +\
           r'(?=./qux/+).*?<.$/^[h-y]+-\d\d$/>'
    flag = lexer.Flag.NONE
    (token_type, lexeme, next_idx) = lexer.advance(prog, 0, flag)
    assert token_type == lexer.Token.WHITESPACE

    # Literally, the program reads...
    # Starting at the root, navigate into the key foo.
    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.Token.ROOT

    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.Token.NAV

    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.Token.STR_MATCH

    # Then navigate into the key bar following by one or more digits.
    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.Token.NAV

    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.Token.REGEX

    # Then look ahead to ensure the next key is not baz.
    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.Token.NONCAP_NEG_BEGIN

    flag = lexer.Flag.NONCAP_NEG_ENABLE
    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.Token.NAV

    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.Token.REGEX

    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.Token.NONCAP_NEG_END

    # After looking ahead, navigate into the object
    flag = lexer.Flag.NONE
    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.Token.NAV

    # Then, navigate into the 7 to 15 entry of a list (implied), or the 100, 105
    # or 110 entry of a list.
    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.Token.CAP_BEGIN

    flag = lexer.Flag.CAP_ENABLE
    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.Token.NAV

    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.Token.SET_MATCH

    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.Token.UNION

    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.Token.NAV

    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.Token.SET_MATCH

    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.Token.CAP_END

    # Look ahead to ensure there exists at least one key named qux down the
    # chain.
    flag = lexer.Flag.NONE
    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.Token.NONCAP_POS_BEGIN

    flag = lexer.Flag.NONCAP_POS_ENABLE
    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.Token.NAV

    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.Token.REGEX

    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.Token.GREEDY_EXIST

    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.Token.NONCAP_POS_END

    # After looking ahead, Navigate into any number of containers.
    flag = lexer.Flag.NONE
    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.Token.NAV

    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.Token.LAZY_ANY

    # Lastly, look for the values matching the pattern /^[h-y]+-\d\d$/
    # Select only the key-value pair of the last navigation down the chain.
    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.Token.SELECT_BEGIN

    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.Token.NAV

    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.Token.VAL

    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.Token.REGEX

    (token_type, lexeme, next_idx) = lexer.advance(prog, next_idx, flag)
    assert token_type == lexer.Token.SELECT_END

def test_negative():
    prog = r'Lorem ipsum dolor sit amet, consectetur adipiscing eli'
    flag = lexer.Flag.NONE
    (token_type, lexeme, next_idx) = lexer.advance(prog, 0, flag)
    assert token_type == lexer.Token.UNEXPECTED

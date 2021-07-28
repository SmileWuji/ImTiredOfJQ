from jspf.compiler import lexer
from jspf.compiler.CompilerError import CompilerError
from enum import Enum

'''
Syntax:

S --> AQE

E --> (lambda)
E --> AQE

A --> <S>
A --> (SU)
A --> (?!SU)
A --> (?=SU)
A --> TC

U --> (lambda)
U --> |S

C --> (lambda)
C --> lexeme.TokenType.REGEX
C --> lexeme.TokenType.STR_MATCH
C --> lexeme.TokenType.SET_MATCH

Q --> (lambda)
Q --> lexeme.TokenType.DEFAULT_OPTIONAL
Q --> lexeme.TokenType.DEFAULT_ANY
Q --> lexeme.TokenType.DEFAULT_EXIST
Q --> lexeme.TokenType.GREEDY_OPTIONAL
Q --> lexeme.TokenType.GREEDY_ANY
Q --> lexeme.TokenType.GREEDY_EXIST
Q --> lexeme.TokenType.LAZY_OPTIONAL
Q --> lexeme.TokenType.LAZY_ANY
Q --> lexeme.TokenType.LAZY_EXIST

T --> lexeme.TokenType.NAV
T --> lexeme.TokenType.VAL
T --> lexeme.TokenType.ROOT
'''

T_1ST = {lexer.TokenType.NAV,
         lexer.TokenType.VAL,
         lexer.TokenType.ROOT}
Q_1ST = {lexer.TokenType.DEFAULT_OPTIONAL,
         lexer.TokenType.DEFAULT_ANY,
         lexer.TokenType.DEFAULT_EXIST,
         lexer.TokenType.GREEDY_OPTIONAL,
         lexer.TokenType.GREEDY_ANY,
         lexer.TokenType.GREEDY_EXIST,
         lexer.TokenType.LAZY_OPTIONAL,
         lexer.TokenType.LAZY_ANY,
         lexer.TokenType.LAZY_EXIST}
C_1ST = {lexer.TokenType.REGEX,
         lexer.TokenType.STR_MATCH,
         lexer.TokenType.SET_MATCH}
U_1ST = {lexer.TokenType.UNION}
A_1ST = {lexer.TokenType.SELECT_BEGIN,
         lexer.TokenType.CAP_BEGIN,
         lexer.TokenType.NONCAP_NEG_BEGIN,
         lexer.TokenType.NONCAP_POS_BEGIN}.union(T_1ST)
E_1ST = A_1ST
S_1ST = A_1ST
U_FOL = {lexer.TokenType.SELECT_END,
         lexer.TokenType.CAP_END,
         lexer.TokenType.NONCAP_NEG_END,
         lexer.TokenType.NONCAP_POS_END}
E_FOL = {None}.union(U_1ST).union(U_FOL).union(A_1ST)
Q_FOL = E_1ST.union(E_FOL)
C_FOL = Q_1ST.union(Q_FOL)

class Node(Enum):
    S = 0
    E = 1
    A = 2
    U = 3
    C = 4
    Q = 5
    T = 6

class Tree:
    def __init__(self, node_type):
        self.node_type = node_type
        self.subtree = list()

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        subtree_repr = list(map(lambda st: st.to_dict(), self.subtree))
        return {str(self.node_type): subtree_repr}

class RecursiveDescentParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.t_idx = 0

    def cur(self):
        if self.t_idx == len(self.tokens):
            return None
        else:
            return self.tokens[self.t_idx].token_type

    def advance(self):
        token = self.tokens[self.t_idx]
        self.t_idx += 1
        assert self.t_idx <= len(self.tokens)
        return token

    def eat(self, token_type):
        if self.cur() == token_type:
            return self.advance()
        else:
            self.err({token_type})

    def err(self, expected_token_types):
        token = self.tokens[self.t_idx]
        err_msg = 'Unexpected token {} "{}" at token {} (byte {})'.format(
            lexer.TOKEN_NAMES[token.token_type],
            token.lexeme,
            self.t_idx,
            token.prog_idx) 
        raise CompilerError(err_msg)        

    def p_T(self):
        tree = Tree(Node.T)

        if self.cur() in T_1ST:
            tree.subtree.append(self.eat(self.cur()))

        else:
            self.err(T_1ST)

        return tree

    def p_Q(self):
        tree = Tree(Node.Q)

        if self.cur() in Q_1ST:
            tree.subtree.append(self.eat(self.cur()))

        elif self.cur() in Q_FOL:
            pass

        else:
            self.err(Q_1ST)

        return tree

    def p_C(self):
        tree = Tree(Node.C)

        if self.cur() in C_1ST:
            tree.subtree.append(self.eat(self.cur()))

        elif self.cur() in C_FOL:
            pass

        else:
            self.err(C_1ST)

        return tree

    def p_U(self):
        tree = Tree(Node.U)

        if self.cur() == lexer.TokenType.UNION:
            tree.subtree.append(self.eat(lexer.TokenType.UNION))
            tree.subtree.append(self.p_S())

        elif self.cur() in U_FOL:
            pass

        else:
            self.err(U_1ST)

        return tree

    def p_A(self):
        tree = Tree(Node.A)

        if self.cur() == lexer.TokenType.SELECT_BEGIN:
            tree.subtree.append(self.eat(lexer.TokenType.SELECT_BEGIN))
            tree.subtree.append(self.p_S())
            tree.subtree.append(self.p_U())
            tree.subtree.append(self.eat(lexer.TokenType.SELECT_END))

        elif self.cur() == lexer.TokenType.CAP_BEGIN:
            tree.subtree.append(self.eat(lexer.TokenType.CAP_BEGIN))
            tree.subtree.append(self.p_S())
            tree.subtree.append(self.p_U())
            tree.subtree.append(self.eat(lexer.TokenType.CAP_END))

        elif self.cur() == lexer.TokenType.NONCAP_POS_BEGIN:
            tree.subtree.append(self.eat(lexer.TokenType.NONCAP_POS_BEGIN))
            tree.subtree.append(self.p_S())
            tree.subtree.append(self.p_U())
            tree.subtree.append(self.eat(lexer.TokenType.NONCAP_POS_END))

        elif self.cur() == lexer.TokenType.NONCAP_NEG_BEGIN:
            tree.subtree.append(self.eat(lexer.TokenType.NONCAP_NEG_BEGIN))
            tree.subtree.append(self.p_S())
            tree.subtree.append(self.p_U())
            tree.subtree.append(self.eat(lexer.TokenType.NONCAP_NEG_END))

        elif self.cur() in T_1ST:
            tree.subtree.append(self.p_T())
            tree.subtree.append(self.p_C())

        else:
            self.err(A_1ST)

        return tree

    def p_E(self):
        tree = Tree(Node.E)

        if self.cur() in A_1ST:
            tree.subtree.append(self.p_A())
            tree.subtree.append(self.p_Q())
            tree.subtree.append(self.p_E())

        elif self.cur() in E_FOL:
            pass

        else:
            self.err(E_1ST)

        return tree

    def p_S(self):
        tree = Tree(Node.S)

        if self.cur() in A_1ST:
            tree.subtree.append(self.p_A())
            tree.subtree.append(self.p_Q())
            tree.subtree.append(self.p_E())

        else:
            self.err(S_1ST)

        return tree

def recursive_descent(tokens):
    raise NotImplementedError()

def pass_syntax(prog):
    tokens = lexer.pass_lexer(prog)
    parser = RecursiveDescentParser(tokens)
    tree = parser.p_S()
    assert parser.t_idx == len(tokens)
    return tree

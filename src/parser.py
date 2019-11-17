import copy

'''
parser.py - parser
This module uses RDP to parse lexed Newt code.
'''

VAL = 'val' # Various tags
TYPE = 'type'
NAME = 'name'
IF = 'if'
FOR = 'for'
WHILE = 'while'
ASM = 'asm'
GOTO = 'goto'
DEFINE = 'define'
LBRACK = '{'
RBRACK = '}'
SEMI = ';'
EQ = '='
OP = 'op'
LPAR = '('
RPAR = ')'
COMMA = ','

def expect(stream, token):
    '''
    expect function.
    Used when a token is manditory.
    '''
    try:
        if type(token) == str: # The token is a string
            if stream[0][1] == token:
                stream.pop(0) # Pop the token if we find a match
                return True
            raise SyntaxError('Invalid token %s' % stream[0][0]) # Raise an error otherwise
        else: # The token is iterable, we never really use this
            for t in token: # Iterate over every token
                if stream[0][1] == t: # Match it
                    stream.pop(0)
                    return True
            raise SyntaxError('Invalid token %s' % stream[0][0])
    except IndexError:
        raise SyntaxError('Not enough tokens') # There aren't enough tokens, yell at somebody
def accept(stream, token):
    '''
    accept function.
    Used for optional tokens or for accepting any of a set of tokens.
    '''
    if type(token) == str: # The token is a string
        first = stream[0][1]
        if first == token:
            stream.pop(0) # Pop the token if we find a match
            return True
        return False # If no match was found, just return false
    else: # The token is iterable, this is not really used
        for t in token: # Iterate over every token
            if stream[0][1] == t: # Match it
                stream.pop(0)
                return True
        return False

def assign(stream):
    '''
    assign function.
    Used for parsing an assign statement.
    '''
    if len(stream) == 5: # The statement is of the form <type> <name> = <val>;
        if accept(stream, TYPE):
            expect(stream, NAME)
            expect(stream, EQ)
            accept(stream, VAL)
            accept(stream, NAME)
            expect(stream, SEMI)
            return True
    elif len(stream) == 4: # The statement is of the form <name> = <val>;
        if accept(stream, NAME):
            expect(stream, EQ)
            accept(stream, VAL)
            accept(stream, NAME)
            expect(stream, SEMI)
            return True
    return False

def arg(stream):
    '''
    arg function.
    Not applied directly to lexed code - used for parsing arguments to functions.
    '''
    if accept(stream, TYPE) or accept(stream, VAL) or accept(stream, NAME): # We found a match
        accept(stream, RPAR) # This could be the end of the stream
        if len(stream) > 1: # But then again, it might not be
            accept(stream, COMMA)
            arg(stream)
        return True
    elif accept(stream, RPAR):
        return True
    return False
def call(stream):
    '''
    call function.
    Used for parsing function calls.
    '''
    if accept(stream, NAME):
        expect(stream, LPAR)
        arg(stream)
        expect(stream, SEMI)
        return True
    return False

def condition(stream):
    '''
    condition function.
    Used for parsing if statements.
    '''
    if accept(stream, IF):
        expect(stream, LPAR)
        accept(stream, VAL)
        accept(stream, NAME)
        expect(stream, OP)
        accept(stream, VAL)
        accept(stream, NAME)
        expect(stream, RPAR)
        expect(stream, LBRACK)
        return True
    return False

def asm(stream):
    '''
    asm function.
    Used for parsing inline assembly.
    '''
    if accept(stream, ASM):
        expect(stream, LBRACK)
        return True
    return False

def loop(stream):
    '''
    loop function.
    Used for parsing while loops.
    '''
    if accept(stream, WHILE):
        expect(stream, LPAR)
        accept(stream, VAL)
        accept(stream, NAME)
        expect(stream, OP)
        accept(stream, VAL)
        accept(stream, NAME)
        expect(stream, RPAR)
        expect(stream, LBRACK)
        return True
    return False

def rep(stream):
    '''
    rep function.
    Used for parsing for loops.
    '''
    if accept(stream, FOR):
        expect(stream, LPAR)
        expect(stream, NAME)
        expect(stream, COMMA)
        accept(stream, VAL)
        accept(stream, NAME)
        expect(stream, COMMA)
        accept(stream, VAL)
        accept(stream, NAME)
        expect(stream, RPAR)
        expect(stream, LBRACK)
        return True
    return False

def goto(stream):
    '''
    goto function.
    Used for parsing goto statements.
    '''
    if accept(stream, GOTO):
        accept(stream, VAL)
        accept(stream, NAME)
        expect(stream, SEMI)

def define(stream):
    '''
    define function.
    Used for parsing function definitions.
    '''
    if accept(stream, DEFINE):
        expect(stream, NAME)
        expect(stream, LPAR)
        arg(stream)
        expect(stream, LBRACK)
        return True
    return False

def end(stream):
    '''
    end function.
    Never applied directly to input, used for checking if a statement just ended.
    '''
    return stream.strip()[0] == '}'

parsers = [assign, call, condition, asm, loop, rep, goto, define] # The parsers
def parse(stream):
    '''
    The parse function - used for parsing lexed code.
    '''
    i = 0
    old = copy.copy(stream) # We need a copy of the stream because ours will be broken.
    p = None
    for parser in parsers: # Iterate over every parser
        try:
            parser(stream) # Apply the current parser to the input
            if not stream:
                p = parser # The whole stream was consumed, so this parser is the match
        except Exception as e: # The parser threw and error, so pass over it
            pass
    return p, old

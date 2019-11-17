import re
import parser

'''
lexer.py - lexer
Converts code to a list of token-tag pairs.
'''

tokens = { # Regex to tag mappings
    r'if':parser.IF,
    r'for':parser.FOR,
    r'while':parser.WHILE,
    r'asm':parser.ASM,
    r'goto':parser.GOTO,
    r'define':parser.DEFINE,
    r'(byte|word|dword|qword)':parser.TYPE,
    r'[a-zA-Z_]+':parser.NAME,
    r'((0[xb])?[0-9a-fA-F]+|"[^"]+")':parser.VAL,
    r'\{':parser.LBRACK,
    r'\}':parser.RBRACK,
    r';':parser.SEMI,
    r'(!=|<|>|==|>=|<=)':parser.OP,
    r'=':parser.EQ,
    r'\(':parser.LPAR,
    r'\)':parser.RPAR,
    r',':parser.COMMA,
}

def lex(code):
    stream = []
    i = 0
    while code: # Repeat till all the code is gone - if there is a syntax error, we will hang
        if code[0] == '#': # The line begins with a comment, so ignore it
            return stream
        while code[0] == ' ' or code[0] == '\t' or code[0] == '\n': # Remove all whitespace
            code = code[1:]
        for token in tokens: # Iterate over every token
            m = re.match(token, code) # Check if the current token is a match
            if m:
                code = code[len(m.group(0)):] # It is, so remove the token and add the match to the stream
                stream.append((m.group(0), tokens[token]))
    return stream

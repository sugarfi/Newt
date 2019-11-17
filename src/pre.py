import re

'''
pre.py - preprocessor
This module does basic preprocessing on Newt code.
'''

macro = r'@[a-z]+ [^;]*;' # The format of a macro
vars = {} # @defined variables

def include(line, code, args):
    '''
    include function.
    Called when an @include macro is parsed.
    '''
    file = open(args[0]).read() # Open the file the user wants
    code = code.replace(line, file) # Replace the macro with the file's contents
    return code

def define(line, code, args):
    '''
    define function.
    Called when an @define macro is parsed.
    '''
    vars[args[0]] = args[1] # Add the variable to the dictionary
    code = code.replace(line, '') # Remove the macro
    lines = code.split('\n')
    for i in range(len(lines)):
        line = lines[i]
        if line[0] != '@':
            line = line.replace(args[0], args[1]) # Replace the variable with its value, except within other macros
        lines[i] = line
    code = '\n'.join(lines)
    return code

funcs = { # String to function mappings
    'include':include,
    'define':define,
}

def pre(code):
    '''
    pre function.
    Used for preprocessing code.
    '''
    macs = re.findall(macro, code) # Find all macros
    for mac in macs:
        line = mac # Store the match
        mac = mac[1:].rstrip(';') # Remove the semicolon
        mac, args = mac.split()[0], mac.split()[1:] # Get the macro name and arguments
        if mac in funcs:
            code = funcs[mac](line, code, args) # The macro is one we know, so run it
        else:
            code = code.replace(line, '') # The macro is unknown, so delete it
    return code

import re
import parser
import lexer
import pre

'''
asm.py - the actual compiler
This module defines functions and objects for compiling parsed Newt code.
'''

jmps = {'==':'je', '!=':'jne', '<':'jl', '>':'jg', '<=':'jle', '>=':'jge'} # The jump instructions for each condition

class Env():
    '''
    The environment object.
    Used to run code.
    '''
    def __init__(self, file):
        self.file = file # The input file
        self.vars = {} # Variables dictionary with types
        self.funcs = {} # Functions dictionary with arguments
        self.pos = 0 # Program counter
        self.indent = 1 # Output indentation level
        self.write('section .text', False) # The text section, store code here
        self.write('global _start')
        self.write('_start:') # Initalize the _start label, need for compiling with ld
        self.indent = 2
        self.loops = 0 # Number of loops, used for naming labels
        self.ifs = 0 # Number of if statements, used for naming labels
    def __repr__(self):
        return self.file.name + ' env'
    def run(self, file):
        '''
        The run method.
        Iterate over every line in the file, lex, parse, and run it.
        '''
        code = pre.pre(file.read()) # Preprocess the input code
        lines = code.split('\n') # Split the code into lines
        self.lines = lines # Store the lines so functions can access them
        while '' in lines:
            lines.remove('') # Remove empty lines
        while self.pos < len(lines):
            line = lines[self.pos] # Get the current line
            stream = lexer.lex(line) # Lex the line
            if parser.end(line): # The line is a } (used for ending statements), so we should skip it
                self.pos += 1
                continue
            elif stream:
                func, stream = parser.parse(stream) # Parse the lexed stream
                stream = [token[0] for token in stream] # We don't need the tag part of the stream, only the text
                func = mapping[func](stream)
                func.run(self) # Run the function we got
            else:
                self.pos += 1
        self.write('ret') # Return from main function, needed to avoid segmenation fault
        self.indent = 1
        self.write('section .data', False) # The data section, store variables here
        for var in self.vars:
            type = 'd' + self.vars[var][0][0] # Define a variable of the right type
            if self.vars[var][1][0] == '"':
                self.write('%s: %s %s' % (var, type, self.vars[var][1]))
            else:
                self.write('%s: %s 0' % (var, type))
    def write(self, line, t=True):
        '''
        The write function.
        Write a line to the output file.
        '''
        self.file.write(('\t' * self.indent if t else '') + line) # Write the line
        self.file.write('\n') # Line break

class Assign():
    '''
    The assign object.
    Run when an assignment statement is parsed.
    Syntax:
    <type> <name> = <value | name>;
    <name> = <value | name>;
    '''
    def __init__(self, stream):
        if len(stream) == 5: # The statement is of the form <type> <name> = <val>;
            self.type = stream[0] # The type
            self.name = stream[1] # The name
            self.value = stream[3] # The value
        else: # The statement is of the form <name> = <val>;
            self.type = None # The type, not known yet
            self.name = stream[0] # The name
            self.value = stream[2] # The value
    def run(self, env):
        if not self.type: # We don't know the type, get it from the dictionary
            self.type = env.vars[self.name][0]
        if self.value in env.vars: # We are assigning a variable to another variable
            type = env.vars[self.value][0]
            val = env.vars[self.value][1]
            # In nasm, we cannot directly mov from one address to another.
            # To get around this, we must move to a register, then to the variable address.
            if type == 'byte':
                reg = 'al' # Byte register
            elif type == 'word':
                reg = 'ax' # Word register
            elif type == 'dword':
                reg = 'eax' # Dword register
            elif type == 'qword':
                reg = 'rax' # Qword register
            self.value = '[%s]' % self.value # Get the variable's value, not its address
            env.write('mov %s, %s' % (reg, self.value)) # Move the value to the register
            self.value = reg # Move register to address
        if '"' not in self.value:
            env.write('mov %s [%s], %s' % (self.type, self.name, self.value)) # Move the value to the name
        env.vars[self.name] = (self.type, self.value) # Store the variables type and value
        env.pos += 1 # Increment the program counter

class Call():
    '''
    The call object.
    Run when a call statement is parsed.
    Syntax:
    <name> (<args>);
    '''
    def __init__(self, stream):
        self.name = stream[0] # The function name to call
        self.args = stream[2:stream.index(')')] # The arguments
        while ',' in self.args: # Remove the commas
            self.args.remove(',')
    def run(self, env):
        for i in range(len(self.args)):
            arg = self.args[i]
            if arg in env.vars: # If an argument is a variable, convert it to its value
                arg = '[%s]' % arg
            self.args[i] = arg
        if self.name in env.funcs: # We are calling a defined function
            args = env.funcs[self.name] # Get the arguments needed
            for i in range(len(args[1::2])): # Each argument is a variable, so we mov to it
                type, name = (args[i * 2], args[1::2][i])
            # Move the value into a register, then into the argument
            if type == 'byte':
                reg = 'al' # Byte register
            elif type == 'word':
                reg = 'ax' # Word register
            elif type == 'dword':
                reg = 'eax' # Dword register
            elif type == 'qword':
                reg = 'rax' # Qword register
            for i in range(len(self.args)):
                arg = self.args[i] # Actual argument
                want = args[1::2][i] # The needed argument
                env.write('mov %s, %s' % (reg, arg)) # Move the value to the register
                env.write('mov [%s], %s' % (want, reg)) # Move the register to the argument
            env.write('call %s' % self.name)
        else: # We are calling a x86 instruction
            env.write('%s %s' % (self.name, ', '.join(self.args))) # Write the instruction
        env.pos += 1

class Condition():
    '''
    Condition object.
    Called when an if statement is parsed.
    Syntax:
    if (<value | name> <op> <value | name>) {
        <code>
    }
    '''
    def __init__(self, stream):
        self.a = stream[2] # The first value
        self.op = stream[3] # The operator
        self.b = stream[4] # The second value
    def run(self, env):
        if self.a in env.vars: # A is a variable, get its value
            self.a = '%s [%s]' % (env.vars[self.a][0], self.a)
        if self.b in env.vars: # B is a variable, get its value
            self.b = env.vars[self.b]
        self.name = 'i%d:' % env.ifs # Get the name for our label
        env.ifs += 1 # Increment the number of labels
        env.write('cmp %s, %s' % (self.a, self.b)) # Compare our two values
        env.write(jmps[self.op] + ' ' + self.name.rstrip(':')) # If they match the operator, jump to our label
        env.write('jmp ' + self.name.rstrip(':') + 'e') # Jump over our label
        env.write(self.name) # Create our label
        env.indent += 1 # Indent
        env.pos += 1
        level = 1 # The bracket level
        while level != 0:
            if parser.end(env.lines[env.pos]): # We just ended a statement, so decrement the bracket level
                level -= 1
            else:
                stream = lexer.lex(env.lines[env.pos]) # Lex the current line
                func, stream = parser.parse(stream) # Parse it
                stream = [token[0] for token in stream] # Remove the tag
                func = mapping[func](stream)
                func.run(env) # Run it, this causes stuff to be written to the file
                env.pos -= 1
            if '{' in env.lines[env.pos]: # We began a statement, so increment the bracket level
                level += 1
            if level == 0:
                env.pos += 1
                break
        env.indent -= 1
        env.write(self.name.rstrip(':') + 'e:') # The label used to jump over our label
        env.indent += 1
        env.write('nop') # Our label should not do anything
        env.indent -= 1

class Asm():
    '''
    Asm object.
    Called when an assembly statement is parsed.
    Syntax:
    asm {
        <assembly>
    }
    '''
    def __init__(self, stream):
        pass # We don't need anything from the stream
    def run(self, env):
        env.pos += 1
        for i in range(env.pos, len(env.lines)):
            if parser.end(env.lines[i]): # The statement ended
                env.pos = i + 1
                return
            else:
                if '}' not in env.lines[i]: #  Write the current line directly to the file
                    env.write(env.lines[i].strip())

class While():
    '''
    While object.
    Called when a while loop is parsed.
    Syntax:
    while (<value | name> <op> <value | name>) {
        <code>
    }
    '''
    def __init__(self, stream):
        self.a = stream[2] # The a value
        self.a2 = self.a
        self.op = stream[3] # The operator
        self.b = stream[4] # The b value
    def run(self, env):
        if self.b in env.vars:
            self.b = env.vars[self.b][1] # B is a variable, get its value
        eval = 0
        self.name = 'w%d:' % env.loops # The name of our loop
        env.loops += 1 # Increment the number of loops
        env.write(self.name) # Add our label
        env.indent += 1
        env.pos += 1
        level = 1 # The bracket level
        while level != 0: # While the statement is not over
            if parser.end(env.lines[env.pos]): # A statement ended, so decrement the bracket level
                level -= 1
            else:
                stream = lexer.lex(env.lines[env.pos]) # Lex the current line
                func, stream = parser.parse(stream) # Parse it
                stream = [token[0] for token in stream] # Remove the tags
                func = mapping[func](stream)
                func.run(env) # Run it, this adds stuff to the file
                env.pos -= 1
            if '{' in env.lines[env.pos]: # A statement began, so increment the bracket level
                level += 1
            if level == 0:
                env.pos += 1
                break
        if self.a2 in env.vars: # A is a variable, so take its value
            self.a2 = '%s [%s]' % (env.vars[self.a2][0], self.a2)
        env.write('cmp %s, %s' % (self.a2, self.b)) # Compare the a and b values
        env.write(jmps[self.op] + ' ' + self.name.rstrip(':')) # Jump to our loop
        env.indent -= 1

class For():
    '''
    For object.
    Called when a for loop is parsed.
    Syntax:
    for (<name>, <value | name>, <value | name>) {
        <code>
    }
    '''
    def __init__(self, stream):
        self.var = stream[2] # The counter variable
        self.min = stream[4] # The minimum
        self.max = stream[6] # The maximum
    def run(self, env):
        self.var = '%s [%s]' % (env.vars[self.var][0], self.var) # Make sure we take the value, not the address, of our variable
        self.name = 'f%d:' % env.loops # The name of our loop
        env.loops += 1
        env.write('mov %s, %s' % (self.var, self.min)) # Set the variable to our minimum
        env.write(self.name) # Add our label
        env.indent += 1
        env.pos += 1
        level = 1 # The bracket level
        while level != 0: # While the statement is still going
            if parser.end(env.lines[env.pos]): # A statement ended, decrement the bracket level
                level -= 1
            else:
                start = '{' in env.lines[env.pos] # Check whether a statement has started
                stream = lexer.lex(env.lines[env.pos]) # Lex the current line
                func, stream = parser.parse(stream) # Parse it
                stream = [token[0] for token in stream] # Remove the tags
                func = mapping[func](stream)
                func.run(env) # Run the function, this adds stuff to the file
                if start:
                    env.pos -= 1
            if '{' in env.lines[env.pos]: # A statement ended, increment the bracket level
                level += 1
            if level == 0:
                env.pos += 1
                break
        env.write('inc %s' % self.var) # Increment our variable
        env.write('cmp %s, %s' % (self.var, self.max)) # Compare it to the max
        env.write('jl ' + self.name.rstrip(':')) # If it is less than it, jump back to our loop
        env.indent -= 1

class Goto():
    '''
    Goto object.
    Called when a go to statement is parsed.
    Syntax:
    goto <line | name>;
    '''
    def __init__(self, stream):
        self.line = stream[1] # The line to jump to
    def run(self, env):
        if self.line in env.vars: # The line is a variable, take its value
            self.line = env.vars[self.line][1]
        self.line = int(self.line, base=10 + (6 * self.line[0:2] == '0x')) # Jump to the line, which might be in hex
        env.pos = self.line

class Define():
    '''
    Define object.
    Called when a function definition is parsed.
    Syntax:
    define <name> (<type> <name>, ...) {
        <code>
    }
    '''
    def __init__(self, stream):
        self.name = stream[1] # The name of our function
        self.args = stream[3:stream.index(')')] # The arguments
        while ',' in self.args: # Remove commas
            self.args.remove(',')
    def run(self, env):
        for i in range(len(self.args[1::2])): # Initialize all our variables
            env.vars[self.args[1::2][i]] = (self.args[i * 2], '0')
        env.funcs[self.name] = self.args # Put our function in the dictionary
        env.write('jmp e%s' % self.name) # Jump over our function until it is called
        env.write('%s:' % self.name) # Add our label
        env.indent += 1
        env.pos += 1
        level = 1 # The bracket level
        while level != 0:
            if parser.end(env.lines[env.pos]): # A statement ended, decrement the bracket level
                level -= 1
            else:
                start = '{' in env.lines[env.pos] # Check if a statement started
                stream = lexer.lex(env.lines[env.pos]) # Lex the current line
                func, stream = parser.parse(stream) # Parse it
                stream = [token[0] for token in stream] # Remove the tags
                func = mapping[func](stream)
                func.run(env) # Run the function, this adds stuff to the file
            if '{' in env.lines[env.pos]: # A statement began, increment the bracket level
                level += 1
            if level == 0:
                env.pos += 1
                break
        env.write('ret') # Return
        env.indent -= 1
        env.write('e%s:' % self.name) # Label used to jump over our function
        env.indent += 1
        env.write('nop') # Do nothing
        env.indent -= 1

mapping = { # Map parsing functions to runner objects
    parser.assign:Assign,
    parser.call:Call,
    parser.condition:Condition,
    parser.asm:Asm,
    parser.loop:While,
    parser.rep:For,
    parser.goto:Goto,
    parser.define:Define
}

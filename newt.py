#!/usr/bin/python3

import parser
import lexer
import asm
import sys
import re

if len(sys.argv) < 1:
    raise ArgumentError('Newt needs a file to run!')

file = open(sys.argv[1], 'r')
out = open(sys.argv[1].split('.')[0] + '.asm', 'w')

env = asm.Env(out)
env.run(file)
out.close()
file.close()

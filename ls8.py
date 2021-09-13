#!/usr/bin/env python3

"""Main."""

import sys
import re
from cpu import *

# check if file was provided from commandline
if len(sys.argv) < 2:
    print('You must provide a file to read.')
    print('-> python ls8.py [file]')
    sys.exit()

# open the specified file
f = open(sys.argv[1], 'r')

# check if the file was properly opened
if f.mode != 'r':
    print('Unable to read specified file:', sys.argv[1])
    sys.exit()

# parse program instructions
program = []
for instruction in re.findall(r'\d{8}', f.read()):
    program.append(int(instruction, 2))

# initialise the CPU
cpu = CPU(program)

# load program into memory and run
cpu.load()
cpu.run()

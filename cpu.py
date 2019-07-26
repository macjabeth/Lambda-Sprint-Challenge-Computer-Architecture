"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self, program):
        """Construct a new CPU."""
        self.program = program
        self.branchtable = {}
        self.setup_branchtable()
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.sp = 0xF4
        self.pc = 0
        self.fl = 0

    def setup_branchtable(self):
        self.branchtable[0b10000010] = self.ldi
        self.branchtable[0b10100000] = self.add
        self.branchtable[0b10100010] = self.mul
        self.branchtable[0b10100011] = self.div
        self.branchtable[0b10101000] = self.bwand
        self.branchtable[0b01100101] = self.inc
        self.branchtable[0b01100110] = self.dec
        self.branchtable[0b10100111] = self.comp
        self.branchtable[0b01000111] = self.prn
        self.branchtable[0b01000101] = self.push
        self.branchtable[0b01000110] = self.pop
        self.branchtable[0b01010000] = self.call
        self.branchtable[0b00010001] = self.ret
        self.branchtable[0b01010100] = self.jmp
        self.branchtable[0b01010101] = self.jeq
        self.branchtable[0b00000001] = self.hlt

    def load(self):
        """Load a program into memory."""

        address = 0

        for instruction in self.program:
            self.ram[address] = instruction
            address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == "AND":
            self.reg[reg_a] &= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010
            else:
                self.fl = 0b00000001
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def hlt(self):
        sys.exit()

    def ldi(self, register, value):
        self.reg[register] = value

    def prn(self, register):
        print(self.reg[register])

    def add(self, reg_a, reg_b):
        self.alu('ADD', reg_a, reg_b)

    def sub(self, reg_a, reg_b):
        self.alu('SUB', reg_a, reg_b)

    def mul(self, reg_a, reg_b):
        self.alu('MUL', reg_a, reg_b)

    def div(self, reg_a, reg_b):
        self.alu('DIV', reg_a, reg_b)

    def bwand(self, reg_a, reg_b):
        self.alu('AND', reg_a, reg_b)

    def inc(self, reg):
        self.alu('ADD', reg, 1)

    def dec(self, reg):
        self.alu('SUB', reg, 1)

    def comp(self, reg_a, reg_b):
        self.alu('CMP', reg_a, reg_b)

    def ram_read(self, mar):
        return self.ram[mar]

    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr

    def push(self, reg):
        self.sp -= 1
        self.ram_write(self.sp, self.reg[reg])

    def pop(self, reg):
        self.reg[reg] = self.ram_read(self.sp)
        self.sp += 1

    def call(self, reg):
        self.sp -= 1
        self.ram_write(self.sp, self.pc)
        self.pc = self.reg[reg]

    def ret(self):
        self.pc = self.ram_read(self.sp)
        self.sp += 1

    def store(self, reg_a, reg_b):
        address = self.ram_read(reg_a)
        value = self.ram_read(reg_b)
        self.ram_write(address, value)

    def jmp(self, reg):
        self.pc = self.reg[reg]

    def jeq(self, reg):
        if self.fl == 0b00000001:
            self.pc = self.reg[reg]

    def run(self):
        """Run the CPU."""
        one_op = set({
            0b01000111, 0b01000101, 0b01000110, 0b01010000, 0b01100101,
            0b01100110, 0b01010100, 0b01010101
        })

        two_op = set({
            0b10000010, 0b10100010, 0b10100000, 0b10101000, 0b10100011,
            0b10100111
        })

        while True:
            IR = self.ram_read(self.pc)

            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if self.branchtable.get(IR):
                args = []

                if IR in one_op:
                    args = [operand_a]
                    self.pc += 2
                elif IR in two_op:
                    args = [operand_a, operand_b]
                    self.pc += 3

                self.branchtable[IR](*args)
            else:
                print('Unknown instruction:', IR)

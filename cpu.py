import sys


class CPU:

    def __init__(self):
        self.register = [0] * 8
        self.ram = [0] * 256
        self.register[7] = len(self.ram) - 1
        self.pc = 0

        self.branchtable = {}
        self.branchtable[int(0b10100000)] = self.handle_ADD
        self.branchtable[int(0b10100011)] = self.handle_SUB
        self.branchtable[int(0b10100010)] = self.handle_MUL
        self.branchtable[int(0b10100011)] = self.handle_DIV
        self.branchtable[int(0b10100111)] = self.handle_CMP
        self.branchtable[int(0b01000111)] = self.handle_PRN
        self.branchtable[int(0b10000010)] = self.handle_LDI
        self.branchtable[int(0b01000110)] = self.sudo_pop
        self.branchtable[int(0b01000101)] = self.sudo_push
        self.branchtable[int(0b01010000)] = self.call
        self.branchtable[int(0b00010001)] = self.ret
        self.branchtable[int(0b01010100)] = self.jmp
        self.branchtable[int(0b01010101)] = self.jeq
        self.branchtable[int(0b01010110)] = self.jne

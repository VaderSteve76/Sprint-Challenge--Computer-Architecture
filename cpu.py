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

    def handle_ADD(self, operand_a, operand_b):
        self.alu('ADD, operand_a, operand_b')
        self.pc += 3

    def handle_SUB(self, operand_a, operand_b):
        self.alu("SUB", operand_a, operand_b)
        self.pc += 3

    def handle_MUL(self, operand_a, operand_b):
        self.alu("MUL", operand_a, operand_b)
        self.pc += 3

    def handle_DIV(self, operand_a, operand_b):
        self.alu("DIV", operand_a, operand_b)
        self.pc += 3

    def handle_CMP(self, operand_a, operand_b):
        self.alu('CMP', operand_a, operand_b)

    def handle_PRN(self, operand_a, operand_b):
        print(f'{self.register[operand_a]}')
        self.pc += 2

    def handle_LDI(self, operand_a, operand_b):
        self.register[operand_a] = operand_b
        self.pc += 3

    def sudo_push(self, operand_a, operand_b):
        self.ram[self.register[7]] = self.register[operand_a]
        self.register[7] -= 1
        self.pc += 2

    def sudo_pop(self, operand_a, operand_b):
        self.register[7] += 1
        self.register[operand_a] = self.ram[self.register[7]]
        self.pc += 2

    def call(self, operand_a, operand_b):
        self.ram[self.register[7]] = self.pc + 2
        self.register[7] -= 1
        self.pc = self.register[operand_a]

    def ret(self, operand_a, operand_b):
        self.register[7] += 1
        self.pc = self.ram[self.register[7]]

    def jmp(self, operand_a, operand_b):
        self.pc = self.register[operand_a]

    def jeq(self, operand_a, operand_b):
        if self.register[6] == 0b00000001:
            self.jmp(operand_a, operand_b)
        else:
            self.pc += 2

    def jne(self, operand_a, operand_b):
        bit_wise_equality = self.register[6] & 0b00000001
        if bit_wise_equality == 0:
            self.jmp(operand_a, operand_b)
        else:
            self.pc += 2

    def dispatch(self, IR, opA, opB):
        self.branchtable[IR](opA, opB)

    def load(self):
        """Load a program into memory."""

        if len(sys.argv) is not 2:
            print(f"usage: {sys.argv[0]} <filename>")
            sys.exit(1)
        try:
            address = 0
            program_name = sys.argv[1]
            with open(program_name) as f:
                for line in f:
                    num = line.split("#", 1)[0]
                    if num.strip() == '':
                        continue
                    num = '0b' + num
                    self.ram[address] = int(num, 2)
                    address += 1
        except FileNotFoundError:
            print(f"{sys.argv[0]}: {sys.argv[1]} not found")
            sys.exit(2)

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value
        pass

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.register[reg_a] += self.register[reg_b]
        elif op == "SUB":
            self.register[reg_a] -= self.register[reg_b]
        elif op == "MUL":
            self.register[reg_a] *= self.register[reg_b]
        elif op == "DIV":
            self.register[reg_a] /= self.register[reg_b]
        elif op == "CMP":
            if self.register[reg_a] > self.register[reg_b]:
                self.register[6] = 0b00000010
                self.pc += 3
            elif self.register[reg_a] < self.register[reg_b]:
                self.register[6] = 0b00000100
                self.pc += 3
            elif self.register[reg_a] == self.register[reg_b]:
                self.register[6] = 0b00000001
                self.pc += 3
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.register[i], end='')
        print()

    def run(self):
        running = True
        while running:
            IR = self.pc
            operand_a = self.ram_read(IR + 1)
            operand_b = self.ram_read(IR + 2)
            if self.ram[IR] == int(0b00000001):
                print("HALT")
                running = False
            else:
                self.dispatch(self.ram[IR], operand_a, operand_b)

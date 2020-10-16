"""CPU functionality."""

import sys

# instruction codes
HLT = 0b00000001 # stop
LDI = 0b10000010 # sets a specified register to a value
PRN = 0b01000111 # print
ADD = 0b10100000 # add
SUB = 0b10100001 # subtract
MUL = 0b10100010 # multiply
PUSH = 0b01000101 # push onto the stack
POP = 0b01000110 # pop off the stack
CALL = 0b01010000 # call
RET = 0b00010001 # return
CMP = 0b10100111 # compare
JMP = 0b01010100 # jump
JEQ = 0b01010101 # equal
JNE = 0b01010110 # not equal

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # ram holds 256 bytes of memory
        self.ram = [0] * 256
        # holding 8 general-purpose registers
        self.reg = [0] * 8
        # program counter (pc)
        self.pc = 0
        # stack pointer (sp)
        self.sp = 7
        # CPU running
        self.running = True

    def ram_read(self, address):
        # return the ram at the specified, indexed address
        return self.ram[address]

    # defining a function to overwrite the ram value at the given address
    def ram_write(self, value, address):
        # set the ram at the specified, indexed address, as the value
        self.ram[address] = value

    def load(self, filename=None):
        """Load a program into memory."""

        address = 0

        with open(filename, 'r') as f:
            for line in f:
                line = line.split("#")[0].strip()
                if line == '':
                    continue
                self.ram[address] = int(line, 2)
                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op =='SUB':
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.flag = 0b00000001
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.flag = 0b00000100
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.flag = 0b00000010
        else:
            raise Exception("Unsupported ALU operation")


    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()


    def run(self):
        """Run the CPU."""
        while self.running:
            # self.trace()
            # instruction register
            instruction_register = self.ram_read(self.pc)
            # in case the instructions need them
            operand_a, operand_b = self.ram_read(self.pc + 1), self.ram_read(self.pc + 2)
            # perform the actions needed for instruction per the LS-8 spec
            # halt the CPU (and exit the emulator)
            if instruction_register == HLT:
                self.running = False
            # set the value of the register to an integer
            elif instruction_register == LDI:
                self.reg[operand_a] = operand_b
                self.pc += 3
            # print numeric value stored in the given register
            elif instruction_register == PRN:
                print(self.reg[operand_a])
                self.pc += 2
            elif instruction_register == ADD:
                self.alu("ADD", operand_a, operand_b)
                self.pc += 3
            elif instruction_register == SUB:
                self.alu("SUB", operand_a, operand_b)
                self.pc += 3
            elif instruction_register == MUL:
                self.alu("MUL", operand_a, operand_b)
                self.pc += 3
            elif instruction_register == CMP:
                self.alu("CMP", operand_a, operand_b)
                self.pc += 3
            elif instruction_register == JMP:
                self.pc = self.reg[operand_a]
            elif instruction_register == JEQ:
                if self.flag == 0b00000001:
                    self.pc = self.reg[operand_a]
                else:
                    self.pc += 2 
            elif instruction_register == JNE:
                if self.flag != 0b00000001:
                    self.pc = self.reg[operand_a]
                else:
                    self.pc += 2
            elif instruction_register == PUSH:
                # decrement the stack pointer
                self.reg[self.sp] -= 1
                # store the value at that address
                self.ram_write(self.reg[operand_a], self.reg[self.sp])
                # increment the program counter
                self.pc += 2
            elif instruction_register == POP:
                # take the value that is stored at the top of the stack
                self.reg[operand_a] = self.ram_read(self.reg[self.sp])
                # increment the stack pointer
                self.reg[self.sp] += 1
                # increment the program counter
                self.pc += 2
            elif instruction_register == CALL:
                # decrement the stack pointer
                self.reg[self.sp] -= 1
                # push the address of the instruction after it onto the stack
                self.ram_write(self.pc + 2, self.reg[self.sp])
                # move the program counter to the subroutine address
                self.pc = self.reg[operand_a]
            elif instruction_register == RET:
                # pop the address off the stack and store it in the program counter
                self.pc = self.ram_read(self.reg[self.sp])
                # increment the stack pointer
                self.reg[self.sp] += 1
            else: 
                print("Instruction not valid")



# python3 ls8.py examples/mult.ls8
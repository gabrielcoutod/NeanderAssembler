import argparse
from instruction import Instruction


class NeanderAssembler:
    """ Assembler for neander. """

    # instructions
    INSTRUCTIONS = {
        "NOP": Instruction("NOP", 0, "0"),
        "STA": Instruction("STA", 1, "16"),
        "LDA": Instruction("LDA", 1, "32"),
        "ADD": Instruction("ADD", 1, "48"),
        "OR": Instruction("OR", 1, "64"),
        "AND": Instruction("AND", 1, "80"),
        "NOT": Instruction("NOT", 0, "96"),
        "JMP": Instruction("JMP", 1, "128"),
        "JN": Instruction("JN", 1, "144"),
        "JZ": Instruction("JZ", 1, "160"),
        "HLT": Instruction("HLT", 0, "240"),
        "DB": Instruction("DB", 1),
        "ORG": Instruction("ORG", 1)
    }
    # memory size
    MEM_SIZE = 256

    def __init__(self, file_path, mem_path):
        self.names = {}  # names defined in the file
        self.mem = ["0" for i in range(NeanderAssembler.MEM_SIZE)]  # stores values for the mem file
        self.lines = None  # lines inside the file
        self.index = 0  # current position on mem
        self.file_path = file_path  # file to read from
        self.mem_path = mem_path  # file to write to

    @staticmethod
    def parse_args():
        """ Arguments to parse when calling neander_assembly.py. """
        parser = argparse.ArgumentParser(description="Assembler for Neander")
        parser.add_argument("file_path", metavar="SOURCE", type=str, help="Path of the file to read")
        parser.add_argument("mem_path", metavar="MEM", type=str, help="Path of the mem file")
        return parser.parse_args()

    def open_file(self):
        """ Opens File to read. """
        with open(self.file_path) as file:
            self.lines = file.readlines()

    def read_lines(self):
        """ Puts the instructions in their positions. """
        for full_line in self.lines:
            # removes comments and blank spaces at the beg and end and capitalizes all letters
            line = NeanderAssembler.remove_comment(full_line).upper().strip()
            if line:  # if isn't a full line comment or empty line
                index_colon = line.find(":")
                if index_colon != -1:  # if has a label
                    name = line[0:index_colon]
                    # if not illegal label
                    if NeanderAssembler.is_label(name):
                        self.names[name] = f"{self.index}"
                        line = line[index_colon + 1:].lstrip()
                        if line:
                            self.read_instruction(line)
                    else:
                        raise Exception(f"Illegal label at {full_line}")
                else:
                    self.read_instruction(line)

    @staticmethod
    def remove_comment(string):
        """ Returns the given string without comments. """
        index_semicolon = string.find(";")
        index_comment = len(string) if index_semicolon == -1 else index_semicolon
        return string[0:index_comment]

    @staticmethod
    def is_label(string):
        """ Returns True if the given string is a valid label, else returns false"""
        return string and string not in NeanderAssembler.INSTRUCTIONS.keys() and \
            not string[0].isdigit() and NeanderAssembler.is_alpha_number_underline(string)

    @staticmethod
    def is_alpha_number_underline(string):
        """ Given a string returns true if all chars are either numbers, alphabets or underline """
        for char in string:
            if not char.isdigit() and not char.isalpha() and not char == "_":
                return False
        return True

    def read_instruction(self, line):
        """ Given an instruction line puts it in the mem object. """
        args = line.split()
        instruction = NeanderAssembler.INSTRUCTIONS.get(args[0])  # gets the instruction object
        if instruction:  # if it is a valid instruction
            if len(args) == 1 and instruction.number_args == 0:  # instructions with 0 args
                self.mem[self.index] = instruction.value
                self.index = (self.index + 1) % NeanderAssembler.MEM_SIZE
            elif len(args) == 2 and instruction.number_args == 1:  # instructions with 1 arg
                if args[1] in NeanderAssembler.INSTRUCTIONS.keys():  # if the arg is a reserved word
                    raise Exception(f"Reserved word as argument at {line}")
                elif instruction.name == "DB":
                    self.mem[self.index] = args[1]
                    self.index = (self.index + 1) % NeanderAssembler.MEM_SIZE
                elif instruction.name == "ORG":
                    if args[1].isdigit():
                        self.index = int(args[1])
                    elif self.names.get(args[1]):
                        self.index = int(self.names[args[1]])
                    else:
                        raise Exception(f"Name {args[1]} not defined before {line}")
                else:  # regular 1 arg instructions
                    self.mem[self.index] = instruction.value
                    self.index = (self.index + 1) % NeanderAssembler.MEM_SIZE
                    self.mem[self.index] = args[1]
                    self.index = (self.index + 1) % NeanderAssembler.MEM_SIZE
            else:  # incorrect number of args, len(args) != instruction.number_args + 1
                raise Exception(f"Incorrect number of arguments in {line}")
        else:
            raise Exception(f"Undefined instruction in {line}")

    def replace_names(self):
        """ Replaces names with their value. """
        for i in range(NeanderAssembler.MEM_SIZE):
            if self.mem[i] in self.names.keys():
                self.mem[i] = self.names[self.mem[i]]
            elif not NeanderAssembler.is_digit(self.mem[i]):
                raise Exception(f"Undefined name {self.mem[i]}")

    @staticmethod
    def is_digit(string):
        try:
            int(string)
            return True
        except ValueError:
            return False

    def write(self):
        """ Writes the mem file. """
        with open(self.mem_path, "wb") as mem_file:
            mem_file.write(bytearray([3, 78, 68, 82]))  # writes mem file specifics
            for val in self.mem:  # writes mem bytes
                mem_file.write(bytearray([int(val) % NeanderAssembler.MEM_SIZE, 0]))


if __name__ == '__main__':
    cli_args = NeanderAssembler.parse_args()
    neander = NeanderAssembler(cli_args.file_path, cli_args.mem_path)
    neander.open_file()
    neander.read_lines()
    neander.replace_names()
    neander.write()
    print("DONE")

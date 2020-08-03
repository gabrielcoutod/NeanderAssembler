class Instruction:
    """ Represents a neander instruction. """
    def __init__(self, name, number_args, value=None):
        self.name = name
        self.number_args = number_args
        self.value = value

import random

class CellularAutomaton2D:
    def __init__(self, rule_function, size, seed=None):
        self.rule_function = rule_function
        self.size = size
        self.state = self.initialize_state(seed)

    def initialize_state(self, seed):
        random.seed(seed)
        return [[random.choice([0, 1]) for _ in range(self.size)] for _ in range(self.size)]

    def apply_rule(self):
        self.state = self.rule_function(self.state)

    def generate_sequence(self, steps):
        sequence = []
        for _ in range(steps):
            self.apply_rule()
            for row in self.state:
                sequence.extend(row)
        return sequence

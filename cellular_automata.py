import random

def initialize_automaton(block_size, seed):
    """Создает случайное начальное состояние автомата фиксированной длины блока."""
    random.seed(seed)
    return [random.choice([0, 1]) for _ in range(block_size)]

def apply_rule(state, rule_function):
    new_state = [0] * len(state)
    for i in range(len(state)):
        left = state[i - 1] if i > 0 else state[-1]
        center = state[i]
        right = state[i + 1] if i < len(state) - 1 else state[0]
        new_state[i] = rule_function(left, center, right)
    return new_state

def generate_sequence(rule_function, block_size, steps, initial_state):
    state = initial_state
    sequence = []
    for _ in range(steps):
        state = apply_rule(state, rule_function)
        sequence.extend(state)
    return sequence, state

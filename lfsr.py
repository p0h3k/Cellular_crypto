import random

def generate_random_taps(length):
    """Генерирует случайные позиции для обрабатываемых бит для LFSR."""
    return random.sample(range(length), k=2)

def lfsr(taps, initial_state, steps):
    """Создает псевдослучайную последовательность, используя LFSR."""
    state = initial_state[:]
    output = []
    n = len(initial_state)

    for _ in range(steps):
        new_bit = 0
        for tap in taps:
            new_bit ^= state[tap]

        output.append(state[-1])
        state = [new_bit] + state[:-1]

    return output, state, taps

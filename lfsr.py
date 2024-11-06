import random

def generate_random_taps(length):
    """Генерирует случайные позиции для обрабатываемых бит для LFSR."""
    if length > 1:
        return random.sample(range(length), k=min(2, length))  # Использует хотя бы два элемента
    else:
        return [0]  # Для случаев длиной 1 или меньше

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

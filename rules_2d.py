def complex_rule_1(automaton):
    """Определяет сложное правило 1 для двумерного клеточного автомата."""
    size = len(automaton)
    new_automaton = [[0] * size for _ in range(size)]

    for i in range(size):
        for j in range(size):
            left = automaton[i][(j - 1) % size]
            right = automaton[i][(j + 1) % size]
            top = automaton[(i - 1) % size][j]
            bottom = automaton[(i + 1) % size][j]
            top_left = automaton[(i - 1) % size][(j - 1) % size]
            top_right = automaton[(i - 1) % size][(j + 1) % size]
            bottom_left = automaton[(i + 1) % size][(j - 1) % size]
            bottom_right = automaton[(i + 1) % size][(j + 1) % size]

            cell = automaton[i][j]
            transition = (
                (cell & (left ^ right)) |
                (((top & bottom) ^ (top_left | bottom_right)) & (top_right ^ bottom_left))
            )
            new_automaton[i][j] = cell ^ transition

    return new_automaton

def complex_rule_2(automaton):
    """Определяет сложное правило 2 для двумерного клеточного автомата."""
    size = len(automaton)
    new_automaton = [[0] * size for _ in range(size)]

    for i in range(size):
        for j in range(size):
            left = automaton[i][(j - 1) % size]
            right = automaton[i][(j + 1) % size]
            top = automaton[(i - 1) % size][j]
            bottom = automaton[(i + 1) % size][j]
            center = automaton[i][j]
            transition = (center | left) ^ (right & top) ^ (bottom | (left & right))
            new_automaton[i][j] = center ^ transition

    return new_automaton


def complex_rule_3(automaton):
    """Определяет сложное правило 3 для двумерного клеточного автомата."""
    size = len(automaton)
    new_automaton = [[0] * size for _ in range(size)]

    for i in range(size):
        for j in range(size):
            # Получаем значения соседних ячеек
            left = automaton[i][(j - 1) % size]
            right = automaton[i][(j + 1) % size]
            top = automaton[(i - 1) % size][j]
            bottom = automaton[(i + 1) % size][j]
            top_left = automaton[(i - 1) % size][(j - 1) % size]
            top_right = automaton[(i - 1) % size][(j + 1) % size]
            bottom_left = automaton[(i + 1) % size][(j - 1) % size]
            bottom_right = automaton[(i + 1) % size][(j + 1) % size]
            center = automaton[i][j]

            # Более сложные вычисления перехода
            # Эти операции включают использование сдвига и XOR с дополнением
            transition = (
                (((left & right) | (top & bottom)) ^ (top_left | bottom_right)) ^
                (((top_right & bottom_left) | center) ^ ((~left ^ right) & (~top ^ bottom)))
            )

            # Применение найденного перехода к центральной ячейке
            new_automaton[i][j] = int(bool(center) ^ bool(transition))

    return new_automaton

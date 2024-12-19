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

            # Приводим значения к булевым
            left = bool(left)
            right = bool(right)
            top = bool(top)
            bottom = bool(bottom)
            top_left = bool(top_left)
            top_right = bool(top_right)
            bottom_left = bool(bottom_left)
            bottom_right = bool(bottom_right)
            cell = bool(cell)

            transition = (
                (cell and (left != right)) or
                (((top and bottom) != (top_left or bottom_right)) and (top_right != bottom_left))
            )

            new_automaton[i][j] = int(cell != transition)

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

            # Приводим значения к булевым
            left = bool(left)
            right = bool(right)
            top = bool(top)
            bottom = bool(bottom)
            center = bool(center)

            transition = (center or left) != (right and top) != (bottom or (left and right))

            new_automaton[i][j] = int(center != transition)

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

            # Приводим значения к булевым
            left = bool(left)
            right = bool(right)
            top = bool(top)
            bottom = bool(bottom)
            top_left = bool(top_left)
            top_right = bool(top_right)
            bottom_left = bool(bottom_left)
            bottom_right = bool(bottom_right)
            center = bool(center)

            # Выполняем логические операции вместо побитовых
            transition = (
                (((left and right) or (top and bottom)) != (top_left or bottom_right)) !=
                (((top_right and bottom_left) or center) != ((not left != right) and (not top != bottom)))
            )

            new_automaton[i][j] = int(center != transition)

    return new_automaton

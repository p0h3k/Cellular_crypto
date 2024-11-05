def rule_30(left, center, right):
    """Реализация правила 30."""
    return (left and not center and not right) or \
           (not left and center and right) or \
           (not left and center and not right) or \
           (not left and not center and right)

def rule_182(left, center, right):
    """Реализация правила 182."""
    return (left and right) or (not left and center and not right)

def rule_126(left, center, right):
    """Реализация правила 126."""
    return (left and not center) or (left and right) or (center and right) or (center and not right)

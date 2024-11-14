def rule_30(left, center, right):
    """Реализация правила 30."""
    return (left and not center and not right) or \
           (not left and center and right) or \
           (not left and center and not right) or \
           (not left and not center and right)

def rule_90(left, center, right):
    """Реализация правила 90."""
    return left ^ right

def rule_150(left, center, right):
    """Реализация правила 150."""
    return left ^ center ^ right


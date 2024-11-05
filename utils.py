def to_bits(message):
    """Преобразует строковое сообщение в список бит."""
    return [int(bit) for char in message for bit in f"{ord(char):08b}"]

def from_bits(bits):
    """Преобразует список бит обратно в строку сообщения."""
    chars = [chr(int("".join(map(str, bits[i:i + 8])), 2)) for i in range(0, len(bits), 8)]
    return "".join(chars)

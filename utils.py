# utils.py

def to_bits(data):
    """Преобразует байты в список битов."""
    bits = []
    for byte in data:
        bits.extend([int(bit) for bit in bin(byte)[2:].zfill(8)])
    return bits

def from_bits(bits):
    """Преобразует список битов обратно в байты."""
    bytes_list = []
    for b in range(0, len(bits), 8):
        byte = bits[b:b+8]
        bytes_list.append(int(''.join(map(str, byte)), 2))
    return bytes(bytes_list)

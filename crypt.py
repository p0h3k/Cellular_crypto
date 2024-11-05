def xor_process(message_bits, keystream):
    """Шифрует/расшифровывает сообщение с помощью XOR и заданного потока ключей."""
    return [mb ^ kb for mb, kb in zip(message_bits, keystream)]

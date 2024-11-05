import json
import base64
from utils import to_bits, from_bits
import cellular_automata as ca
import lfsr as lfsr_module
from crypt import xor_process
import rules
import random

def decrypt_message(encrypted_message, key_details):
    """Расшифровывает сообщение с использованием предоставленного ключа."""
    # Парсинг ключа из JSON-строки
    key = json.loads(key_details)

    # Восстановление параметров из ключа
    rules_map = {
        'rule_30': rules.rule_30,
        'rule_182': rules.rule_182,
        'rule_126': rules.rule_126
    }
    selected_rules = [rules_map[name] for name in key['rules']]
    seeds = key['seeds']
    lfsr_seed = key['lfsr_seed']
    taps = key['taps']

    # Преобразование зашифрованного сообщения из Base64
    encrypted_bits = to_bits(base64.b64decode(encrypted_message).decode('utf-8'))

    automaton_size = len(encrypted_bits)

    # Восстановление последовательностей клеточного автомата
    sequences = []
    for rule, seed in zip(selected_rules, seeds):
        initial_state = ca.initialize_automaton(automaton_size, seed)
        sequence, _ = ca.generate_sequence(rule, automaton_size, 1, initial_state)
        sequences.append(sequence)

    combined_sequence = [sum(bits) % 2 for bits in zip(*sequences)]

    # Восстановление LFSR последовательности
    # Используем тот же метод преобразования lfsr_seed в двоичное начальное состояние
    lfsr_initial_state = [int(x) for x in bin(lfsr_seed)[2:].zfill(automaton_size)]
    if len(lfsr_initial_state) != automaton_size:
        raise ValueError(f"Ошибка: длина начального состояния LFSR должна быть {automaton_size}")

    lfsr_sequence, _, _ = lfsr_module.lfsr(taps, lfsr_initial_state, automaton_size)

    # Генерация итогового потока ключей
    final_keystream = [b1 ^ b2 for b1, b2 in zip(combined_sequence, lfsr_sequence)]

    # Расшифровка сообщения
    decrypted_bits = xor_process(encrypted_bits, final_keystream)
    decrypted_message = from_bits(decrypted_bits)
    return decrypted_message

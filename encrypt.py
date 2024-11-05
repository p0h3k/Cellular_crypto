# encrypt.py

import random
import base64
import json
from utils import to_bits, from_bits
import cellular_automata as ca
import lfsr as lfsr_module
from crypt import xor_process
import rules

def encrypt_message(message, manual_seed=None, key_details=None):
    """Шифрует сообщение с использованием нового или существующего ключа."""
    if key_details:
        # Используем существующий ключ
        key = json.loads(key_details)
        
        selected_rules = [getattr(rules, rule) for rule in key['rules']]
        seeds = key['seeds']
        lfsr_seed = key['lfsr_seed']
        taps = key['taps']
    else:
        # Создаем новый ключ
        num_automata = int(input("Сколько клеточных автоматов использовать? "))

        rule_choices = {
            '30': rules.rule_30,
            '182': rules.rule_182,
            '126': rules.rule_126
        }

        selected_rules = []
        seeds = []
        for i in range(num_automata):
            rule_number = input(f"Выберите правило для автомата {i+1} (30, 182, 126): ")
            selected_rules.append(rule_choices[rule_number])
            if manual_seed:
                seed = manual_seed[i]
            else:
                seed = random.getrandbits(32)
            seeds.append(seed)
        
        lfsr_seed = random.getrandbits(32)
        taps = lfsr_module.generate_random_taps(len(message))
        if manual_seed:
            lfsr_seed, taps = manual_seed[-1], manual_seed[-2]

    message_bits = to_bits(message)
    automaton_size = len(message_bits)

    # Создание последовательностей клеточного автомата
    sequences = []
    for i, rule in enumerate(selected_rules):
        initial_state = ca.initialize_automaton(automaton_size, seeds[i])
        sequence, _ = ca.generate_sequence(rule, automaton_size, 1, initial_state)
        sequences.append(sequence)

    combined_sequence = [sum(bits) % 2 for bits in zip(*sequences)]

    # Инициализация LFSR с заданными или случайными параметрами
    lfsr_initial_state = [int(x) for x in bin(lfsr_seed)[2:].zfill(automaton_size)]
    lfsr_sequence, _, _ = lfsr_module.lfsr(taps, lfsr_initial_state, automaton_size)

    # Генерация итогового потока ключей
    final_keystream = [b1 ^ b2 for b1, b2 in zip(combined_sequence, lfsr_sequence)]

    # Шифрование сообщения
    encrypted_bits = xor_process(message_bits, final_keystream)
    encrypted_bytes = bytes(from_bits(encrypted_bits), 'utf-8')
    encrypted_base64 = base64.b64encode(encrypted_bytes).decode('utf-8')

    # Параметры ключа для расшифровки
    key_details = json.dumps({
        "rules": [rule.__name__ for rule in selected_rules],
        "seeds": seeds,
        "lfsr_seed": lfsr_seed,
        "taps": taps
    })

    return encrypted_base64, key_details

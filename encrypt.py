# encrypt.py

import random
import base64
import json
from utils import to_bits, from_bits
import cellular_automata as ca
import cellular_automata_2d as ca2d
import lfsr as lfsr_module
from crypt import xor_process
import rules
import rules_2d

def encrypt_message(message, manual_seed=None, key_details=None, return_keystream=False):
    rule_choices_1d = {
        'rule_30': rules.rule_30,
        'rule_90': rules.rule_90,
        'rule_150': rules.rule_150,
    }

    rule_choices_2d = {
        'complex_rule_1': rules_2d.complex_rule_1,
        'complex_rule_2': rules_2d.complex_rule_2,
        'complex_rule_3': rules_2d.complex_rule_3
    }

    if key_details:
        key = json.loads(key_details)
        selected_rules = [
            getattr(rules if rule in ['rule_30', 'rule_90', 'rule_150'] else rules_2d, rule)
            for rule in key['rules']
        ]
        seeds = key['seeds']
        lfsr_seed = key['lfsr_seed']
        taps = key['taps']
        block_size = key['block_size']
    else:
        num_automata = int(input("Сколько клеточных автоматов использовать? "))
        block_size = int(input("Введите размер блока для шифрования: "))

        selected_rules = []
        seeds = []
        for i in range(num_automata):
            type_choice = input(f"Выберите тип автомата для {i+1} (1D, 2D): ").strip()
            if type_choice == '1D':
                rule_number = input(f"Выберите правило для автомата {i+1} (30, 90, 150): ").strip()
                selected_rules.append(rule_choices_1d[f'rule_{rule_number}'])
            elif type_choice == '2D':
                rule_name = input(f"Выберите правило для автомата {i+1} (complex_rule_1, complex_rule_2, complex_rule_3): ").strip()
                selected_rules.append(rule_choices_2d[rule_name])
            else:
                print("Неверный выбор типа автомата.")
                return

            seed_input = input(f"Введите начальное состояние для автомата {i+1} или оставьте пустым для случайного: ").strip()
            seed = int(seed_input) if seed_input else random.getrandbits(block_size)
            seeds.append(seed)

        lfsr_seed_input = input("Введите начальное состояние LFSR или оставьте пустым для случайного: ").strip()
        lfsr_seed = int(lfsr_seed_input) if lfsr_seed_input else random.getrandbits(block_size)

        taps_input = input("Введите биты сдвига LFSR через запятую или оставьте пустым для случайного: ").strip()
        if taps_input:
            taps = list(map(int, taps_input.split(',')))
        else:
            taps = lfsr_module.generate_random_taps(block_size)

    # Преобразование сообщения в байты и затем в биты
    message_bytes = message.encode('utf-8')
    message_bits = to_bits(message_bytes)
    total_length = len(message_bits)
    # Паддинг, если необходимо
    if len(message_bits) % block_size != 0:
        padded_bits = message_bits + [0] * (block_size - len(message_bits) % block_size)
    else:
        padded_bits = message_bits
    bit_blocks = [padded_bits[i:i + block_size] for i in range(0, len(padded_bits), block_size)]

    # Подготовка полного ключевого потока
    complete_sequence = []
    for rule, seed in zip(selected_rules, seeds):
        if rule.__name__ in ['rule_30', 'rule_90', 'rule_150']:
            initial_state = ca.initialize_automaton(block_size, seed)
            sequence, _ = ca.generate_sequence(rule, block_size, (total_length // block_size) + 1, initial_state)
            complete_sequence.extend(sequence[:total_length])
        else:
            size = int(block_size ** 0.5)
            automaton = ca2d.CellularAutomaton2D(rule, size, seed)
            sequence = automaton.generate_sequence((total_length // (block_size)) + 1)
            flat_sequence = [bit for block in sequence for bit in block]
            complete_sequence.extend(flat_sequence[:total_length])

    # Проверка и генерация дополнительного ключевого потока, если необходимо
    while len(complete_sequence) < total_length:
        for rule, seed in zip(selected_rules, seeds):
            if rule.__name__ in ['rule_30', 'rule_90', 'rule_150']:
                initial_state = ca.initialize_automaton(block_size, seed)
                sequence, _ = ca.generate_sequence(rule, block_size, 1, initial_state)
                complete_sequence.extend(sequence)
            else:
                size = int(block_size ** 0.5)
                automaton = ca2d.CellularAutomaton2D(rule, size, seed)
                sequence = automaton.generate_sequence(1)
                flat_sequence = [bit for block in sequence for bit in block]
                complete_sequence.extend(flat_sequence)

    # Шифрование
    encrypted_bits = []
    for i, block in enumerate(bit_blocks):
        start_idx = i * block_size
        key_block = complete_sequence[start_idx:start_idx + block_size]
        encrypted_block = [b1 ^ b2 for b1, b2 in zip(block, key_block)]
        encrypted_bits.extend(encrypted_block)

    # Применение LFSR
    lfsr_initial_state = [int(x) for x in bin(lfsr_seed)[2:].zfill(len(taps))]
    lfsr_sequence, _, _ = lfsr_module.lfsr(taps, lfsr_initial_state, len(encrypted_bits))
    final_keystream = xor_process(encrypted_bits, lfsr_sequence)

    encrypted_bytes = from_bits(final_keystream)
    encrypted_base64 = base64.b64encode(encrypted_bytes).decode('utf-8')

    key_details = json.dumps({
        "rules": [rule.__name__ for rule in selected_rules],
        "seeds": seeds,
        "lfsr_seed": lfsr_seed,
        "taps": taps,
        "block_size": block_size
    })

    if return_keystream:
        return encrypted_base64, key_details, final_keystream
    return encrypted_base64, key_details

import random
import base64
import json
import logging
from utils import to_bits, from_bits
import cellular_automata as ca
import cellular_automata_2d as ca2d
import lfsr as lfsr_module
from crypt import xor_process
import rules
import rules_2d

# Настройка базового логирования (добавьте конфигурацию согласно вашим предпочтениям)
logging.basicConfig(level=logging.DEBUG)

def encrypt_message(message, manual_seed=None, key_details=None):
    rule_choices_1d = {
        'rule_30': rules.rule_30,
        'rule_182': rules.rule_182,
        'rule_126': rules.rule_126
    }

    rule_choices_2d = {
        'complex_rule_1': rules_2d.complex_rule_1,
        'complex_rule_2': rules_2d.complex_rule_2
    }

    if key_details:
        key = json.loads(key_details)
        selected_rules = [
            rule_choices_1d.get(rule) or rule_choices_2d.get(rule)
            for rule in key['rules']
        ]

        # Debug logging
        logging.debug(f"Parsed rules: {key['rules']}")
        logging.debug(f"Selected rules: {[rule.__name__ if rule else 'None' for rule in selected_rules]}")

        # Проверка правил на наличие None
        for rule in selected_rules:
            if rule is None:
                raise ValueError("Некоторые из правил не были правильно определены.")

        seeds = key['seeds']
        lfsr_seed = key['lfsr_seed']
        taps = key['taps']
        block_size = key['block_size']
    else:
        # Логическое продолжение существующего кода
        ...

    message_bits = to_bits(message)
    total_length = len(message_bits)
    padded_bits = message_bits + [0] * (block_size - len(message_bits) % block_size)
    bit_blocks = [padded_bits[i:i + block_size] for i in range(0, len(padded_bits), block_size)]

    complete_sequence = []
    for rule in selected_rules:
        if rule in rule_choices_1d.values():
            for seed in seeds:
                initial_state = ca.initialize_automaton(block_size, seed)
                sequence, _ = ca.generate_sequence(rule, block_size, total_length // block_size + 1, initial_state)
                complete_sequence.extend(sequence[:total_length])
        else:
            for seed in seeds:
                size = int(block_size ** 0.5)
                automaton = ca2d.CellularAutomaton2D(rule, size, seed)
                sequence = automaton.generate_sequence(total_length // block_size + 1)
                complete_sequence.extend(sequence[:total_length])

    lfsr_initial_state = [int(x) for x in bin(lfsr_seed)[2:].zfill(block_size)]
    lfsr_sequence, _, _ = lfsr_module.lfsr(taps, lfsr_initial_state, total_length)

    # XOR with LFSR sequence to get the final keystream
    final_keystream = xor_process(complete_sequence, lfsr_sequence)

    # Запись финальной последовательности в файл
    with open('encryption_keystream.txt', 'w') as f:
        f.write(''.join(map(str, final_keystream)))

    encrypted_bits = []
    for i, block in enumerate(bit_blocks):
        key_block = final_keystream[i * block_size:(i + 1) * block_size]
        encrypted_block = [b1 ^ b2 for b1, b2 in zip(block, key_block)]
        encrypted_bits.extend(encrypted_block)

    encrypted_bytes = bytes(from_bits(encrypted_bits), 'latin1')
    encrypted_base64 = base64.b64encode(encrypted_bytes).decode('utf-8')

    key_details = json.dumps({
        "rules": [rule.__name__ for rule in selected_rules],
        "seeds": seeds,
        "lfsr_seed": lfsr_seed,
        "taps": taps,
        "block_size": block_size
    })

    return encrypted_base64, key_details

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

def encrypt_message(message, manual_seed=None, key_details=None):
    rule_choices_1d = {
        '30': rules.rule_30,
        '90': rules.rule_90,
        '150': rules.rule_150,
    }

    rule_choices_2d = {
        'complex_rule_1': rules_2d.complex_rule_1,
        'complex_rule_2': rules_2d.complex_rule_2,
        'complex_rule_3': rules_2d.complex_rule_3
    }

    if key_details:
        key = json.loads(key_details)
        selected_rules = [getattr(rules if rule in ['rule_30', 'rule_90', 'rule_150'] else rules_2d, rule) for rule in key['rules']]
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
            type_choice = input(f"Выберите тип автомата для {i+1} (1D, 2D): ")
            if type_choice == '1D':
                rule_number = input(f"Выберите правило для автомата {i+1} (30, 90, 150): ")
                selected_rules.append(rule_choices_1d[rule_number])
            else:
                rule_name = input(f"Выберите правило для автомата {i+1} (complex_rule_1, complex_rule_2, complex_rule_3): ")
                selected_rules.append(rule_choices_2d[rule_name])
            seed = random.getrandbits(32) if not manual_seed else manual_seed[i]
            seeds.append(seed)

        lfsr_seed = random.getrandbits(32)
        taps = lfsr_module.generate_random_taps(block_size)
        
        if manual_seed:
            lfsr_seed, taps = manual_seed[-1], manual_seed[-2]

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

    encrypted_bits = []
    for i, block in enumerate(bit_blocks):
        key_block = complete_sequence[i * block_size:(i + 1) * block_size]
        encrypted_block = [b1 ^ b2 for b1, b2 in zip(block, key_block)]
        encrypted_bits.extend(encrypted_block)

    lfsr_initial_state = [int(x) for x in bin(lfsr_seed)[2:].zfill(block_size)]
    lfsr_sequence, _, _ = lfsr_module.lfsr(taps, lfsr_initial_state, len(encrypted_bits))

    final_keystream = xor_process(encrypted_bits, lfsr_sequence)
    with open('encryption_keystream.txt', 'w') as f:
        f.write(''.join(map(str, final_keystream)))
    
    encrypted_bytes = bytes(from_bits(final_keystream), 'latin1')
    encrypted_base64 = base64.b64encode(encrypted_bytes).decode('utf-8')

    key_details = json.dumps({
        "rules": [rule.__name__ for rule in selected_rules],
        "seeds": seeds,
        "lfsr_seed": lfsr_seed,
        "taps": taps,
        "block_size": block_size
    })

    return encrypted_base64, key_details

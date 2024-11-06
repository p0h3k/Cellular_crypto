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
        key = json.loads(key_details)
        selected_rules = [getattr(rules, rule) for rule in key['rules']]
        seeds = key['seeds']
        lfsr_seed = key['lfsr_seed']
        taps = key['taps']
    else:
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
            seed = random.getrandbits(32) if not manual_seed else manual_seed[i]
            seeds.append(seed)
        
        lfsr_seed = random.getrandbits(32)
        message_bits = to_bits(message)
        automaton_size = len(message_bits)
        lfsr_initial_state = [int(x) for x in bin(lfsr_seed)[2:].zfill(automaton_size)]
        taps = lfsr_module.generate_random_taps(len(lfsr_initial_state))
        if manual_seed:
            lfsr_seed, taps = manual_seed[-1], manual_seed[-2]

    sequences = []
    for rule, seed in zip(selected_rules, seeds):
        initial_state = ca.initialize_automaton(automaton_size, seed)
        sequence, _ = ca.generate_sequence(rule, automaton_size, automaton_size, initial_state)
        sequences.append(sequence)

    combined_sequence = [0] * automaton_size
    for seq in sequences:
        combined_sequence = [b1 ^ b2 for b1, b2 in zip(combined_sequence, seq)]

    lfsr_sequence, _, _ = lfsr_module.lfsr(taps, lfsr_initial_state, automaton_size)

    final_keystream = [b1 ^ b2 for b1, b2 in zip(combined_sequence, lfsr_sequence)]
    
    print("Ключевая последовательность для шифрования:", ''.join(map(str, final_keystream)))

    encrypted_bits = xor_process(message_bits, final_keystream)
    encrypted_bytes = bytes(from_bits(encrypted_bits), 'latin1')
    encrypted_base64 = base64.b64encode(encrypted_bytes).decode('utf-8')
    
    key_details = json.dumps({
        "rules": [rule.__name__ for rule in selected_rules],
        "seeds": seeds,
        "lfsr_seed": lfsr_seed,
        "taps": taps
    })

    return encrypted_base64, key_details

import json
import base64
from utils import to_bits, from_bits
import cellular_automata as ca
import lfsr as lfsr_module
from crypt import xor_process
import rules

def decrypt_message(encrypted_message, key_details):
    """Расшифровывает сообщение с использованием предоставленного ключа."""
    key = json.loads(key_details)

    rules_map = {
        'rule_30': rules.rule_30,
        'rule_182': rules.rule_182,
        'rule_126': rules.rule_126
    }
    selected_rules = [rules_map[name] for name in key['rules']]
    seeds = key['seeds']
    lfsr_seed = key['lfsr_seed']
    taps = key['taps']

    encrypted_bytes = base64.b64decode(encrypted_message)
    encrypted_bits = to_bits(encrypted_bytes.decode('latin1'))

    automaton_size = len(encrypted_bits)

    sequences = []
    for rule, seed in zip(selected_rules, seeds):
        initial_state = ca.initialize_automaton(automaton_size, seed)
        sequence, _ = ca.generate_sequence(rule, automaton_size, automaton_size, initial_state)
        sequences.append(sequence)

    combined_sequence = [0] * automaton_size
    for seq in sequences:
        combined_sequence = [b1 ^ b2 for b1, b2 in zip(combined_sequence, seq)]

    lfsr_initial_state = [int(x) for x in bin(lfsr_seed)[2:].zfill(automaton_size)]
    lfsr_sequence, _, _ = lfsr_module.lfsr(taps, lfsr_initial_state, automaton_size)

    final_keystream = [b1 ^ b2 for b1, b2 in zip(combined_sequence, lfsr_sequence)]

    decrypted_bits = xor_process(encrypted_bits, final_keystream)
    decrypted_message = from_bits(decrypted_bits)

    print("Ключевая последовательность для дешифрования:", ''.join(map(str, final_keystream)))
    
    return decrypted_message

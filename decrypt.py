import json
import base64
from utils import to_bits, from_bits
import cellular_automata as ca
import cellular_automata_2d as ca2d
import lfsr as lfsr_module
from crypt import xor_process
import rules
import rules_2d

def decrypt_message(encrypted_message, key_details):
    key = json.loads(key_details)

    selected_rules = [getattr(rules if rule in ['rule_30', 'rule_90', 'rule_150'] else rules_2d, rule) for rule in key['rules']]
    seeds = key['seeds']
    lfsr_seed = key['lfsr_seed']
    taps = key['taps']
    block_size = key['block_size']

    encrypted_bytes = base64.b64decode(encrypted_message)
    encrypted_bits = to_bits(encrypted_bytes.decode('latin1'))

    total_length = len(encrypted_bits)
    bit_blocks = [encrypted_bits[i:i + block_size] for i in range(0, len(encrypted_bits), block_size)]

    complete_sequence = []
    for rule in selected_rules:
        if rule in [rules.rule_30, rules.rule_90, rules.rule_150]:
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

    decrypted_bits = []
    for i, block in enumerate(bit_blocks):
        key_block = complete_sequence[i * block_size:(i + 1) * block_size]
        decrypted_block = [b1 ^ b2 for b1, b2 in zip(block, key_block)]
        decrypted_bits.extend(decrypted_block)

    lfsr_initial_state = [int(x) for x in bin(lfsr_seed)[2:].zfill(block_size)]
    lfsr_sequence, _, _ = lfsr_module.lfsr(taps, lfsr_initial_state, len(decrypted_bits))

    final_stream = xor_process(decrypted_bits, lfsr_sequence)
    decrypted_message = from_bits(final_stream[:total_length])

    return decrypted_message

#!/usr/bin/env python3
"""
Debug script to check coil structure.
"""

import sys
sys.path.insert(0, '/home/alf/OpenMagnetics/PyMKF/build/cp312-cp312-linux_x86_64')

import PyOpenMagnetics as pom
import json

print('Setting up test data...')
core_input = {
    'functionalDescription': {
        'type': 'two-piece set', 
        'material': '3C95', 
        'shape': 'E 42/21/15', 
        'gapping': [{'type': 'subtractive', 'length': 0.0005}], 
        'numberStacks': 1
    }
}
core_data = pom.calculate_core_data(core_input, True)
bobbin = pom.create_basic_bobbin(core_data, True)
wire = pom.find_wire_by_name('Round 0.5 - Grade 1')
coil_spec = {
    'bobbin': bobbin,
    'functionalDescription': [{
        'name': 'Primary', 
        'numberTurns': 5, 
        'numberParallels': 1,
        'isolationSide': 'primary', 
        'wire': wire
    }]
}

# Use the full wind() function with proper arguments
# wind(coil, repetitions, proportion_per_winding, pattern, margin_pairs)
print('Winding with full wind() function...')
coil = pom.wind(
    coil_spec,
    1,               # repetitions
    [1.0],           # proportion_per_winding
    [0],             # pattern
    [[0.001, 0.001]] # margin_pairs
)
print('Coil wound.')

# Check what's in the coil
print(f'\nCoil keys: {list(coil.keys())}')
if 'turnsDescription' in coil:
    turns = coil['turnsDescription']
    print(f'Number of turns in turnsDescription: {len(turns)}')
    if len(turns) > 0:
        print(f'First turn keys: {list(turns[0].keys())}')
        if 'coordinates' in turns[0]:
            print(f'First turn coordinates: {turns[0]["coordinates"]}')
else:
    print('No turnsDescription in coil!')

# Check bobbin and functional description
if 'bobbin' in coil:
    print(f'\nBobbin present: {type(coil["bobbin"])}')
if 'functionalDescription' in coil:
    print(f'Functional description: {len(coil["functionalDescription"])} windings')

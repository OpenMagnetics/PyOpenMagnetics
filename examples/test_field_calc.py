#!/usr/bin/env python3
"""
Test script for magnetic field calculation (simpler than plotting).
"""

import sys
sys.path.insert(0, '/home/alf/OpenMagnetics/PyMKF/build/cp312-cp312-linux_x86_64')

import PyOpenMagnetics as pom
import time

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

# Wind the coil properly to get turn coordinates
coil = pom.wind(coil_spec, 1, [1.0], [0], [[0.001, 0.001]])
print(f'Coil wound with {len(coil.get("turnsDescription", []))} turns')

magnetic = {'core': core_data, 'coil': coil}

# Create proper inputs and process them
inputs = {
    'designRequirements': {
        'magnetizingInductance': {'nominal': 100e-6},
        'turnsRatios': []
    },
    'operatingPoints': [{
        'name': 'Test',
        'conditions': {'ambientTemperature': 25},
        'excitationsPerWinding': [{
            'frequency': 100000,
            'current': {
                'waveform': {'data': [-5, 5, -5], 'time': [0, 2.5e-6, 10e-6]}
            }
        }]
    }]
}

print('Processing inputs...')
processed_inputs = pom.process_inputs(inputs)
operating_point = processed_inputs['operatingPoints'][0]
print(f'Operating point processed. Current has harmonics: {"harmonics" in operating_point["excitationsPerWinding"][0]["current"]}')

print('\nCalling calculate_magnetic_field_strength_field...')
start = time.time()
try:
    result = pom.calculate_magnetic_field_strength_field(operating_point, magnetic)
    elapsed = time.time() - start
    print(f'Field calculation took {elapsed:.2f}s')
    if 'data' in result and isinstance(result['data'], str) and 'Exception' in result['data']:
        print(f'Error: {result["data"]}')
    else:
        print(f'Success! Result keys: {list(result.keys()) if isinstance(result, dict) else type(result)}')
except Exception as e:
    print(f'Exception: {e}')

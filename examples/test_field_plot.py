#!/usr/bin/env python3
"""
Test script for PyOpenMagnetics field plotting functions.
These tests are separate because they can be slow.
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
coil = pom.wind_by_turns(coil_spec)
magnetic = {'core': core_data, 'coil': coil}
operating_point = {
    'name': 'Test',
    'conditions': {'ambientTemperature': 25},
    'excitationsPerWinding': [{
        'name': 'Primary', 
        'frequency': 100000,
        'current': {'waveform': {'data': [1.0, -1.0, 1.0], 'time': [0, 5e-6, 10e-6]}}
    }]
}
print('Data ready.')

print('\nCalling plot_field_2d...')
start = time.time()
result = pom.plot_field_2d(magnetic, operating_point, 0, False, 1.0)
elapsed = time.time() - start
print(f'Field 2D took {elapsed:.2f}s, success: {result.get("success")}')
if result.get('success'):
    print(f'SVG length: {len(result.get("svg", ""))} chars')
else:
    print(f'Error: {result.get("error")}')

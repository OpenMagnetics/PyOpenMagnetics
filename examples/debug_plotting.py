#!/usr/bin/env python3
"""
Debug script for PyOpenMagnetics plotting functions.
"""
import sys
sys.path.insert(0, '/home/alf/OpenMagnetics/PyMKF/build/cp312-cp312-linux_x86_64')

import PyOpenMagnetics as pom
import os

print("Module dir:", dir(pom))
print()
print("plot_wire available:", hasattr(pom, 'plot_wire'))

if hasattr(pom, 'plot_wire'):
    wire = pom.find_wire_by_name('Round 1.00 - Grade 1')
    result = pom.plot_wire(wire, False)
    print('SVG length from result:', len(result.get('svg', '')))

    # Check if temp file was created
    temp_path = '/tmp/pyom_plot_wire.svg'
    if os.path.exists(temp_path):
        with open(temp_path) as f:
            content = f.read()
            print('Temp file length:', len(content))
            print('Temp file first 500 chars:')
            print(repr(content[:500]))
    else:
        print('Temp file does not exist')

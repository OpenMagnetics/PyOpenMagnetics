#!/usr/bin/env python3
"""
Debug script for core plotting.
"""
import sys
sys.path.insert(0, '/home/alf/OpenMagnetics/PyMKF/build/cp312-cp312-linux_x86_64')
import PyOpenMagnetics as pom
import json

print("Testing plot_core...")
print()

# First, get a processed core using calculate_core_data
core_input = {
    "functionalDescription": {
        "type": "two-piece set", 
        "material": "3C95", 
        "shape": "E 42/21/15", 
        "gapping": [{"type": "subtractive", "length": 0.001}], 
        "numberStacks": 1
    }
}
core_data = pom.calculate_core_data(core_input, True)
print("Core data has processedDescription:", 'processedDescription' in core_data)

# Build a magnetic with the processed core
magnetic = {
    "core": core_data, 
    "coil": {
        "bobbin": "Dummy", 
        "functionalDescription": []
    }
}

print()
print("Calling plot_core...")
result = pom.plot_core(magnetic)
print("Result success:", result.get('success'))
if result.get('success'):
    svg = result.get('svg', '')
    print("SVG length:", len(svg))
    print("SVG starts with:", repr(svg[:100]))
    
    # Save to file
    with open('/tmp/debug_core_plot.svg', 'w') as f:
        f.write(svg)
    print("Saved to /tmp/debug_core_plot.svg")
else:
    print("Error:", result.get('error', 'Unknown error'))

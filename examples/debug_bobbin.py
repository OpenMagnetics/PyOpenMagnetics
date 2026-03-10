#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/alf/OpenMagnetics/PyMKF/build/cp312-cp312-linux_x86_64')
import PyOpenMagnetics as pom

# Search for Round Grade 1 wires
print("Searching for Round Grade 1 wires:")
matches = [w for w in pom.get_wire_names() if 'Grade 1' in w and 'Round' in w]
print(f"Found {len(matches)} matches:")
for w in matches[:10]:
    print(f"  {w}")

# Try create_basic_bobbin
print()
print("Testing create_basic_bobbin...")
core_input = {
    "functionalDescription": {
        "type": "two-piece set", 
        "material": "3C95", 
        "shape": "E 42/21/15", 
        "gapping": [], 
        "numberStacks": 1
    }
}
core_data = pom.calculate_core_data(core_input, True)
print("Core data keys:", core_data.keys())

bobbin = pom.create_basic_bobbin(core_data, True)
print("Bobbin type:", type(bobbin))
if isinstance(bobbin, dict):
    print("Bobbin keys:", bobbin.keys())
else:
    print("Bobbin:", bobbin)

# Now test plot_bobbin
print()
print("Testing plot_bobbin...")
magnetic = {
    "core": core_data, 
    "coil": {
        "bobbin": bobbin, 
        "functionalDescription": []
    }
}

result = pom.plot_bobbin(magnetic)
print("Result:", result)

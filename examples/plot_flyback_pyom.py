#!/usr/bin/env python3
"""
Flyback Transformer Design Visualization using PyOpenMagnetics
===============================================================
Uses the native SVG plotting functions from PyOpenMagnetics.
"""

import json
import PyOpenMagnetics

def create_flyback_magnetic():
    """Create the flyback transformer magnetic structure for plotting."""
    
    # Core specification: E 25/13/7 with 3C95 material and gap
    core = {
        "functionalDescription": {
            "type": "two-piece set",
            "material": "3C95",
            "shape": "E 25/13/7",
            "gapping": [
                {
                    "type": "subtractive",
                    "length": 0.00013  # 0.13mm gap
                }
            ],
            "numberStacks": 1
        }
    }
    
    # Coil/winding specification
    coil = {
        "functionalDescription": [
            {
                "name": "Primary",
                "numberTurns": 45,
                "numberParallels": 1,
                "isolationSide": "primary",
                "wire": "Round 0.35 - Grade 1"
            },
            {
                "name": "Secondary", 
                "numberTurns": 4,
                "numberParallels": 2,
                "isolationSide": "secondary",
                "wire": "Round 0.6 - Grade 1"
            }
        ]
    }
    
    # Operating point for field visualization
    operating_point = {
        "conditions": {
            "ambientTemperature": 25
        },
        "excitationsPerWinding": [
            {
                "name": "Primary",
                "frequency": 100000,
                "current": {
                    "waveform": {
                        "data": [0, 0.59, 0, 0],
                        "time": [0, 4.5e-6, 4.5e-6, 10e-6]
                    }
                },
                "voltage": {
                    "waveform": {
                        "data": [222, 222, -148, -148],
                        "time": [0, 4.5e-6, 4.5e-6, 10e-6]
                    }
                }
            },
            {
                "name": "Secondary",
                "frequency": 100000,
                "current": {
                    "waveform": {
                        "data": [0, 0, 7.3, 0],
                        "time": [0, 4.5e-6, 4.5e-6, 10e-6]
                    }
                },
                "voltage": {
                    "waveform": {
                        "data": [0, 0, 12, 12],
                        "time": [0, 4.5e-6, 4.5e-6, 10e-6]
                    }
                }
            }
        ]
    }
    
    magnetic = {
        "core": core,
        "coil": coil
    }
    
    return magnetic, operating_point


def save_svg(svg_content, filename):
    """Save SVG content to file."""
    # Handle dict response with 'data' key
    if isinstance(svg_content, dict):
        if 'data' in svg_content:
            svg_content = svg_content['data']
        elif 'svg' in svg_content:
            svg_content = svg_content['svg']
        else:
            svg_content = json.dumps(svg_content, indent=2)
    
    with open(filename, 'w') as f:
        f.write(svg_content if isinstance(svg_content, str) else str(svg_content))
    print(f"  Saved: {filename}")


def main():
    print("=" * 60)
    print(" FLYBACK TRANSFORMER VISUALIZATION (PyOpenMagnetics)")
    print(" 220V AC → 12V @ 1A (12W)")
    print("=" * 60)
    print()
    
    magnetic, operating_point = create_flyback_magnetic()
    output_dir = "/home/alf/OpenMagnetics/PyMKF/examples"
    
    # Process the core to get full data
    print("Processing core data...")
    try:
        core_processed = PyOpenMagnetics.calculate_core_data(
            json.dumps(magnetic["core"]), 
            True
        )
        print(f"  Core processed successfully")
        
        # Debug: check what we got
        if isinstance(core_processed, dict):
            print(f"  Core keys: {list(core_processed.keys())[:5]}...")
    except Exception as e:
        print(f"  Error processing core: {e}")
        core_processed = magnetic["core"]
    
    # 1. Plot Core (3D SVG)
    print("\n[1/5] Generating core 3D view...")
    try:
        svg_core = PyOpenMagnetics.plot_core(json.dumps(core_processed), True)
        save_svg(svg_core, f"{output_dir}/flyback_core_3d.svg")
    except Exception as e:
        print(f"  Error: {e}")
    
    # 2. Plot Core 2D cross-section
    print("\n[2/5] Generating core 2D cross-section...")
    try:
        svg_core_2d = PyOpenMagnetics.plot_core_2d(json.dumps(core_processed), 1, None, True)
        save_svg(svg_core_2d, f"{output_dir}/flyback_core_2d.svg")
    except Exception as e:
        print(f"  Error: {e}")
    
    # 3. Process and plot coil
    print("\n[3/5] Generating coil 2D view...")
    try:
        # Wind the coil first
        inputs = {
            "designRequirements": {
                "magnetizingInductance": {"nominal": 800e-6},
                "turnsRatios": [{"nominal": 12.37}]
            },
            "operatingPoints": [operating_point]
        }
        
        wound_result = PyOpenMagnetics.wind_coil_based_on_number_turns_and_layers(
            json.dumps(magnetic["coil"]),
            json.dumps(core_processed),
            1  # 1 layer
        )
        
        if isinstance(wound_result, dict) and 'data' in wound_result:
            wound_coil = json.loads(wound_result['data']) if isinstance(wound_result['data'], str) else wound_result['data']
        else:
            wound_coil = wound_result
            
        svg_coil = PyOpenMagnetics.plot_coil_2d(json.dumps(wound_coil), 1, True, True)
        save_svg(svg_coil, f"{output_dir}/flyback_coil_2d.svg")
    except Exception as e:
        print(f"  Error: {e}")
    
    # 4. Plot wire cross-section
    print("\n[4/5] Generating wire cross-section...")
    try:
        # Get wire data
        wire = PyOpenMagnetics.find_wire_by_name("Round 0.35 - Grade 1")
        if isinstance(wire, dict) and 'data' in wire:
            wire_data = wire['data']
        else:
            wire_data = wire
        
        svg_wire = PyOpenMagnetics.plot_wire(json.dumps(wire_data) if isinstance(wire_data, dict) else wire_data, True)
        save_svg(svg_wire, f"{output_dir}/flyback_wire.svg")
    except Exception as e:
        print(f"  Error: {e}")
    
    # 5. Try to create a complete magnetic and plot field
    print("\n[5/5] Attempting field visualization...")
    try:
        # Create full magnetic structure
        full_magnetic = {
            "core": core_processed if isinstance(core_processed, dict) else magnetic["core"],
            "coil": wound_coil if 'wound_coil' in dir() else magnetic["coil"]
        }
        
        svg_field = PyOpenMagnetics.plot_field_2d(
            json.dumps(full_magnetic),
            json.dumps(operating_point),
            1,
            True
        )
        save_svg(svg_field, f"{output_dir}/flyback_field_2d.svg")
    except Exception as e:
        print(f"  Error (field plot requires complete winding): {e}")
    
    print()
    print("=" * 60)
    print("VISUALIZATION COMPLETE")
    print("=" * 60)
    print("\nSVG files can be opened in any web browser or vector editor.")
    print()
    
    # List generated files
    import os
    svg_files = [f for f in os.listdir(output_dir) if f.startswith('flyback_') and f.endswith('.svg')]
    if svg_files:
        print("Generated SVG files:")
        for f in sorted(svg_files):
            filepath = os.path.join(output_dir, f)
            size = os.path.getsize(filepath)
            print(f"  • {f} ({size:,} bytes)")


if __name__ == '__main__':
    main()

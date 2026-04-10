#!/usr/bin/env python3
"""
Test script for PyOpenMagnetics plotting functions.
Tests the 5 plotting methods: plot_core, plot_magnetic, plot_magnetic_field, plot_wire, plot_bobbin
"""

import sys
import os
import tempfile

# Add build directory to path (works from any directory)
_script_dir = os.path.dirname(os.path.abspath(__file__))
_project_dir = os.path.dirname(_script_dir)
_build_dir = os.path.join(_project_dir, 'build', 'cp312-cp312-linux_x86_64')
if os.path.exists(_build_dir):
    sys.path.insert(0, _build_dir)

import PyOpenMagnetics as pom

# Test output directory (use system temp)
_temp_dir = tempfile.gettempdir()

# Placeholder bobbin value (this is a valid API value meaning "no bobbin specified")
NO_BOBBIN = "Dummy"


def test_plot_wire():
    """Test wire plotting function."""
    print("\n=== Testing plot_wire (Round) ===")
    
    wire = pom.find_wire_by_name("Round 1.00 - Grade 1")
    print(f"Wire: {wire.get('name', 'Unknown')}")
    
    result = pom.plot_wire(wire)
    
    if result.get('success'):
        svg_content = result.get('svg', '')
        print(f"✓ Wire plot generated successfully!")
        print(f"  SVG length: {len(svg_content)} characters")
        print(f"  Contains SVG tag: {'<svg' in svg_content}")
        
        output_path = os.path.join(_temp_dir, 'test_wire_plot.svg')
        with open(output_path, 'w') as f:
            f.write(svg_content)
        print(f"  Saved to {output_path}")
    else:
        print(f"✗ Wire plot failed: {result.get('error', 'Unknown error')}")
    
    return result.get('success', False)


def test_plot_rectangular_wire():
    """Test plotting a rectangular wire."""
    print("\n=== Testing plot_wire (Rectangular) ===")
    
    wire = pom.find_wire_by_name("Rectangular 2.36x1.12 - Grade 1")
    print(f"Wire: {wire.get('name', 'Unknown')}")
    
    result = pom.plot_wire(wire)
    
    if result.get('success'):
        svg_content = result.get('svg', '')
        print(f"✓ Rectangular wire plot generated successfully!")
        print(f"  SVG length: {len(svg_content)} characters")
        
        output_path = os.path.join(_temp_dir, 'test_rect_wire_plot.svg')
        with open(output_path, 'w') as f:
            f.write(svg_content)
        print(f"  Saved to {output_path}")
    else:
        print(f"✗ Rectangular wire plot failed: {result.get('error', 'Unknown error')}")
    
    return result.get('success', False)


def test_plot_core():
    """Test core plotting function with a complete magnetic."""
    print("\n=== Testing plot_core ===")
    
    try:
        core_input = {
            "functionalDescription": {
                "type": "two-piece set", 
                "material": "3C95", 
                "shape": "E 55/28/21", 
                "gapping": [{"type": "subtractive", "length": 0.001}], 
                "numberStacks": 1
            }
        }
        core_data = pom.calculate_core_data(core_input, True)
        
        magnetic = {
            "core": core_data, 
            "coil": {
                "bobbin": NO_BOBBIN, 
                "functionalDescription": []
            }
        }
        
        result = pom.plot_core(magnetic)
        
        if result.get('success'):
            svg_content = result.get('svg', '')
            print(f"✓ Core plot generated successfully!")
            print(f"  SVG length: {len(svg_content)} characters")
            print(f"  Contains SVG tag: {'<svg' in svg_content}")
            
            output_path = os.path.join(_temp_dir, 'test_core_plot.svg')
            with open(output_path, 'w') as f:
                f.write(svg_content)
            print(f"  Saved to {output_path}")
        else:
            print(f"✗ Core plot failed: {result.get('error', 'Unknown error')}")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"✗ Exception in test_plot_core: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_plot_magnetic():
    """Test magnetic plotting with a complete wound magnetic."""
    print("\n=== Testing plot_magnetic ===")
    
    try:
        core_input = {
            "functionalDescription": {
                "type": "two-piece set", 
                "material": "3C95", 
                "shape": "E 42/21/15", 
                "gapping": [{"type": "subtractive", "length": 0.0005}], 
                "numberStacks": 1
            }
        }
        core_data = pom.calculate_core_data(core_input, True)
        
        bobbin = pom.create_basic_bobbin(core_data, True)
        wire = pom.find_wire_by_name("Round 0.5 - Grade 1")
        
        coil_spec = {
            "bobbin": bobbin,
            "functionalDescription": [
                {
                    "name": "Primary",
                    "numberTurns": 20,
                    "numberParallels": 1,
                    "isolationSide": "primary",
                    "wire": wire
                }
            ]
        }
        
        coil = pom.wind(coil_spec, 1, [1.0], [0], [[0.001, 0.001]])
        
        magnetic = {
            "core": core_data, 
            "coil": coil
        }
        
        result = pom.plot_magnetic(magnetic)
        
        if result.get('success'):
            svg_content = result.get('svg', '')
            print(f"✓ Magnetic plot generated successfully!")
            print(f"  SVG length: {len(svg_content)} characters")
            print(f"  Contains SVG tag: {'<svg' in svg_content}")
            
            output_path = os.path.join(_temp_dir, 'test_magnetic_plot.svg')
            with open(output_path, 'w') as f:
                f.write(svg_content)
            print(f"  Saved to {output_path}")
        else:
            print(f"✗ Magnetic plot failed: {result.get('error', 'Unknown error')}")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"✗ Exception in test_plot_magnetic: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_plot_bobbin():
    """Test bobbin plotting function."""
    print("\n=== Testing plot_bobbin ===")
    
    try:
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
        
        bobbin = pom.create_basic_bobbin(core_data, True)
        
        magnetic = {
            "core": core_data, 
            "coil": {
                "bobbin": bobbin, 
                "functionalDescription": []
            }
        }
        
        result = pom.plot_bobbin(magnetic)
        
        if result.get('success'):
            svg_content = result.get('svg', '')
            print(f"✓ Bobbin plot generated successfully!")
            print(f"  SVG length: {len(svg_content)} characters")
            print(f"  Contains SVG tag: {'<svg' in svg_content}")
            
            output_path = os.path.join(_temp_dir, 'test_bobbin_plot.svg')
            with open(output_path, 'w') as f:
                f.write(svg_content)
            print(f"  Saved to {output_path}")
        else:
            print(f"✗ Bobbin plot failed: {result.get('error', 'Unknown error')}")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"✗ Exception in test_plot_bobbin: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_plot_magnetic_field():
    """Test magnetic field plotting function with 2 windings."""
    print("\n=== Testing plot_magnetic_field ===")
    
    try:
        core_input = {
            "functionalDescription": {
                "type": "two-piece set", 
                "material": "3C95", 
                "shape": "E 42/21/15", 
                "gapping": [{"type": "subtractive", "length": 0.0005}], 
                "numberStacks": 1
            }
        }
        core_data = pom.calculate_core_data(core_input, True)
        
        bobbin = pom.create_basic_bobbin(core_data, True)
        primary_wire = pom.find_wire_by_name("Round 0.5 - Grade 1")
        secondary_wire = pom.find_wire_by_name("Round 1.25 - Grade 1")
        
        # 2 windings with ~50% fill factor
        coil_spec = {
            "bobbin": bobbin,
            "functionalDescription": [
                {
                    "name": "Primary",
                    "numberTurns": 25,
                    "numberParallels": 1,
                    "isolationSide": "primary",
                    "wire": primary_wire
                },
                {
                    "name": "Secondary",
                    "numberTurns": 15,
                    "numberParallels": 1,
                    "isolationSide": "secondary",
                    "wire": secondary_wire
                }
            ]
        }
        
        coil = pom.wind(coil_spec, 2, [0.5, 0.5], [0, 1], [[0.0005, 0.0005], [0.0005, 0.0005]])
        
        magnetic = {
            "core": core_data, 
            "coil": coil
        }
        
        inputs = {
            "designRequirements": {
                "magnetizingInductance": {"nominal": 100e-6},
                "turnsRatios": [{"nominal": 1.67}]
            },
            "operatingPoints": [{
                "name": "Operating Point 1",
                "conditions": {
                    "ambientTemperature": 25
                },
                "excitationsPerWinding": [
                    {
                        "name": "Primary",
                        "frequency": 100000,
                        "current": {
                            "waveform": {
                                "data": [2.0, -2.0, 2.0],
                                "time": [0, 5e-6, 10e-6]
                            }
                        }
                    },
                    {
                        "name": "Secondary",
                        "frequency": 100000,
                        "current": {
                            "waveform": {
                                "data": [-1.2, 1.2, -1.2],
                                "time": [0, 5e-6, 10e-6]
                            }
                        }
                    }
                ]
            }]
        }
        processed_inputs = pom.process_inputs(inputs)
        operating_point = processed_inputs["operatingPoints"][0]
        
        result = pom.plot_magnetic_field(magnetic, operating_point)
        
        if result.get('success'):
            svg_content = result.get('svg', '')
            print(f"✓ Magnetic field plot generated successfully!")
            print(f"  SVG length: {len(svg_content)} characters")
            print(f"  Contains SVG tag: {'<svg' in svg_content}")
            
            output_path = os.path.join(_temp_dir, 'test_magnetic_field_plot.svg')
            with open(output_path, 'w') as f:
                f.write(svg_content)
            print(f"  Saved to {output_path}")
        else:
            print(f"✗ Magnetic field plot failed: {result.get('error', 'Unknown error')}")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"✗ Exception in test_plot_magnetic_field: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_plot_electric_field():
    """Test electric field plotting function with 2 windings."""
    print("\n=== Testing plot_electric_field ===")
    
    try:
        core_input = {
            "functionalDescription": {
                "type": "two-piece set", 
                "material": "3C95", 
                "shape": "E 42/21/15", 
                "gapping": [{"type": "subtractive", "length": 0.0005}], 
                "numberStacks": 1
            }
        }
        core_data = pom.calculate_core_data(core_input, True)
        
        bobbin = pom.create_basic_bobbin(core_data, True)
        primary_wire = pom.find_wire_by_name("Round 0.5 - Grade 1")
        secondary_wire = pom.find_wire_by_name("Round 1.25 - Grade 1")
        
        # 2 windings with ~50% fill factor
        coil_spec = {
            "bobbin": bobbin,
            "functionalDescription": [
                {
                    "name": "Primary",
                    "numberTurns": 25,
                    "numberParallels": 1,
                    "isolationSide": "primary",
                    "wire": primary_wire
                },
                {
                    "name": "Secondary",
                    "numberTurns": 15,
                    "numberParallels": 1,
                    "isolationSide": "secondary",
                    "wire": secondary_wire
                }
            ]
        }
        
        coil = pom.wind(coil_spec, 2, [0.5, 0.5], [0, 1], [[0.0005, 0.0005], [0.0005, 0.0005]])
        
        magnetic = {
            "core": core_data, 
            "coil": coil
        }
        
        inputs = {
            "designRequirements": {
                "magnetizingInductance": {"nominal": 100e-6},
                "turnsRatios": [{"nominal": 1.67}]
            },
            "operatingPoints": [{
                "name": "Operating Point 1",
                "conditions": {
                    "ambientTemperature": 25
                },
                "excitationsPerWinding": [
                    {
                        "name": "Primary",
                        "frequency": 100000,
                        "current": {
                            "waveform": {
                                "data": [2.0, -2.0, 2.0],
                                "time": [0, 5e-6, 10e-6]
                            }
                        },
                        "voltage": {
                            "waveform": {
                                "data": [100.0, -100.0, 100.0],
                                "time": [0, 5e-6, 10e-6]
                            }
                        }
                    },
                    {
                        "name": "Secondary",
                        "frequency": 100000,
                        "current": {
                            "waveform": {
                                "data": [-1.2, 1.2, -1.2],
                                "time": [0, 5e-6, 10e-6]
                            }
                        },
                        "voltage": {
                            "waveform": {
                                "data": [167.0, -167.0, 167.0],
                                "time": [0, 5e-6, 10e-6]
                            }
                        }
                    }
                ]
            }]
        }
        processed_inputs = pom.process_inputs(inputs)
        operating_point = processed_inputs["operatingPoints"][0]
        
        result = pom.plot_electric_field(magnetic, operating_point)
        
        if result.get('success'):
            svg_content = result.get('svg', '')
            print(f"✓ Electric field plot generated successfully!")
            print(f"  SVG length: {len(svg_content)} characters")
            print(f"  Contains SVG tag: {'<svg' in svg_content}")
            
            output_path = os.path.join(_temp_dir, 'test_electric_field_plot.svg')
            with open(output_path, 'w') as f:
                f.write(svg_content)
            print(f"  Saved to {output_path}")
        else:
            print(f"✗ Electric field plot failed: {result.get('error', 'Unknown error')}")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"✗ Exception in test_plot_electric_field: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all plotting tests and report results."""
    print("=" * 60)
    print("PyOpenMagnetics Plotting Tests")
    print("=" * 60)
    
    tests = [
        ("Wire (Round)", test_plot_wire),
        ("Wire (Rectangular)", test_plot_rectangular_wire),
        ("Core", test_plot_core),
        ("Magnetic", test_plot_magnetic),
        ("Bobbin", test_plot_bobbin),
        ("Magnetic Field", test_plot_magnetic_field),
        ("Electric Field", test_plot_electric_field),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Test '{name}' raised exception: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = 0
    failed = 0
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("-" * 60)
    print(f"Total: {passed} passed, {failed} failed out of {len(tests)} tests")
    
    return failed == 0


def generate_all_plots(output_dir=None):
    """Generate all plots and save to output directory."""
    if output_dir is None:
        output_dir = os.path.join(_project_dir, 'output', 'plots')
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\nGenerating all plots to {output_dir}...")
    
    # Wire plots
    wire = pom.find_wire_by_name("Round 1.00 - Grade 1")
    result = pom.plot_wire(wire)
    if result.get('success'):
        with open(os.path.join(output_dir, 'wire_round.svg'), 'w') as f:
            f.write(result['svg'])
        print("  ✓ wire_round.svg")
    
    wire = pom.find_wire_by_name("Rectangular 2.36x1.12 - Grade 1")
    result = pom.plot_wire(wire)
    if result.get('success'):
        with open(os.path.join(output_dir, 'wire_rectangular.svg'), 'w') as f:
            f.write(result['svg'])
        print("  ✓ wire_rectangular.svg")
    
    # Core plot
    core_input = {
        "functionalDescription": {
            "type": "two-piece set", 
            "material": "3C95", 
            "shape": "E 55/28/21", 
            "gapping": [{"type": "subtractive", "length": 0.001}], 
            "numberStacks": 1
        }
    }
    core_data = pom.calculate_core_data(core_input, True)
    magnetic = {"core": core_data, "coil": {"bobbin": NO_BOBBIN, "functionalDescription": []}}
    result = pom.plot_core(magnetic)
    if result.get('success'):
        with open(os.path.join(output_dir, 'core.svg'), 'w') as f:
            f.write(result['svg'])
        print("  ✓ core.svg")
    
    # Bobbin plot
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
    bobbin = pom.create_basic_bobbin(core_data, True)
    magnetic = {"core": core_data, "coil": {"bobbin": bobbin, "functionalDescription": []}}
    result = pom.plot_bobbin(magnetic)
    if result.get('success'):
        with open(os.path.join(output_dir, 'bobbin.svg'), 'w') as f:
            f.write(result['svg'])
        print("  ✓ bobbin.svg")
    
    # Magnetic plot (with coil)
    core_input = {
        "functionalDescription": {
            "type": "two-piece set", 
            "material": "3C95", 
            "shape": "E 42/21/15", 
            "gapping": [{"type": "subtractive", "length": 0.0005}], 
            "numberStacks": 1
        }
    }
    core_data = pom.calculate_core_data(core_input, True)
    bobbin = pom.create_basic_bobbin(core_data, True)
    wire = pom.find_wire_by_name("Round 0.5 - Grade 1")
    coil_spec = {
        "bobbin": bobbin,
        "functionalDescription": [{
            "name": "Primary",
            "numberTurns": 20,
            "numberParallels": 1,
            "isolationSide": "primary",
            "wire": wire
        }]
    }
    coil = pom.wind(coil_spec, 1, [1.0], [0], [[0.001, 0.001]])
    magnetic = {"core": core_data, "coil": coil}
    result = pom.plot_magnetic(magnetic)
    if result.get('success'):
        with open(os.path.join(output_dir, 'magnetic.svg'), 'w') as f:
            f.write(result['svg'])
        print("  ✓ magnetic.svg")
    
    # Create 2-winding magnetic for field plots (~50% fill factor)
    core_input = {
        "functionalDescription": {
            "type": "two-piece set", 
            "material": "3C95", 
            "shape": "E 42/21/15", 
            "gapping": [{"type": "subtractive", "length": 0.0005}], 
            "numberStacks": 1
        }
    }
    core_data = pom.calculate_core_data(core_input, True)
    bobbin = pom.create_basic_bobbin(core_data, True)
    primary_wire = pom.find_wire_by_name("Round 0.5 - Grade 1")
    secondary_wire = pom.find_wire_by_name("Round 1.25 - Grade 1")
    coil_spec = {
        "bobbin": bobbin,
        "functionalDescription": [
            {
                "name": "Primary",
                "numberTurns": 25,
                "numberParallels": 1,
                "isolationSide": "primary",
                "wire": primary_wire
            },
            {
                "name": "Secondary",
                "numberTurns": 15,
                "numberParallels": 1,
                "isolationSide": "secondary",
                "wire": secondary_wire
            }
        ]
    }
    coil = pom.wind(coil_spec, 2, [0.5, 0.5], [0, 1], [[0.0005, 0.0005], [0.0005, 0.0005]])
    magnetic_2w = {"core": core_data, "coil": coil}
    
    # Magnetic field plot (current only)
    inputs_mag = {
        "designRequirements": {"magnetizingInductance": {"nominal": 100e-6}, "turnsRatios": [{"nominal": 1.67}]},
        "operatingPoints": [{
            "name": "Operating Point 1",
            "conditions": {"ambientTemperature": 25},
            "excitationsPerWinding": [
                {
                    "name": "Primary",
                    "frequency": 100000,
                    "current": {"waveform": {"data": [2.0, -2.0, 2.0], "time": [0, 5e-6, 10e-6]}}
                },
                {
                    "name": "Secondary",
                    "frequency": 100000,
                    "current": {"waveform": {"data": [-1.2, 1.2, -1.2], "time": [0, 5e-6, 10e-6]}}
                }
            ]
        }]
    }
    processed_inputs = pom.process_inputs(inputs_mag)
    operating_point = processed_inputs["operatingPoints"][0]
    result = pom.plot_magnetic_field(magnetic_2w, operating_point)
    if result.get('success'):
        with open(os.path.join(output_dir, 'magnetic_field.svg'), 'w') as f:
            f.write(result['svg'])
        print("  ✓ magnetic_field.svg")
    
    # Electric field plot (requires voltage)
    inputs_elec = {
        "designRequirements": {"magnetizingInductance": {"nominal": 100e-6}, "turnsRatios": [{"nominal": 1.67}]},
        "operatingPoints": [{
            "name": "Operating Point 1",
            "conditions": {"ambientTemperature": 25},
            "excitationsPerWinding": [
                {
                    "name": "Primary",
                    "frequency": 100000,
                    "current": {"waveform": {"data": [2.0, -2.0, 2.0], "time": [0, 5e-6, 10e-6]}},
                    "voltage": {"waveform": {"data": [100.0, -100.0, 100.0], "time": [0, 5e-6, 10e-6]}}
                },
                {
                    "name": "Secondary",
                    "frequency": 100000,
                    "current": {"waveform": {"data": [-1.2, 1.2, -1.2], "time": [0, 5e-6, 10e-6]}},
                    "voltage": {"waveform": {"data": [167.0, -167.0, 167.0], "time": [0, 5e-6, 10e-6]}}
                }
            ]
        }]
    }
    processed_inputs = pom.process_inputs(inputs_elec)
    operating_point = processed_inputs["operatingPoints"][0]
    result = pom.plot_electric_field(magnetic_2w, operating_point)
    if result.get('success'):
        with open(os.path.join(output_dir, 'electric_field.svg'), 'w') as f:
            f.write(result['svg'])
        print("  ✓ electric_field.svg")
    
    print(f"\nAll plots saved to {output_dir}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--generate":
        generate_all_plots()
    else:
        success = run_all_tests()
        sys.exit(0 if success else 1)

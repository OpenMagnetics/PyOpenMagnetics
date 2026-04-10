#!/usr/bin/env python3
"""
PyOpenMagnetics - Converter-Based Magnetic Design Example

This example demonstrates the most powerful PyOpenMagnetics feature:
design_magnetics_from_converter() - which goes directly from converter 
specifications to complete magnetic designs.

Usage:
    python converter_design_example.py
"""

import PyOpenMagnetics
import json


def design_flyback_with_converter_method():
    """
    Design a flyback transformer using the converter-based method.
    This is the recommended approach for most converter designs.
    """
    print("=" * 70)
    print("FLYBACK DESIGN USING design_magnetics_from_converter()")
    print("220V AC → 12V @ 2A (24W)")
    print("=" * 70)
    
    # Define flyback converter specifications
    flyback_specs = {
        "inputVoltage": {
            "minimum": 185,    # V AC minimum (low line)
            "maximum": 265     # V AC maximum (high line)
        },
        "desiredInductance": 800e-6,     # 800 µH magnetizing inductance
        "desiredTurnsRatios": [13.5],    # Np/Ns for 12V output
        "maximumDutyCycle": 0.45,
        "efficiency": 0.88,
        "diodeVoltageDrop": 0.5,
        "operatingPoints": [{
            "outputVoltages": [12.0],    # 12V output
            "outputCurrents": [2.0],     # 2A output
            "switchingFrequency": 100000, # 100 kHz
            "ambientTemperature": 40
        }]
    }
    
    print("\n[1] Converter Specifications:")
    print(f"    Input: 185-265V AC")
    print(f"    Output: 12V @ 2A (24W)")
    print(f"    Switching Frequency: 100 kHz")
    print(f"    Target Inductance: 800 µH")
    print(f"    Turns Ratio: 13.5:1")
    
    # Design magnetics directly from converter specs
    print("\n[2] Running design_magnetics_from_converter()...")
    print("    (This may take 10-30 seconds...)")
    
    try:
        result = PyOpenMagnetics.design_magnetics_from_converter(
            topology="flyback",
            converter=flyback_specs,
            max_results=3,
            core_mode="STANDARD_CORES",
            use_ngspice=False,  # Use analytical for speed
            weights={
                "COST": 1.0,
                "EFFICIENCY": 2.0,  # Prioritize efficiency
                "DIMENSIONS": 0.5
            }
        )
        
        # Process results
        if isinstance(result, dict) and "data" in result:
            designs = result["data"]
            
            if isinstance(designs, str):
                # Error message
                print(f"\n✗ Error: {designs}")
                return None
            
            print(f"\n✓ Found {len(designs)} suitable designs\n")
            
            # Analyze top designs
            models = {
                "coreLosses": "IGSE",
                "reluctance": "ZHANG"
            }
            
            for i, design in enumerate(designs[:3]):
                mas = design.get("mas", design)
                score = design.get("scoring", 0)
                
                if "magnetic" not in mas:
                    print(f"Design #{i+1}: Invalid format")
                    continue
                
                magnetic = mas["magnetic"]
                core = magnetic["core"]
                
                # Get core info
                shape_desc = core["functionalDescription"]["shape"]
                shape_name = shape_desc["name"] if isinstance(shape_desc, dict) else shape_desc
                
                material_desc = core["functionalDescription"]["material"]
                material_name = material_desc["name"] if isinstance(material_desc, dict) else material_desc
                
                print("-" * 60)
                print(f"Design #{i+1}: {shape_name} / {material_name}")
                print(f"Score: {score:.3f}")
                
                # Get gap info
                gapping = core["functionalDescription"].get("gapping", [])
                if gapping:
                    gap_length = gapping[0].get("length", 0) * 1000
                    print(f"Air Gap: {gap_length:.2f} mm")
                
                # Get winding info
                if "coil" in magnetic and "functionalDescription" in magnetic["coil"]:
                    print("Windings:")
                    for winding in magnetic["coil"]["functionalDescription"]:
                        name = winding.get("name", "Winding")
                        turns = winding.get("numberTurns", "?")
                        n_parallels = winding.get("numberParallels", 1)
                        wire = winding.get("wire", "?")
                        if isinstance(wire, dict):
                            wire = wire.get("name", wire.get("type", "?"))
                        parallel_str = f" x {n_parallels}" if n_parallels > 1 else ""
                        print(f"  {name}: {turns} turns{parallel_str}, {wire}")
                
                # Calculate losses
                try:
                    losses = PyOpenMagnetics.calculate_core_losses(
                        core, magnetic["coil"], mas["inputs"], models
                    )
                    print(f"Core Losses: {losses.get('coreLosses', 0):.3f} W")
                    print(f"Peak Flux Density: {losses.get('magneticFluxDensityPeak', 0)*1000:.1f} mT")
                except Exception as e:
                    print(f"  (Could not calculate losses: {e})")
                
                print()
            
            return designs[0] if designs else None
            
        else:
            print("\n✗ No designs found or unexpected result format")
            print(f"Result: {result}")
            return None
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def design_buck_with_converter_method():
    """
    Design a buck converter inductor using the converter-based method.
    """
    print("\n" + "=" * 70)
    print("BUCK INDUCTOR DESIGN USING design_magnetics_from_converter()")
    print("12V → 3.3V @ 5A")
    print("=" * 70)
    
    buck_specs = {
        "inputVoltage": {
            "minimum": 10,
            "maximum": 14
        },
        "desiredInductance": 4.7e-6,  # 4.7 µH
        "currentRippleRatio": 0.3,
        "operatingPoints": [{
            "outputVoltages": [3.3],
            "outputCurrents": [5.0],
            "switchingFrequency": 500000,  # 500 kHz
            "ambientTemperature": 25
        }]
    }
    
    print("\n[1] Converter Specifications:")
    print(f"    Input: 10-14V")
    print(f"    Output: 3.3V @ 5A")
    print(f"    Switching Frequency: 500 kHz")
    print(f"    Target Inductance: 4.7 µH")
    
    print("\n[2] Running design_magnetics_from_converter()...")
    
    try:
        result = PyOpenMagnetics.design_magnetics_from_converter(
            topology="buck",
            converter=buck_specs,
            max_results=3,
            core_mode="STANDARD_CORES",
            use_ngspice=False,
            weights={
                "EFFICIENCY": 1.0,
                "DIMENSIONS": 1.0
            }
        )
        
        if isinstance(result, dict) and "data" in result:
            designs = result["data"]
            
            if isinstance(designs, list) and len(designs) > 0:
                print(f"\n✓ Found {len(designs)} suitable designs\n")
                
                for i, design in enumerate(designs[:2]):
                    mas = design.get("mas", design)
                    magnetic = mas.get("magnetic", mas)
                    
                    core = magnetic["core"]
                    shape = core["functionalDescription"]["shape"]
                    shape_name = shape["name"] if isinstance(shape, dict) else shape
                    
                    print(f"Design #{i+1}: {shape_name}")
                    
                    if "coil" in magnetic and "functionalDescription" in magnetic["coil"]:
                        winding = magnetic["coil"]["functionalDescription"][0]
                        print(f"  Turns: {winding.get('numberTurns', '?')}")
                        print(f"  Wire: {winding.get('wire', '?')}")
                    print()
            else:
                print("\n✗ No designs found")
        else:
            print("\n✗ Unexpected result")
            
    except Exception as e:
        print(f"\n✗ Error: {e}")


def compare_topology_processors():
    """
    Compare different ways to process converter specifications.
    """
    print("\n" + "=" * 70)
    print("COMPARING TOPOLOGY PROCESSORS")
    print("=" * 70)
    
    flyback_specs = {
        "inputVoltage": {"minimum": 185, "maximum": 265},
        "desiredInductance": 1e-3,
        "desiredTurnsRatios": [10.0],
        "operatingPoints": [{
            "outputVoltages": [12.0],
            "outputCurrents": [1.0],
            "switchingFrequency": 100000,
            "ambientTemperature": 25
        }]
    }
    
    print("\n[1] Using process_converter() - Generic method:")
    try:
        result = PyOpenMagnetics.process_converter("flyback", flyback_specs, use_ngspice=False)
        if "error" not in result:
            print("    ✓ Successfully processed flyback specs")
            print(f"    Has designRequirements: {'designRequirements' in result}")
            print(f"    Has operatingPoints: {'operatingPoints' in result}")
        else:
            print(f"    ✗ Error: {result['error']}")
    except Exception as e:
        print(f"    ✗ Exception: {e}")
    
    print("\n[2] Using process_flyback() - Specific method:")
    try:
        result = PyOpenMagnetics.process_flyback(flyback_specs)
        if isinstance(result, dict):
            if "error" not in result:
                print("    ✓ Successfully processed with process_flyback()")
                print(f"    Has designRequirements: {'designRequirements' in result}")
            else:
                print(f"    ✗ Error: {result['error']}")
        else:
            print(f"    ✗ Unexpected result type: {type(result)}")
    except Exception as e:
        print(f"    ✗ Exception: {e}")
    
    print("\n[3] Using design_magnetics_from_converter() - Complete pipeline:")
    try:
        result = PyOpenMagnetics.design_magnetics_from_converter(
            "flyback", flyback_specs, max_results=1, use_ngspice=False
        )
        if isinstance(result, dict) and "data" in result:
            designs = result["data"]
            if isinstance(designs, list):
                print(f"    ✓ Successfully designed {len(designs)} magnetics")
            else:
                print(f"    ✗ Unexpected data format: {type(designs)}")
        else:
            print(f"    ✗ Unexpected result format")
    except Exception as e:
        print(f"    ✗ Exception: {e}")


def main():
    """Main execution function."""
    print("\n" + "=" * 70)
    print(" PYOPENMAGNETICS - CONVERTER-BASED DESIGN EXAMPLES")
    print(" Using converter.h methods from PyMKF")
    print("=" * 70)
    
    # Example 1: Flyback design
    best_flyback = design_flyback_with_converter_method()
    
    # Example 2: Buck design
    design_buck_with_converter_method()
    
    # Example 3: Compare methods
    compare_topology_processors()
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("""
The design_magnetics_from_converter() function is the most powerful
PyOpenMagnetics feature for converter design. It:

1. Takes converter specifications (input/output voltage, current, etc.)
2. Automatically calculates required magnetic parameters
3. Runs the magnetic adviser to find optimal designs
4. Returns ranked/scored magnetic designs ready to build

Key benefits:
- Single function call from specs to designs
- No manual inductance/turns calculations needed
- Automatic waveform generation
- Multiple design options with scoring
- Supports all major converter topologies

For more examples, see:
- AGENTS.md (Converter-Based Design section)
- tests/test_converter_endpoints.py
- llms.txt
""")


if __name__ == "__main__":
    main()

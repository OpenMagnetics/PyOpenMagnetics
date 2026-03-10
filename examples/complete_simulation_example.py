#!/usr/bin/env python3
"""
PyOpenMagnetics - Complete Design, Simulation, and Visualization Example

This example demonstrates:
1. Manual magnetic component design (without adviser)
2. Core and winding loss calculations
3. Inductance verification
4. SVG visualization of all components
5. Magnetic and electric field plotting

Usage:
    python complete_simulation_example.py
"""

import PyOpenMagnetics
import json
import os


def create_manual_design():
    """
    Create a manual transformer design for a flyback converter.
    This bypasses the adviser and creates the design directly.
    """
    print("=" * 70)
    print("CREATING MANUAL TRANSFORMER DESIGN")
    print("=" * 70)
    
    # Design specifications
    specs = {
        "L_m": 1000e-6,  # 1 mH magnetizing inductance
        "turns_ratio": 10.0,  # 10:1
        "f_sw": 100000,  # 100 kHz
        "V_in": 200,  # Input voltage
        "I_pri": 0.5,  # Primary current
    }
    
    # Step 1: Select core
    print("\n[1] Selecting core...")
    shape = PyOpenMagnetics.find_core_shape_by_name("E 42/21/15")
    material = PyOpenMagnetics.find_core_material_by_name("3C95")
    print(f"    Core: E 42/21/15 with 3C95 material")
    
    # Step 2: Calculate turns and gap
    print("\n[2] Calculating turns and gap...")
    N_pri = 40  # Primary turns
    N_sec = int(N_pri / specs["turns_ratio"])  # Secondary turns
    
    # Calculate gap for target inductance
    # L = N^2 * AL, and AL ≈ μ0 * Ae / gap
    Ae = 181e-6  # m² (E 42/21/15 effective area)
    mu_0 = 4 * 3.14159 * 1e-7
    AL_target = specs["L_m"] / (N_pri ** 2)
    gap_length = mu_0 * Ae / AL_target
    
    print(f"    Primary turns: {N_pri}")
    print(f"    Secondary turns: {N_sec}")
    print(f"    Air gap: {gap_length*1000:.3f} mm")
    
    # Step 3: Create core specification
    core_data = {
        "functionalDescription": {
            "type": "two-piece set",
            "shape": shape,
            "material": material,
            "gapping": [{"type": "subtractive", "length": gap_length}],
            "numberStacks": 1
        }
    }
    
    # Calculate complete core data
    core = PyOpenMagnetics.calculate_core_data(core_data, False)
    
    # Get effective parameters
    if "processedDescription" in core:
        eff_params = core["processedDescription"].get("effectiveParameters", {})
        Ae_actual = eff_params.get("effectiveArea", Ae)
        le = eff_params.get("effectiveLength", 0)
        print(f"    Effective area: {Ae_actual*1e6:.1f} mm²")
        print(f"    Effective length: {le*1000:.1f} mm")
    
    # Step 4: Select wires
    print("\n[3] Selecting wires...")
    try:
        primary_wire = PyOpenMagnetics.find_wire_by_name("Round 0.40 - Grade 1")
        secondary_wire = PyOpenMagnetics.find_wire_by_name("Round 0.80 - Grade 1")
        print(f"    Primary: Round 0.40mm")
        print(f"    Secondary: Round 0.80mm")
    except:
        # Fallback if wire names don't match
        primary_wire = {"type": "round", "name": "Round 0.40mm"}
        secondary_wire = {"type": "round", "name": "Round 0.80mm"}
    
    # Step 5: Create coil
    print("\n[4] Creating coil...")
    coil_data = {
        "functionalDescription": [
            {
                "name": "Primary",
                "numberTurns": N_pri,
                "numberParallels": 1,
                "wire": primary_wire,
                "isolationSide": "primary"
            },
            {
                "name": "Secondary",
                "numberTurns": N_sec,
                "numberParallels": 1,
                "wire": secondary_wire,
                "isolationSide": "secondary"
            }
        ]
    }
    
    # Create magnetic
    magnetic = {
        "core": core,
        "coil": coil_data
    }
    
    print("✓ Manual design created successfully")
    
    return magnetic, specs


def simulate_losses(magnetic, specs):
    """
    Calculate core and winding losses.
    
    Args:
        magnetic: Magnetic design dict
        specs: Design specifications
        
    Returns:
        dict: Simulation results
    """
    print("\n" + "=" * 70)
    print("SIMULATING LOSSES")
    print("=" * 70)
    
    # Create operating point
    operating_point = {
        "name": "Nominal",
        "conditions": {"ambientTemperature": 40},
        "excitationsPerWinding": [
            {
                "name": "Primary",
                "frequency": specs["f_sw"],
                "current": {
                    "processed": {
                        "label": "Triangular",
                        "dutyCycle": 0.45,
                        "offset": specs["I_pri"],
                        "peakToPeak": specs["I_pri"] * 0.4
                    }
                }
            }
        ]
    }
    
    # Create inputs for loss calculation
    inputs = {
        "designRequirements": {
            "magnetizingInductance": {"nominal": specs["L_m"]},
            "turnsRatios": [{"nominal": specs["turns_ratio"]}]
        },
        "operatingPoints": [operating_point]
    }
    
    # Process inputs
    processed_result = PyOpenMagnetics.process_inputs(inputs)
    if isinstance(processed_result, dict) and "data" in processed_result:
        processed_inputs = processed_result["data"]
    else:
        processed_inputs = processed_result
    
    # Calculate core losses
    print("\n[1] Calculating core losses...")
    models = {
        "coreLosses": "IGSE",
        "reluctance": "ZHANG",
        "coreTemperature": "MANIKTALA"
    }
    
    try:
        core_losses = PyOpenMagnetics.calculate_core_losses(
            magnetic["core"],
            magnetic["coil"],
            processed_inputs,
            models
        )
        
        print(f"    Core losses: {core_losses.get('coreLosses', 0):.3f} W")
        print(f"    Peak flux density: {core_losses.get('magneticFluxDensityPeak', 0)*1000:.1f} mT")
        print(f"    Temperature rise: {core_losses.get('maximumCoreTemperatureRise', 0):.1f} K")
    except Exception as e:
        print(f"    ✗ Core loss calculation failed: {e}")
        core_losses = {}
    
    # Calculate winding losses
    print("\n[2] Calculating winding losses...")
    try:
        winding_losses = PyOpenMagnetics.calculate_winding_losses(
            magnetic,
            operating_point,
            temperature=80
        )
        
        print(f"    Total winding losses: {winding_losses.get('windingLosses', 0):.3f} W")
        if "windingLossesPerWinding" in winding_losses:
            for i, loss in enumerate(winding_losses["windingLossesPerWinding"]):
                print(f"    Winding {i+1} losses: {loss:.3f} W")
    except Exception as e:
        print(f"    ✗ Winding loss calculation failed: {e}")
        winding_losses = {}
    
    # Calculate total losses
    total_core = core_losses.get("coreLosses", 0)
    total_winding = winding_losses.get("windingLosses", 0)
    total_losses = total_core + total_winding
    
    print(f"\n[3] Total losses: {total_losses:.3f} W")
    print(f"    Core: {total_core:.3f} W ({total_core/total_losses*100:.1f}%)")
    print(f"    Winding: {total_winding:.3f} W ({total_winding/total_losses*100:.1f}%)")
    
    return {
        "core_losses": core_losses,
        "winding_losses": winding_losses,
        "total_losses": total_losses
    }


def verify_inductance(magnetic, specs):
    """
    Verify the actual inductance of the design.
    
    Args:
        magnetic: Magnetic design dict
        specs: Design specifications
    """
    print("\n" + "=" * 70)
    print("VERIFYING INDUCTANCE")
    print("=" * 70)
    
    # Create a simple operating point for inductance calculation
    operating_point = {
        "name": "Inductance Check",
        "conditions": {"ambientTemperature": 25},
        "excitationsPerWinding": [
            {
                "name": "Primary",
                "frequency": specs["f_sw"],
                "current": {
                    "processed": {
                        "label": "DC",
                        "dutyCycle": 0.5,
                        "offset": 0.1,
                        "peakToPeak": 0.01
                    }
                }
            }
        ]
    }
    
    models = {"reluctance": "ZHANG"}
    
    try:
        L_actual = PyOpenMagnetics.calculate_inductance_from_number_turns_and_gapping(
            magnetic["core"],
            magnetic["coil"],
            operating_point,
            models
        )
        
        L_target = specs["L_m"]
        error = abs(L_actual - L_target) / L_target * 100
        
        print(f"\n    Target inductance: {L_target*1e6:.1f} µH")
        print(f"    Actual inductance: {L_actual*1e6:.1f} µH")
        print(f"    Error: {error:.1f}%")
        
        if error < 10:
            print("    ✓ Inductance within acceptable range")
        else:
            print("    ⚠ Inductance deviation is high - adjust gap")
            
    except Exception as e:
        print(f"    ✗ Inductance calculation failed: {e}")


def visualize_design(magnetic, output_dir="output"):
    """
    Generate comprehensive visualizations of the design.
    
    Args:
        magnetic: Magnetic design dict
        output_dir: Directory to save SVG files
    """
    print("\n" + "=" * 70)
    print("GENERATING VISUALIZATIONS")
    print("=" * 70)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Plot core
    print("\n[1] Plotting core...")
    try:
        result = PyOpenMagnetics.plot_core(magnetic["core"], use_colors=True)
        if result.get('success'):
            filename = os.path.join(output_dir, "01_core.svg")
            with open(filename, 'w') as f:
                f.write(result['svg'])
            print(f"    ✓ Saved: {filename}")
        else:
            print(f"    ✗ Failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"    ✗ Error: {e}")
    
    # 2. Plot wire (primary)
    print("\n[2] Plotting primary wire...")
    try:
        wire = magnetic["coil"]["functionalDescription"][0]["wire"]
        if isinstance(wire, dict):
            result = PyOpenMagnetics.plot_wire(wire)
            if result.get('success'):
                filename = os.path.join(output_dir, "02_wire_primary.svg")
                with open(filename, 'w') as f:
                    f.write(result['svg'])
                print(f"    ✓ Saved: {filename}")
    except Exception as e:
        print(f"    ✗ Error: {e}")
    
    # 3. Plot wire (secondary)
    print("\n[3] Plotting secondary wire...")
    try:
        wire = magnetic["coil"]["functionalDescription"][1]["wire"]
        if isinstance(wire, dict):
            result = PyOpenMagnetics.plot_wire(wire)
            if result.get('success'):
                filename = os.path.join(output_dir, "03_wire_secondary.svg")
                with open(filename, 'w') as f:
                    f.write(result['svg'])
                print(f"    ✓ Saved: {filename}")
    except Exception as e:
        print(f"    ✗ Error: {e}")
    
    # 4. Plot complete magnetic
    print("\n[4] Plotting complete magnetic...")
    try:
        result = PyOpenMagnetics.plot_magnetic(magnetic)
        if result.get('success'):
            filename = os.path.join(output_dir, "04_magnetic_complete.svg")
            with open(filename, 'w') as f:
                f.write(result['svg'])
            print(f"    ✓ Saved: {filename}")
        else:
            print(f"    ✗ Failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"    ✗ Error: {e}")
    
    # 5. Plot magnetic field (if we have operating point data)
    print("\n[5] Plotting magnetic field...")
    try:
        # Create operating point for field plot
        operating_point = {
            "name": "Field Plot",
            "conditions": {"ambientTemperature": 25},
            "excitationsPerWinding": [
                {
                    "name": "Primary",
                    "frequency": 100000,
                    "current": {
                        "processed": {
                            "label": "Triangular",
                            "dutyCycle": 0.45,
                            "offset": 0.5,
                            "peakToPeak": 0.2
                        }
                    }
                },
                {
                    "name": "Secondary",
                    "frequency": 100000,
                    "current": {
                        "processed": {
                            "label": "Triangular",
                            "dutyCycle": 0.45,
                            "offset": 5.0,
                            "peakToPeak": 2.0
                        }
                    }
                }
            ]
        }
        
        result = PyOpenMagnetics.plot_magnetic_field(magnetic, operating_point)
        if result.get('success'):
            filename = os.path.join(output_dir, "05_magnetic_field.svg")
            with open(filename, 'w') as f:
                f.write(result['svg'])
            print(f"    ✓ Saved: {filename}")
        else:
            print(f"    ✗ Failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"    ✗ Error: {e}")
    
    # 6. Plot electric field
    print("\n[6] Plotting electric field...")
    try:
        operating_point_with_voltage = {
            "name": "Electric Field Plot",
            "conditions": {"ambientTemperature": 25},
            "excitationsPerWinding": [
                {
                    "name": "Primary",
                    "frequency": 100000,
                    "current": {
                        "processed": {
                            "label": "Triangular",
                            "dutyCycle": 0.45,
                            "offset": 0.5,
                            "peakToPeak": 0.2
                        }
                    },
                    "voltage": {
                        "processed": {
                            "label": "Rectangular",
                            "dutyCycle": 0.45,
                            "offset": 100,
                            "peakToPeak": 200
                        }
                    }
                },
                {
                    "name": "Secondary",
                    "frequency": 100000,
                    "current": {
                        "processed": {
                            "label": "Triangular",
                            "dutyCycle": 0.45,
                            "offset": 5.0,
                            "peakToPeak": 2.0
                        }
                    },
                    "voltage": {
                        "processed": {
                            "label": "Rectangular",
                            "dutyCycle": 0.45,
                            "offset": 10,
                            "peakToPeak": 20
                        }
                    }
                }
            ]
        }
        
        result = PyOpenMagnetics.plot_electric_field(magnetic, operating_point_with_voltage)
        if result.get('success'):
            filename = os.path.join(output_dir, "06_electric_field.svg")
            with open(filename, 'w') as f:
                f.write(result['svg'])
            print(f"    ✓ Saved: {filename}")
        else:
            print(f"    ✗ Failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"    ✗ Error: {e}")
    
    print(f"\n✓ All visualizations saved to: {output_dir}/")


def export_spice_model(magnetic, output_dir="output"):
    """
    Export the magnetic component as a SPICE subcircuit.
    
    Args:
        magnetic: Magnetic design dict
        output_dir: Directory to save SPICE file
    """
    print("\n" + "=" * 70)
    print("EXPORTING SPICE MODEL")
    print("=" * 70)
    
    try:
        subcircuit = PyOpenMagnetics.export_magnetic_as_subcircuit(magnetic)
        
        filename = os.path.join(output_dir, "transformer.spice")
        with open(filename, 'w') as f:
            f.write(subcircuit)
        
        print(f"\n✓ SPICE subcircuit exported to: {filename}")
        print(f"  Subcircuit length: {len(subcircuit)} characters")
        
    except Exception as e:
        print(f"\n✗ SPICE export failed: {e}")


def main():
    """Main execution function."""
    print("\n" + "=" * 70)
    print(" PYOPENMAGNETICS - COMPLETE SIMULATION EXAMPLE")
    print(" Design, Simulate, Visualize, Export")
    print("=" * 70)
    
    # Step 1: Create design
    magnetic, specs = create_manual_design()
    
    # Step 2: Simulate losses
    results = simulate_losses(magnetic, specs)
    
    # Step 3: Verify inductance
    verify_inductance(magnetic, specs)
    
    # Step 4: Generate visualizations
    visualize_design(magnetic)
    
    # Step 5: Export SPICE model
    export_spice_model(magnetic)
    
    print("\n" + "=" * 70)
    print("✓ COMPLETE")
    print("=" * 70)
    print("\nGenerated files:")
    print("  - output/01_core.svg")
    print("  - output/02_wire_primary.svg")
    print("  - output/03_wire_secondary.svg")
    print("  - output/04_magnetic_complete.svg")
    print("  - output/05_magnetic_field.svg")
    print("  - output/06_electric_field.svg")
    print("  - output/transformer.spice")
    print("\nNext steps:")
    print("  1. Review SVG visualizations in output/ directory")
    print("  2. Import SPICE model into your simulator")
    print("  3. Build prototype and verify measurements")


if __name__ == "__main__":
    main()

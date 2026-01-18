"""
PyOpenMagnetics Examples - Flyback Transformer Design

This example demonstrates a complete flyback transformer design workflow:
1. Define converter specifications
2. Get design recommendations
3. Analyze losses and performance
4. Visualize the result

For more examples, see llms.txt in the PyOpenMagnetics directory.
"""

import PyOpenMagnetics


def design_flyback_transformer():
    """
    Design a flyback transformer for a 24V/3A output from universal AC input.
    
    Specifications:
    - Input: 85-265 VAC (rectified to ~120-375 VDC)
    - Output: 24V @ 3A (72W)
    - Switching frequency: 100 kHz
    - Efficiency target: 85%
    """
    
    # Step 1: Define the converter operating conditions
    print("=" * 60)
    print("FLYBACK TRANSFORMER DESIGN")
    print("Output: 24V @ 3A (72W)")
    print("=" * 60)
    
    # Define design requirements
    inputs = {
        "designRequirements": {
            "magnetizingInductance": {
                "nominal": 200e-6,    # 200 µH magnetizing inductance
                "minimum": 180e-6,
                "maximum": 220e-6
            },
            "turnsRatios": [
                {"nominal": 6.0}      # Npri/Nsec = 6:1
            ],
            "insulation": {
                "insulationType": "Functional",
                "pollutionDegree": "P2",
                "overvoltageCategory": "OVC-II"
            }
        },
        "operatingPoints": [
            {
                "name": "Low Line (85 VAC)",
                "conditions": {"ambientTemperature": 40},
                "excitationsPerWinding": [{
                    "name": "Primary",
                    "frequency": 100000,
                    # Typical flyback triangular current waveform
                    "current": {
                        "waveform": {
                            "data": [0.2, 1.8, 1.8, 0.2],
                            "time": [0, 4.5e-6, 4.5e-6, 10e-6]
                        }
                    },
                    # Square wave voltage during on-time
                    "voltage": {
                        "waveform": {
                            "data": [120, 120, 0, 0],
                            "time": [0, 4.5e-6, 4.5e-6, 10e-6]
                        }
                    }
                }]
            },
            {
                "name": "High Line (265 VAC)",
                "conditions": {"ambientTemperature": 40},
                "excitationsPerWinding": [{
                    "name": "Primary",
                    "frequency": 100000,
                    "current": {
                        "waveform": {
                            "data": [0.1, 0.6, 0.6, 0.1],
                            "time": [0, 2e-6, 2e-6, 10e-6]
                        }
                    },
                    "voltage": {
                        "waveform": {
                            "data": [375, 375, 0, 0],
                            "time": [0, 2e-6, 2e-6, 10e-6]
                        }
                    }
                }]
            }
        ]
    }
    
    # Step 2: Process inputs (adds harmonics for accurate loss calculation)
    print("\n[1] Processing inputs...")
    processed_inputs = PyOpenMagnetics.process_inputs(inputs)
    print("    ✓ Harmonics calculated")
    
    # Step 3: Get design recommendations
    print("\n[2] Getting design recommendations...")
    
    weights = {
        "EFFICIENCY": 1.0,    # Prioritize efficiency
        "DIMENSIONS": 0.5,    # Secondary: small size
        "COST": 0.3           # Tertiary: low cost
    }
    
    magnetics = PyOpenMagnetics.calculate_advised_magnetics(
        processed_inputs,
        max_results=3,
        core_mode="STANDARD_CORES"
    )
    
    print(f"    ✓ Found {len(magnetics)} suitable designs")
    
    # Step 4: Analyze top recommendations
    print("\n[3] Analyzing top designs:")
    print("-" * 60)
    
    models = {
        "coreLosses": "IGSE",
        "reluctance": "ZHANG",
        "coreTemperature": "MANIKTALA"
    }
    
    for i, mas in enumerate(magnetics):
        if "magnetic" not in mas:
            continue
            
        magnetic = mas["magnetic"]
        core = magnetic["core"]
        coil = magnetic["coil"]
        
        # Get core info
        shape_name = core["functionalDescription"]["shape"]["name"]
        material_name = core["functionalDescription"]["material"]["name"]
        
        # Calculate losses for worst-case (low line)
        losses = PyOpenMagnetics.calculate_core_losses(
            core, coil, processed_inputs, models
        )
        
        # Calculate winding losses
        winding_losses = PyOpenMagnetics.calculate_winding_losses(
            magnetic, 
            processed_inputs["operatingPoints"][0],  # Low line
            temperature=80  # Estimated operating temperature
        )
        
        core_loss = losses.get("coreLosses", 0)
        winding_loss = winding_losses.get("windingLosses", 0)
        total_loss = core_loss + winding_loss
        
        print(f"\nDesign #{i+1}: {shape_name} / {material_name}")
        print(f"  Core losses:    {core_loss:.3f} W")
        print(f"  Winding losses: {winding_loss:.3f} W")
        print(f"  Total losses:   {total_loss:.3f} W")
        print(f"  B_peak:         {losses.get('magneticFluxDensityPeak', 0)*1000:.1f} mT")
        
        # Get winding info
        if "functionalDescription" in coil:
            for winding in coil["functionalDescription"]:
                print(f"  {winding['name']}: {winding['numberTurns']} turns")
    
    print("\n" + "=" * 60)
    print("Design complete! Best design is #1")
    
    return magnetics[0] if magnetics else None


def explore_core_database():
    """Demonstrate database access functions."""
    
    print("\n" + "=" * 60)
    print("CORE DATABASE EXPLORATION")
    print("=" * 60)
    
    # Get available shape families
    families = PyOpenMagnetics.get_core_shape_families()
    print(f"\nShape families: {', '.join(families[:10])}...")
    
    # Get materials by manufacturer
    ferroxcube = PyOpenMagnetics.get_core_material_names_by_manufacturer("Ferroxcube")
    print(f"Ferroxcube materials: {', '.join(ferroxcube[:5])}...")
    
    tdk = PyOpenMagnetics.get_core_material_names_by_manufacturer("TDK")
    print(f"TDK materials: {', '.join(tdk[:5])}...")
    
    # Get material properties
    print("\n3C95 Properties at 25°C:")
    mu = PyOpenMagnetics.get_material_permeability("3C95", 25, 0, 100000)
    print(f"  Permeability (100 kHz): {mu:.0f}")
    
    rho = PyOpenMagnetics.get_material_resistivity("3C95", 25)
    print(f"  Resistivity: {rho:.2f} Ω·m")
    
    material = PyOpenMagnetics.find_core_material_by_name("3C95")
    steinmetz = PyOpenMagnetics.get_core_material_steinmetz_coefficients(material, 100000)
    print(f"  Steinmetz k={steinmetz['k']:.2e}, α={steinmetz['alpha']:.2f}, β={steinmetz['beta']:.2f}")


def wire_selection_example():
    """Demonstrate wire selection and loss calculation."""
    
    print("\n" + "=" * 60)
    print("WIRE SELECTION")
    print("=" * 60)
    
    # Find available wire types
    wire_types = PyOpenMagnetics.get_available_wire_types()
    print(f"\nAvailable wire types: {wire_types}")
    
    # Find wire by dimension
    round_wire = PyOpenMagnetics.find_wire_by_dimension(0.0005, "round", "IEC 60317")
    print(f"\n0.5mm round wire: {round_wire.get('name', 'N/A')}")
    
    # Calculate DC resistance
    R_dc = PyOpenMagnetics.calculate_dc_resistance_per_meter(round_wire, 25)
    print(f"  DC resistance: {R_dc*1000:.2f} mΩ/m at 25°C")
    
    R_dc_hot = PyOpenMagnetics.calculate_dc_resistance_per_meter(round_wire, 100)
    print(f"  DC resistance: {R_dc_hot*1000:.2f} mΩ/m at 100°C")
    
    # Litz wire for high frequency
    print("\nFor high-frequency applications, consider litz wire:")
    litz_wires = [w for w in PyOpenMagnetics.get_wire_names() if "litz" in w.lower()]
    print(f"  Available litz options: {len(litz_wires)} types")


if __name__ == "__main__":
    # Run the flyback design example
    best_design = design_flyback_transformer()
    
    # Explore the database
    explore_core_database()
    
    # Wire selection
    wire_selection_example()
    
    print("\n✓ All examples completed successfully!")

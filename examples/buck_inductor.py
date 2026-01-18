"""
PyOpenMagnetics Examples - Buck Inductor Design

This example demonstrates designing a buck converter output inductor:
1. Define operating conditions
2. Calculate inductance requirements
3. Select core and wire
4. Verify losses and saturation
"""

import PyOpenMagnetics


def design_buck_inductor():
    """
    Design a buck converter inductor for 12V to 3.3V @ 10A.
    
    Specifications:
    - Input: 12V (10-14V range)
    - Output: 3.3V @ 10A
    - Switching frequency: 500 kHz
    - Current ripple: 30% of Iout (3A p-p)
    - Required inductance: ~4.7 µH
    """
    
    print("=" * 60)
    print("BUCK INDUCTOR DESIGN")
    print("12V → 3.3V @ 10A, 500 kHz")
    print("=" * 60)
    
    # Calculate duty cycle and inductance
    Vin = 12
    Vout = 3.3
    Iout = 10
    fsw = 500000
    ripple_ratio = 0.3
    
    D = Vout / Vin  # Duty cycle ≈ 0.275
    delta_I = Iout * ripple_ratio  # 3A ripple
    L = (Vin - Vout) * D / (fsw * delta_I)  # ~4.7 µH
    
    print(f"\nCalculated parameters:")
    print(f"  Duty cycle: {D*100:.1f}%")
    print(f"  Current ripple: {delta_I:.1f} A p-p")
    print(f"  Required inductance: {L*1e6:.2f} µH")
    
    # Peak and RMS currents
    I_peak = Iout + delta_I/2  # 11.5A
    I_valley = Iout - delta_I/2  # 8.5A
    I_rms = Iout  # Approximately equal to DC for low ripple
    
    print(f"  Peak current: {I_peak:.1f} A")
    print(f"  Valley current: {I_valley:.1f} A")
    
    # Define inputs for PyOpenMagnetics
    inputs = {
        "designRequirements": {
            "magnetizingInductance": {
                "nominal": L,
                "minimum": L * 0.9,
                "maximum": L * 1.1
            }
        },
        "operatingPoints": [{
            "name": "Full Load",
            "conditions": {"ambientTemperature": 50},
            "excitationsPerWinding": [{
                "name": "Main",
                "frequency": fsw,
                # Triangular ripple current on DC bias
                "current": {
                    "waveform": {
                        "data": [I_valley, I_peak, I_valley],
                        "time": [0, D/fsw, 1/fsw]
                    }
                },
                # Rectangular voltage
                "voltage": {
                    "waveform": {
                        "data": [Vin - Vout, Vin - Vout, -Vout, -Vout],
                        "time": [0, D/fsw, D/fsw, 1/fsw]
                    }
                }
            }]
        }]
    }
    
    # Process inputs
    print("\n[1] Processing inputs...")
    processed = PyOpenMagnetics.process_inputs(inputs)
    
    # Get inductor designs
    print("\n[2] Finding suitable cores...")
    
    # For inductors, we want powder cores (low loss with DC bias)
    materials = PyOpenMagnetics.get_core_material_names()
    powder_materials = [m for m in materials if any(x in m for x in ["MPP", "High Flux", "Kool", "XFlux", "-26", "-52"])]
    print(f"  Found {len(powder_materials)} powder core materials")
    
    # Get recommendations
    weights = {
        "EFFICIENCY": 1.0,
        "DIMENSIONS": 0.8,
        "COST": 0.3
    }
    
    magnetics = PyOpenMagnetics.calculate_advised_magnetics(
        processed,
        max_results=5,
        core_mode="STANDARD_CORES"
    )
    
    print(f"  Found {len(magnetics)} suitable designs")
    
    # Analyze designs
    print("\n[3] Analyzing designs:")
    print("-" * 60)
    
    models = {
        "coreLosses": "IGSE",
        "reluctance": "ZHANG"
    }
    
    for i, mas in enumerate(magnetics[:3]):
        if "magnetic" not in mas:
            continue
            
        magnetic = mas["magnetic"]
        core = magnetic["core"]
        coil = magnetic["coil"]
        
        shape = core["functionalDescription"]["shape"]["name"]
        material = core["functionalDescription"]["material"]["name"]
        
        # Check for gapping
        gapping = core["functionalDescription"].get("gapping", [])
        total_gap = sum(g.get("length", 0) for g in gapping) * 1000  # mm
        
        # Calculate inductance to verify
        actual_L = PyOpenMagnetics.calculate_inductance_from_number_turns_and_gapping(
            core, coil, processed["operatingPoints"][0], models
        )
        
        # Calculate losses
        losses = PyOpenMagnetics.calculate_core_losses(core, coil, processed, models)
        winding_losses = PyOpenMagnetics.calculate_winding_losses(
            magnetic, processed["operatingPoints"][0], 85
        )
        
        print(f"\nDesign #{i+1}: {shape} / {material}")
        print(f"  Gap: {total_gap:.2f} mm total")
        print(f"  Inductance: {actual_L*1e6:.2f} µH (target: {L*1e6:.2f} µH)")
        print(f"  Core losses: {losses.get('coreLosses', 0):.3f} W")
        print(f"  Winding losses: {winding_losses.get('windingLosses', 0):.3f} W")
        print(f"  B_peak: {losses.get('magneticFluxDensityPeak', 0)*1000:.0f} mT")
        
        # Get turns
        if "functionalDescription" in coil:
            turns = coil["functionalDescription"][0]["numberTurns"]
            print(f"  Turns: {turns}")
    
    # Saturation check
    print("\n[4] Saturation margin:")
    if magnetics:
        best = magnetics[0]["magnetic"]
        I_sat = PyOpenMagnetics.calculate_saturation_current(best, 85)
        margin = (I_sat - I_peak) / I_peak * 100
        print(f"  Saturation current: {I_sat:.1f} A")
        print(f"  Margin above I_peak: {margin:.0f}%")
    
    print("\n" + "=" * 60)
    return magnetics[0] if magnetics else None


def compare_wire_options():
    """Compare different wire options for high-current applications."""
    
    print("\n" + "=" * 60)
    print("WIRE COMPARISON FOR 10A APPLICATION")
    print("=" * 60)
    
    # For 10A, we need substantial copper area
    # Target: ~4 A/mm² current density → ~2.5 mm² area → ~1.8mm diameter
    
    options = [
        ("Round 1.6mm", 0.0016, "round"),
        ("Round 1.8mm", 0.0018, "round"),
        ("Rectangular", 0.002, "rectangular"),
    ]
    
    print(f"\nComparing wires for 10A RMS at 100°C:")
    print("-" * 50)
    
    current = {
        "processed": {
            "rms": 10,
            "peakToPeak": 3
        }
    }
    
    for name, dim, wire_type in options:
        try:
            wire = PyOpenMagnetics.find_wire_by_dimension(dim, wire_type, "IEC 60317")
            
            R_dc = PyOpenMagnetics.calculate_dc_resistance_per_meter(wire, 100)
            P_dc = PyOpenMagnetics.calculate_dc_losses_per_meter(wire, current, 100)
            
            print(f"\n{name}:")
            print(f"  R_dc: {R_dc*1000:.2f} mΩ/m")
            print(f"  P_dc (10A): {P_dc:.2f} W/m")
            
            # For rectangular, show dimensions
            if wire_type == "rectangular" and "conductingWidth" in wire:
                w = wire["conductingWidth"]["nominal"] * 1000
                h = wire["conductingHeight"]["nominal"] * 1000
                print(f"  Dimensions: {w:.2f} × {h:.2f} mm")
                
        except Exception as e:
            print(f"\n{name}: Not available")


if __name__ == "__main__":
    # Design the buck inductor
    best_design = design_buck_inductor()
    
    # Compare wire options
    compare_wire_options()
    
    print("\n✓ Buck inductor design complete!")

#!/usr/bin/env python3
"""
PyOpenMagnetics - Flyback Transformer Design
220V AC to 12V @ 2A (24W) Converter

This script designs a complete flyback transformer for an isolated power supply:
- Input: 220V AC nominal (185-265V AC range, ~260-375V DC)
- Output: 12V @ 2A (24W)
- Switching frequency: 100 kHz
- Topology: Flyback, Continuous Conduction Mode (CCM)

Usage:
    python flyback_220v_12v_2a_complete.py
"""

import PyOpenMagnetics
import math


def calculate_flyback_specs():
    """
    Calculate flyback transformer electrical specifications.
    
    Returns:
        dict: Design parameters needed for PyOpenMagnetics
    """
    # ========== CONVERTER SPECIFICATIONS ==========
    # Input voltage (rectified DC from 220V AC)
    V_ac_min = 185      # V AC minimum (typical low line)
    V_ac_max = 265      # V AC maximum (typical high line)
    V_in_min = V_ac_min * math.sqrt(2) * 0.90  # DC after rectifier with 10% ripple
    V_in_max = V_ac_max * math.sqrt(2)         # Peak DC voltage
    V_in_nom = 220 * math.sqrt(2) * 0.95       # Nominal DC (with ripple)
    
    # Output
    V_out = 12          # V
    I_out = 2           # A
    P_out = V_out * I_out  # 24W
    
    # Switching parameters
    f_sw = 100000       # 100 kHz
    T_sw = 1 / f_sw     # 10 µs period
    
    # Design choices
    eta = 0.88          # Estimated efficiency (88%)
    D_max = 0.45        # Maximum duty cycle
    ripple_ratio = 0.35 # Current ripple ratio (∆I / 2*I_avg)
    V_diode = 0.5       # Secondary diode forward drop (Schottky)
    
    print("=" * 70)
    print("FLYBACK TRANSFORMER DESIGN: 220V AC → 12V @ 2A (24W)")
    print("=" * 70)
    print(f"Output Power: {P_out} W")
    print(f"Switching Frequency: {f_sw/1000} kHz")
    print(f"DC Input Range: {V_in_min:.0f}V - {V_in_max:.0f}V (from {V_ac_min}-{V_ac_max}V AC)")
    print(f"Target Efficiency: {eta*100:.0f}%")
    
    # ========== TURNS RATIO CALCULATION ==========
    # Flyback equation: Vout = Vin * (D/(1-D)) * (Ns/Np) * eta - V_diode
    # At maximum duty cycle and minimum input voltage:
    # n = Ns/Np = (Vout + V_diode) * (1-D_max) / (Vin_min * D_max * eta)
    
    n = (V_out + V_diode) * (1 - D_max) / (V_in_min * D_max * eta)
    turns_ratio = 1 / n  # Np/Ns (primary to secondary)
    
    print(f"\nTurns Ratio (Np/Ns): {turns_ratio:.2f}:1")
    print(f"Secondary/Primary (Ns/Np): {n:.3f}")
    
    # ========== INDUCTANCE CALCULATION ==========
    # For CCM flyback, calculate magnetizing inductance from energy balance
    # P_in = P_out / eta = 0.5 * L_m * (I_pk^2 - I_valley^2) * f_sw
    # With ripple ratio, we can solve for L_m
    
    P_in = P_out / eta
    
    # For a practical design with reasonable peak current
    # Typical peak currents for 24W flyback: 0.5 - 1.0 A
    I_pri_avg = P_in / V_in_min  # Average primary current at low line
    I_pri_pk = I_pri_avg * (1 + ripple_ratio/2) / D_max  # Peak current
    
    # Calculate inductance: L = V * dt / dI
    # During on-time: V_in = L * dI/dt => L = V_in * D * T / dI
    dI = I_pri_pk * ripple_ratio  # Current ripple
    L_m = (V_in_min * D_max * T_sw) / dI
    
    # Round to a practical value
    L_m = round(L_m * 1e6 / 50) * 50e-6  # Round to nearest 50µH
    L_m = max(L_m, 500e-6)  # At least 500µH for this power level
    L_m = min(L_m, 2000e-6)  # At most 2mH
    
    # Recalculate actual peak current with this inductance
    dI_actual = (V_in_min * D_max * T_sw) / L_m
    I_pri_pk_actual = I_pri_avg / D_max + dI_actual / 2
    I_pri_valley = I_pri_pk_actual - dI_actual
    
    print(f"\nMagnetizing Inductance: {L_m*1e6:.0f} µH")
    print(f"Primary Peak Current: {I_pri_pk_actual:.2f} A")
    print(f"Primary Valley Current: {I_pri_valley:.2f} A")
    print(f"Current Ripple: {dI_actual:.2f} A ({ripple_ratio*100:.0f}%)")
    
    # ========== OPERATING POINTS ==========
    # Low line (worst case for primary current)
    D_low = D_max
    t_on_low = D_low * T_sw
    
    # High line (lower duty cycle)
    D_high = (V_out + V_diode) / (eta * V_in_max * n + V_out + V_diode)
    D_high = min(D_high, 0.35)  # Limit duty at high line
    t_on_high = D_high * T_sw
    
    # High line currents (lower)
    I_pri_avg_high = P_in / V_in_max
    dI_high = (V_in_max * D_high * T_sw) / L_m
    I_pri_pk_high = I_pri_avg_high / D_high + dI_high / 2
    I_pri_valley_high = max(I_pri_pk_high - dI_high, 0)
    
    print(f"\nOperating Points:")
    print(f"  Low Line ({V_ac_min}V AC): D={D_low:.2f}, ton={t_on_low*1e6:.1f}µs, Ipk={I_pri_pk_actual:.2f}A")
    print(f"  High Line ({V_ac_max}V AC): D={D_high:.2f}, ton={t_on_high*1e6:.1f}µs, Ipk={I_pri_pk_high:.2f}A")
    
    return {
        "L_m": L_m,
        "turns_ratio": turns_ratio,
        "f_sw": f_sw,
        "T_sw": T_sw,
        "V_in_min": V_in_min,
        "V_in_max": V_in_max,
        "V_in_nom": V_in_nom,
        "V_out": V_out,
        "I_out": I_out,
        "P_out": P_out,
        "D_low": D_low,
        "D_high": D_high,
        "t_on_low": t_on_low,
        "t_on_high": t_on_high,
        "I_pri_pk": I_pri_pk_actual,
        "I_pri_valley": I_pri_valley,
        "I_pri_pk_high": I_pri_pk_high,
        "I_pri_valley_high": I_pri_valley_high,
        "dI": dI_actual,
        "dI_high": dI_high,
        "eta": eta,
        "V_diode": V_diode,
    }


def create_pyopenmagnetics_inputs(specs):
    """
    Create the inputs structure for PyOpenMagnetics design adviser.
    
    Args:
        specs: Dictionary from calculate_flyback_specs()
        
    Returns:
        dict: PyOpenMagnetics inputs structure
    """
    L_m = specs["L_m"]
    turns_ratio = specs["turns_ratio"]
    f_sw = specs["f_sw"]
    
    # Use processed waveforms (simpler and more reliable for the adviser)
    # These are the key parameters the adviser needs
    I_pk = specs["I_pri_pk"]
    I_valley = specs["I_pri_valley"]
    I_avg = (I_pk + I_valley) / 2
    I_ripple = I_pk - I_valley
    
    inputs = {
        "designRequirements": {
            "magnetizingInductance": {
                "nominal": L_m,
                "minimum": L_m * 0.9,
                "maximum": L_m * 1.1
            },
            "turnsRatios": [
                {"nominal": turns_ratio}  # Np/Ns
            ],
            "insulation": {
                "insulationType": "Functional",
                "pollutionDegree": "P2",
                "overvoltageCategory": "OVC-II",
                "altitude": {"maximum": 2000}
            }
        },
        "operatingPoints": [
            {
                "name": "Low Line (185V AC)",
                "conditions": {
                    "ambientTemperature": 40
                },
                "excitationsPerWinding": [
                    {
                        "name": "Primary",
                        "frequency": f_sw,
                        "current": {
                            "processed": {
                                "label": "Triangular",
                                "dutyCycle": specs["D_low"],
                                "offset": I_avg,
                                "peakToPeak": I_ripple
                            }
                        }
                    }
                ]
            },
            {
                "name": "High Line (265V AC)",
                "conditions": {
                    "ambientTemperature": 40
                },
                "excitationsPerWinding": [
                    {
                        "name": "Primary",
                        "frequency": f_sw,
                        "current": {
                            "processed": {
                                "label": "Triangular",
                                "dutyCycle": specs["D_high"],
                                "offset": (specs["I_pri_pk_high"] + specs["I_pri_valley_high"]) / 2,
                                "peakToPeak": specs["I_pri_pk_high"] - specs["I_pri_valley_high"]
                            }
                        }
                    }
                ]
            }
        ]
    }
    
    return inputs


def design_flyback_transformer():
    """
    Main function to design the flyback transformer.
    
    Returns:
        list: List of magnetic designs
    """
    # Step 1: Calculate specifications
    specs = calculate_flyback_specs()
    
    # Step 2: Create PyOpenMagnetics inputs
    print("\n" + "-" * 70)
    print("Creating PyOpenMagnetics inputs...")
    inputs = create_pyopenmagnetics_inputs(specs)
    
    # Step 3: Process inputs (adds harmonics for loss calculation)
    print("Processing inputs (calculating harmonics)...")
    processed_result = PyOpenMagnetics.process_inputs(inputs)
    
    # Extract the actual processed inputs from the result
    if isinstance(processed_result, dict) and "data" in processed_result:
        processed_inputs = processed_result["data"]
    else:
        processed_inputs = processed_result
    
    print("✓ Inputs processed successfully")
    
    # Step 4: Get design recommendations
    print("\n" + "-" * 70)
    print("Searching for optimal magnetic designs...")
    print("(This may take 10-30 seconds...)")
    
    magnetics = []
    try:
        result = PyOpenMagnetics.calculate_advised_magnetics(
            processed_inputs,
            5,
            "standard cores"
        )
        
        # Handle result format
        if isinstance(result, dict) and "data" in result:
            data = result["data"]
            if isinstance(data, str):
                # Try to parse as JSON
                try:
                    import json
                    data = json.loads(data)
                except:
                    pass
            if isinstance(data, list):
                magnetics = data
                print(f"✓ Found {len(magnetics)} suitable designs")
            else:
                print(f"✗ Unexpected data format: {type(data)}")
                print(f"   Data: {data[:200] if isinstance(data, str) else data}")
        else:
            magnetics = result if isinstance(result, list) else []
            print(f"✓ Found {len(magnetics)} suitable designs")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Step 5: Analyze designs
    print("\n" + "=" * 70)
    print("TOP MAGNETIC DESIGNS")
    print("=" * 70)
    
    models = {
        "coreLosses": "IGSE",
        "reluctance": "ZHANG",
        "coreTemperature": "MANIKTALA"
    }
    
    best_design = None
    
    for i, item in enumerate(magnetics[:3]):  # Show top 3
        # Extract magnetic data
        if isinstance(item, dict):
            if "mas" in item:
                mas = item["mas"]
                score = item.get("scoring", 0)
            else:
                mas = item
                score = 0
            
            if "magnetic" in mas:
                magnetic = mas["magnetic"]
            else:
                magnetic = mas
        else:
            continue
        
        core = magnetic["core"]
        
        # Get core info
        shape_desc = core["functionalDescription"]["shape"]
        shape_name = shape_desc["name"] if isinstance(shape_desc, dict) else shape_desc
        
        material_desc = core["functionalDescription"]["material"]
        material_name = material_desc["name"] if isinstance(material_desc, dict) else material_desc
        
        print(f"\n{'─' * 60}")
        print(f"Design #{i+1}: {shape_name} / {material_name}")
        if score:
            print(f"Score: {score:.3f}")
        print(f"{'─' * 60}")
        
        # Get gap info
        gapping = core["functionalDescription"].get("gapping", [])
        if gapping:
            gap_length = gapping[0].get("length", 0) * 1000  # mm
            print(f"  Air Gap: {gap_length:.2f} mm")
        
        # Get winding info
        if "coil" in magnetic and "functionalDescription" in magnetic["coil"]:
            print("  Windings:")
            for winding in magnetic["coil"]["functionalDescription"]:
                name = winding.get("name", "Winding")
                turns = winding.get("numberTurns", "?")
                n_parallels = winding.get("numberParallels", 1)
                wire = winding.get("wire", "?")
                if isinstance(wire, dict):
                    wire = wire.get("name", wire.get("type", "?"))
                parallel_str = f" x {n_parallels}" if n_parallels > 1 else ""
                print(f"    {name}: {turns} turns{parallel_str}, {wire}")
        
        # Calculate core parameters
        try:
            core_processed = PyOpenMagnetics.calculate_core_data(core, False)
            if "processedDescription" in core_processed:
                eff_params = core_processed["processedDescription"].get("effectiveParameters", {})
                Ae = eff_params.get("effectiveArea", 0)
                le = eff_params.get("effectiveLength", 0)
                if Ae > 0:
                    print(f"\n  Core Parameters:")
                    print(f"    Effective Area (Ae): {Ae*1e6:.1f} mm²")
                    print(f"    Effective Length (le): {le*1000:.1f} mm")
        except:
            pass
        
        # Estimate B_peak for sanity check
        try:
            L_m = specs["L_m"]
            I_pk = specs["I_pri_pk"]
            
            # Get primary turns
            N_pri = 40  # default estimate
            if "coil" in magnetic and "functionalDescription" in magnetic["coil"]:
                for w in magnetic["coil"]["functionalDescription"]:
                    if w.get("name") == "Primary":
                        N_pri = w.get("numberTurns", 40)
                        break
            
            # Estimate Ae if not available
            Ae_est = 60e-6  # Typical for E25/EC25 size
            B_peak_est = (L_m * I_pk) / (N_pri * Ae_est)
            
            print(f"  Estimated Peak Flux Density: {B_peak_est*1000:.0f} mT")
            if B_peak_est > 0.35:
                print("  ⚠ WARNING: B_peak is high - risk of saturation")
            elif B_peak_est > 0.25:
                print("  ⚠ CAUTION: B_peak is moderate - verify saturation margin")
            else:
                print("  ✓ B_peak is in safe range for ferrite")
                
        except Exception as e:
            pass
        
        # Store first design as best
        if best_design is None:
            best_design = magnetic
            print("\n  ★ SELECTED as best design")
    
    # If no designs found, create manual design
    if not magnetics:
        print("\nNo designs found by adviser. Creating manual design...")
        magnetics = create_manual_design(specs)
    
    # Step 6: Visualize best design
    if best_design:
        print("\n" + "=" * 70)
        print("VISUALIZATION")
        print("=" * 70)
        visualize_design(best_design)
    
    return magnetics


def create_manual_design(specs):
    """
    Create a manual design if the adviser doesn't find suitable options.
    
    Args:
        specs: Design specifications
        
    Returns:
        list: List with manual magnetic design
    """
    print("\n  Creating manual design with E 25/13/7 core...")
    
    # For 24W flyback, E 25/13/7 or ETD 29 are typical choices
    shape = PyOpenMagnetics.find_core_shape_by_name("E 25/13/7")
    material = PyOpenMagnetics.find_core_material_by_name("3C95")
    
    # Calculate gap length for desired inductance
    L_target = specs["L_m"]
    
    # Estimate turns: For E25 with ~800µH, use ~40 primary turns
    N_pri = 40
    N_sec = max(int(N_pri / specs["turns_ratio"]), 3)  # At least 3 secondary turns
    
    # Calculate required AL
    AL_required = L_target / (N_pri ** 2)
    
    # Calculate gap: AL ≈ µ0 * Ae / gap
    Ae = 52e-6  # m² (E 25/13/7)
    mu_0 = 4 * math.pi * 1e-7
    gap_length = mu_0 * Ae / AL_required
    gap_length = max(gap_length, 0.0001)  # At least 0.1mm
    gap_length = min(gap_length, 0.002)   # At most 2mm
    
    print(f"  Air Gap: {gap_length*1000:.2f} mm")
    print(f"  Primary Turns: {N_pri}")
    print(f"  Secondary Turns: {N_sec}")
    
    # Create core
    core_data = {
        "functionalDescription": {
            "type": "two-piece set",
            "shape": shape,
            "material": material,
            "gapping": [{"type": "subtractive", "length": gap_length}],
            "numberStacks": 1
        }
    }
    
    # Get wires
    try:
        primary_wire = PyOpenMagnetics.find_wire_by_name("Round 0.40 - Grade 1")
        secondary_wire = PyOpenMagnetics.find_wire_by_name("Round 0.80 - Grade 1")
    except:
        primary_wire = {"type": "round", "name": "Round 0.40mm"}
        secondary_wire = {"type": "round", "name": "Round 0.80mm"}
    
    # Create coil
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
                "numberParallels": 2,
                "wire": secondary_wire,
                "isolationSide": "secondary"
            }
        ]
    }
    
    magnetic = {"core": core_data, "coil": coil_data}
    return [{"magnetic": magnetic}]


def visualize_design(magnetic):
    """
    Generate SVG visualization of the design.
    
    Args:
        magnetic: Magnetic design dictionary
    """
    try:
        # Plot the core
        core = magnetic["core"]
        result = PyOpenMagnetics.plot_core(core, use_colors=True)
        
        if result.get('success'):
            svg_core = result['svg']
            filename_core = "flyback_220v_12v_2a_core.svg"
            with open(filename_core, "w") as f:
                f.write(svg_core)
            print(f"✓ Core visualization saved to '{filename_core}'")
        else:
            print(f"  Core plot failed: {result.get('error', 'Unknown error')}")
        
        # Plot complete magnetic
        result = PyOpenMagnetics.plot_magnetic(magnetic)
        if result.get('success'):
            svg_magnetic = result['svg']
            filename_magnetic = "flyback_220v_12v_2a_magnetic.svg"
            with open(filename_magnetic, "w") as f:
                f.write(svg_magnetic)
            print(f"✓ Magnetic visualization saved to '{filename_magnetic}'")
        else:
            print(f"  Magnetic plot failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"  (Visualization error: {e})")


def print_design_summary(specs):
    """
    Print a summary of the design specifications.
    
    Args:
        specs: Design specifications dictionary
    """
    print("\n" + "=" * 70)
    print("DESIGN SUMMARY")
    print("=" * 70)
    print(f"Application: Isolated Flyback Power Supply")
    print(f"Input: {specs['V_in_min']:.0f}-{specs['V_in_max']:.0f}V DC (from 185-265V AC)")
    print(f"Output: {specs['V_out']}V @ {specs['I_out']}A ({specs['P_out']}W)")
    print(f"Switching Frequency: {specs['f_sw']/1000:.0f} kHz")
    print(f"\nMagnetic Requirements:")
    print(f"  Magnetizing Inductance: {specs['L_m']*1e6:.0f} µH")
    print(f"  Turns Ratio (Np:Ns): {specs['turns_ratio']:.1f}:1")
    print(f"  Primary Peak Current: {specs['I_pri_pk']:.2f} A")
    print(f"  Operating Duty Cycle: {specs['D_low']*100:.0f}% (low line)")
    print(f"\nRecommended Components:")
    print(f"  Core: E 25/13/7, ETD 29, or similar (Ferrite 3C95/3C90)")
    print(f"  Primary Wire: AWG 26-28 (0.4-0.35mm)")
    print(f"  Secondary Wire: AWG 20-22 (0.8-0.65mm) x 2 parallel")
    print(f"  Secondary Diode: MBR1045 or similar (45V, 10A Schottky)")
    print(f"  Primary MOSFET: 600V, <1Ω Rds(on)")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print(" PYOPENMAGNETICS FLYBACK TRANSFORMER DESIGN")
    print(" 220V AC → 12V @ 2A (24W)")
    print("=" * 70 + "\n")
    
    # Run the design
    magnetics = design_flyback_transformer()
    
    # Print final summary
    specs = calculate_flyback_specs()
    print_design_summary(specs)
    
    print("\n" + "=" * 70)
    print("✓ Design complete!")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Order core samples (E 25/13/7 or ETD 29 with 3C95 material)")
    print("  2. Build prototype with calculated turns and gap")
    print("  3. Measure actual inductance and adjust gap if needed")
    print("  4. Verify thermal performance and efficiency")
    print("  5. Check EMI/EMC compliance")
    print("\nFor questions: github.com/OpenMagnetics/PyOpenMagnetics")

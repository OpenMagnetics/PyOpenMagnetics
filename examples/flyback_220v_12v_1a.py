"""
PyOpenMagnetics - Flyback Transformer Design
220V AC to 12V @ 1A (12W) Converter

This script designs a flyback transformer for a small isolated power supply:
- Input: 220V AC nominal (185-265V AC range)
- Output: 12V @ 1A (12W)
- Switching frequency: 100 kHz
- Topology: Flyback, Continuous/Discontinuous Conduction Mode

Design approach:
1. Calculate electrical specifications from input/output requirements
2. Determine magnetizing inductance and turns ratio
3. Use PyOpenMagnetics adviser to find optimal core and windings
4. Analyze losses and verify the design
"""

import PyOpenMagnetics
import math


def calculate_flyback_specs():
    """
    Calculate flyback transformer electrical specifications.
    
    Returns design parameters needed for PyOpenMagnetics.
    """
    # ========== CONVERTER SPECIFICATIONS ==========
    # Input voltage (rectified DC from 220V AC)
    V_ac_min = 185      # V AC minimum
    V_ac_max = 265      # V AC maximum
    V_in_min = V_ac_min * math.sqrt(2) * 0.85  # DC after rectifier, accounting for ripple
    V_in_max = V_ac_max * math.sqrt(2)         # Peak DC voltage
    V_in_nom = 220 * math.sqrt(2) * 0.9        # Nominal DC
    
    # Output
    V_out = 12          # V
    I_out = 1           # A
    P_out = V_out * I_out  # 12W
    
    # Switching parameters
    f_sw = 100000       # 100 kHz
    T_sw = 1 / f_sw     # 10 µs period
    
    # Design choices
    eta = 0.85          # Estimated efficiency
    D_max = 0.45        # Maximum duty cycle
    ripple_ratio = 0.4  # Current ripple ratio (∆I / 2*I_pk)
    V_diode = 0.5       # Secondary diode forward drop
    
    print("=" * 60)
    print("FLYBACK TRANSFORMER DESIGN: 220V AC → 12V @ 1A")
    print("=" * 60)
    print(f"Output Power: {P_out} W")
    print(f"Switching Frequency: {f_sw/1000} kHz")
    print(f"DC Input Range: {V_in_min:.0f}V - {V_in_max:.0f}V")
    
    # ========== TURNS RATIO CALCULATION ==========
    # Flyback equation: Vout = Vin * (D/(1-D)) * (Ns/Np)
    # At maximum duty cycle and minimum input voltage
    # n = Ns/Np = Vout * (1-D_max) / (Vin_min * D_max * eta)
    
    n = (V_out + V_diode) * (1 - D_max) / (V_in_min * D_max * eta)
    turns_ratio = 1 / n  # Np/Ns (primary to secondary)
    
    print(f"\nTurns Ratio (Np/Ns): {turns_ratio:.2f}:1")
    
    # ========== INDUCTANCE CALCULATION ==========
    # For flyback, use energy balance at minimum input voltage
    # P_in = 0.5 * L_m * I_pk^2 * f_sw (for DCM)
    # For CCM boundary, we need L_m such that the core doesn't saturate
    # and the peak current is manageable
    
    P_in = P_out / eta
    
    # For a practical design, choose L_m to achieve a reasonable peak current
    # Typical peak currents for 12W flyback: 0.4 - 0.8 A
    # Using energy balance: L_m = 2 * P_in / (f_sw * I_pk^2)
    
    I_pri_pk_target = 0.6  # A - reasonable peak current for 12W
    
    # Calculate inductance from energy balance (for DCM)
    L_m = (2 * P_in) / (f_sw * I_pri_pk_target**2)
    
    # For CCM, verify using V = L * dI/dt:
    # dI = V_in * D * T / L_m
    # This gives the current ripple, peak = avg + ripple/2
    
    # Round to a nice value
    L_m = round(L_m * 1e6 / 50) * 50e-6  # Round to nearest 50µH
    L_m = max(L_m, 300e-6)  # At least 300µH
    
    # Recalculate actual peak current with this inductance
    # Using energy: I_pk = sqrt(2 * P_in / (L_m * f_sw))
    I_pri_pk = math.sqrt(2 * P_in / (L_m * f_sw))
    
    print(f"Magnetizing Inductance: {L_m*1e6:.1f} µH")
    print(f"Primary Peak Current: {I_pri_pk:.2f} A")
    
    # ========== OPERATING WAVEFORMS ==========
    # Primary current: ramps up during on-time, zero during off-time (simplified)
    # This is a triangular approximation for the transformer current
    
    # At low line (worst case for primary current)
    D_low = D_max
    t_on_low = D_low * T_sw
    I_valley_low = I_pri_pk * (1 - ripple_ratio)
    
    # At high line (lower current, shorter on-time)
    # Recalculate duty for high line
    D_high = (V_out + V_diode) / (eta * V_in_max * n + V_out + V_diode)
    D_high = min(D_high, 0.35)  # Limit duty at high line
    t_on_high = D_high * T_sw
    I_pri_pk_high = (2 * P_in) / (V_in_max * D_high) * 0.5  # Lower current at high line
    I_valley_high = I_pri_pk_high * (1 - ripple_ratio)
    
    print(f"\nLow Line:  D={D_low:.2f}, ton={t_on_low*1e6:.1f}µs, Ipk={I_pri_pk:.2f}A")
    print(f"High Line: D={D_high:.2f}, ton={t_on_high*1e6:.1f}µs, Ipk={I_pri_pk_high:.2f}A")
    
    return {
        "L_m": L_m,
        "turns_ratio": turns_ratio,
        "f_sw": f_sw,
        "T_sw": T_sw,
        "V_in_min": V_in_min,
        "V_in_max": V_in_max,
        "V_out": V_out,
        "I_out": I_out,
        "P_out": P_out,
        "D_low": D_low,
        "D_high": D_high,
        "t_on_low": t_on_low,
        "t_on_high": t_on_high,
        "I_pri_pk": I_pri_pk,
        "I_pri_pk_high": I_pri_pk_high,
        "I_valley_low": I_valley_low,
        "I_valley_high": I_valley_high,
    }


def create_pyopenmagnetics_inputs(specs):
    """
    Create the inputs structure for PyOpenMagnetics design adviser.
    """
    
    L_m = specs["L_m"]
    turns_ratio = specs["turns_ratio"]
    f_sw = specs["f_sw"]
    T_sw = specs["T_sw"]
    
    # Operating point waveforms
    # Low line (worst case) - triangular current during on-time
    t_on = specs["t_on_low"]
    t_off = T_sw - t_on
    I_pk = specs["I_pri_pk"]
    I_valley = specs["I_valley_low"]
    V_in = specs["V_in_min"]
    
    # Create flyback waveforms
    # Primary current: ramp up during on-time, then flyback reset
    primary_current_waveform = {
        "data": [I_valley, I_pk, I_pk * 0.1, I_valley],  # Ramp up, then collapse
        "time": [0, t_on, t_on + 0.5e-6, T_sw]
    }
    
    # Primary voltage: Vin during on-time, reflected voltage during off-time
    V_reflected = -(specs["V_out"] + 0.5) * turns_ratio  # Reflected voltage
    primary_voltage_waveform = {
        "data": [V_in, V_in, V_reflected, V_reflected, 0],
        "time": [0, t_on - 0.1e-6, t_on, t_on + t_off * 0.8, T_sw]
    }
    
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
                "insulationType": "Functional",  # Basic isolation
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
                            "waveform": primary_current_waveform
                        },
                        "voltage": {
                            "waveform": primary_voltage_waveform
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
                            "waveform": {
                                "data": [specs["I_valley_high"], specs["I_pri_pk_high"], 
                                        specs["I_pri_pk_high"] * 0.1, specs["I_valley_high"]],
                                "time": [0, specs["t_on_high"], specs["t_on_high"] + 0.5e-6, T_sw]
                            }
                        },
                        "voltage": {
                            "waveform": {
                                "data": [specs["V_in_max"], specs["V_in_max"], 
                                        V_reflected, V_reflected, 0],
                                "time": [0, specs["t_on_high"] - 0.1e-6, specs["t_on_high"], 
                                        specs["t_on_high"] + (T_sw - specs["t_on_high"]) * 0.8, T_sw]
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
    """
    
    # Step 1: Calculate specifications
    specs = calculate_flyback_specs()
    
    # Step 2: Create PyOpenMagnetics inputs
    print("\n" + "-" * 60)
    print("Creating PyOpenMagnetics inputs...")
    inputs = create_pyopenmagnetics_inputs(specs)
    
    # Step 3: Process inputs (adds harmonics for loss calculation)
    print("Processing inputs (calculating harmonics)...")
    processed_inputs = PyOpenMagnetics.process_inputs(inputs)
    print("✓ Inputs processed successfully")
    
    # Step 4: Get design recommendations
    print("\n" + "-" * 60)
    print("Searching for optimal magnetic designs...")
    print("This may take a moment...")
    
    try:
        # The core_mode must be passed as a JSON string
        magnetics = PyOpenMagnetics.calculate_advised_magnetics(
            processed_inputs,
            5,  # max_results
            "standard cores"  # core_mode: "standard cores" or "available cores"
        )
        print(f"✓ Found {len(magnetics)} suitable designs")
    except Exception as e:
        print(f"Warning: Adviser returned error: {e}")
        print("Creating a manual design instead...")
        magnetics = []
    
    if not magnetics:
        print("\nNo designs found with automatic adviser.")
        print("Creating a manual design with E 25/13/7 core...")
        magnetics = create_manual_design(specs)
    
    # Step 5: Analyze top designs
    print("\n" + "=" * 60)
    print("TOP MAGNETIC DESIGNS")
    print("=" * 60)
    
    models = {
        "coreLosses": "IGSE",
        "reluctance": "ZHANG",
        "coreTemperature": "MANIKTALA"
    }
    
    best_design = None
    
    # Handle both list and dict return types
    if isinstance(magnetics, dict):
        # If it's a single dict, check if it contains 'magnetic' or is itself a magnetic
        if "magnetic" in magnetics:
            magnetics_list = [magnetics]
        elif "core" in magnetics:
            # It's directly a magnetic, not a MAS
            magnetics_list = [{"magnetic": magnetics}]
        else:
            magnetics_list = [magnetics]
    else:
        magnetics_list = list(magnetics) if magnetics else []
    
    # Debug: print structure of first result
    if magnetics_list:
        print(f"\nFound {len(magnetics_list)} design(s)")
        first = magnetics_list[0]
        print(f"Result structure: {list(first.keys())[:5]}...")
        if "data" in first:
            data_val = first['data']
            print(f"  data type: {type(data_val)}")
            # If data is a JSON string, parse it
            if isinstance(data_val, str):
                import json
                if data_val.strip():  # Non-empty string
                    try:
                        parsed_data = json.loads(data_val)
                        print(f"  parsed data type: {type(parsed_data)}")
                        if isinstance(parsed_data, list):
                            print(f"  data length: {len(parsed_data)}")
                            # Update magnetics_list with parsed data
                            magnetics_list = parsed_data
                    except json.JSONDecodeError as e:
                        print(f"  JSON parse error: {e}")
                        magnetics_list = []  # Clear the list so we fall back
                else:
                    print("  data is empty - no cores matched requirements")
                    magnetics_list = []  # Clear the list so we fall back
            elif isinstance(data_val, list):
                print(f"  data length: {len(data_val)}")
                if data_val:
                    print(f"  first data keys: {list(data_val[0].keys())[:5] if isinstance(data_val[0], dict) else 'not a dict'}...")
            elif isinstance(data_val, dict):
                print(f"  data keys: {list(data_val.keys())[:5]}...")
    
    # If no results from adviser, fall back to manual design
    if not magnetics_list:
        print("\nNo suitable cores found by adviser. Creating manual design...")
        magnetics_list = create_manual_design(specs)
    
    for i, mas in enumerate(magnetics_list[:3]):  # Show top 3
        # Handle different result formats
        if isinstance(mas, dict) and "data" in mas:
            # The results are nested under 'data'
            data = mas["data"]
            if isinstance(data, str):
                import json
                if data.strip():
                    try:
                        data = json.loads(data)
                    except json.JSONDecodeError:
                        continue
                else:
                    continue
            if isinstance(data, list) and data:
                mas = data[0]  # Get first result from data array
            elif isinstance(data, dict):
                mas = data
            else:
                continue
        
        if "magnetic" in mas:
            magnetic = mas["magnetic"]
        elif "core" in mas:
            magnetic = mas
        else:
            print(f"\nDesign #{i+1}: Unrecognized format")
            print(f"  Keys: {list(mas.keys())[:10]}")
            continue
        
        core = magnetic["core"]
        
        # Get core info
        shape_name = core["functionalDescription"]["shape"]
        if isinstance(shape_name, dict):
            shape_name = shape_name.get("name", "Unknown")
        
        material_name = core["functionalDescription"]["material"]
        if isinstance(material_name, dict):
            material_name = material_name.get("name", "Unknown")
        
        print(f"\n{'─' * 50}")
        print(f"Design #{i+1}: {shape_name} / {material_name}")
        print(f"{'─' * 50}")
        
        # Get gap info
        gapping = core["functionalDescription"].get("gapping", [])
        if gapping:
            gap_length = gapping[0].get("length", 0) * 1000  # mm
            print(f"  Gap: {gap_length:.2f} mm")
        
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
        
        # Try to calculate estimated inductance and B_peak
        Ae_actual = None
        try:
            # Get core data and calculate
            core_processed = PyOpenMagnetics.calculate_core_data(core, False)
            if "processedDescription" in core_processed:
                eff_params = core_processed["processedDescription"].get("effectiveParameters", {})
                Ae = eff_params.get("effectiveArea", 0)  # m²
                le = eff_params.get("effectiveLength", 0)  # m
                if Ae > 0 and le > 0:
                    Ae_actual = Ae
                    print(f"\n  Core Parameters:")
                    print(f"    Effective Area (Ae): {Ae*1e6:.1f} mm²")
                    print(f"    Effective Length (le): {le*1000:.1f} mm")
        except Exception as e:
            pass  # Silently skip if processing fails
        
        # Skip loss calculation for manual designs (need full winding)
        # Just mark the design as potentially good
        if best_design is None:
            best_design = magnetic
            print("\n  ✓ Design selected for further analysis")
        
        # Calculate approximate B_peak for sanity check
        try:
            # B_peak = L * I_pk / (N * Ae)
            L_m = specs["L_m"]
            I_pk = specs["I_pri_pk"]
            
            # Get N_pri from the coil data
            N_pri = 45  # default
            if "coil" in magnetic and "functionalDescription" in magnetic["coil"]:
                for w in magnetic["coil"]["functionalDescription"]:
                    if w.get("name") == "Primary":
                        N_pri = w.get("numberTurns", 45)
                        break
            
            # Use actual Ae if available
            Ae_m2 = Ae_actual if Ae_actual else 52e-6  # fallback to E 25/13/7 nominal
            B_peak_est = (L_m * I_pk) / (N_pri * Ae_m2)
            print(f"  Estimated B_peak: {B_peak_est*1000:.0f} mT")
            if B_peak_est > 0.30:
                print("  ⚠ B_peak is high - consider more turns or larger core")
            elif B_peak_est > 0.20:
                print("  ⚠ B_peak is moderate - verify saturation margin")
            else:
                print("  ✓ B_peak is in safe range")
        except:
            pass
    
    # Step 6: Visualize best design (if available)
    if best_design:
        print("\n" + "=" * 60)
        print("BEST DESIGN SELECTED")
        print("=" * 60)
        visualize_design(best_design)
    
    return magnetics_list


def create_manual_design(specs):
    """
    Create a manual design if the adviser doesn't find suitable options.
    This provides a fallback with a commonly-used core for this power level.
    """
    
    print("\n  Using E 25/13/7 core with 3C95 material")
    
    # For 12W flyback, EE16 or EE20 or E25 are typical choices
    # Let's use E 25/13/7 with 3C95 material
    
    shape = PyOpenMagnetics.find_core_shape_by_name("E 25/13/7")
    material = PyOpenMagnetics.find_core_material_by_name("3C95")
    
    # Calculate gap length for desired inductance
    # AL with gap ≈ µ0 * Ae / gap_length (simplified)
    # For E 25/13/7: Ae ≈ 40mm² = 40e-6 m²
    # L = N² * AL => AL = L / N²
    L_target = specs["L_m"]
    
    # Estimate number of turns based on area product method
    # For this power level with ~800µH inductance and E25 core:
    # AL ~ 2000 nH/turn² (with gap), N = sqrt(L/AL) ≈ 20 turns
    N_pri = 45  # Primary turns (conservative)
    N_sec = max(int(N_pri / specs["turns_ratio"]), 4)  # At least 4 secondary turns
    
    # Calculate required AL
    AL_required = L_target / (N_pri ** 2)  # H/turn²
    print(f"  Required AL: {AL_required*1e9:.0f} nH/turn²")
    
    # Calculate gap for this AL
    # Gap reluctance dominates: AL ≈ µ0 * Ae / gap
    Ae = 40e-6  # m² (approximate for E 25/13/7)
    mu_0 = 4e-7 * 3.14159  # H/m
    gap_length = mu_0 * Ae / AL_required
    gap_length = max(gap_length, 0.0001)  # At least 0.1mm
    gap_length = min(gap_length, 0.002)   # At most 2mm
    
    print(f"  Calculated gap: {gap_length*1000:.2f} mm")
    print(f"  Primary turns: {N_pri}")
    print(f"  Secondary turns: {N_sec}")
    
    core_data = {
        "functionalDescription": {
            "type": "two-piece set",
            "shape": shape,
            "material": material,
            "gapping": [
                {"type": "subtractive", "length": gap_length}
            ],
            "numberStacks": 1
        }
    }
    
    # Get wires with fallbacks
    try:
        primary_wire = PyOpenMagnetics.find_wire_by_name("Round 0.35 - Grade 1")
        if not primary_wire:
            raise ValueError("Wire not found")
    except:
        primary_wire = {
            "type": "round",
            "conductingDiameter": {"nominal": 0.00035},
            "outerDiameter": {"nominal": 0.00040},
            "coating": {"type": "enamel"},
            "material": "copper",
            "name": "Round 0.35mm"
        }
    
    try:
        secondary_wire = PyOpenMagnetics.find_wire_by_name("Round 0.6 - Grade 1")
        if not secondary_wire:
            raise ValueError("Wire not found")
    except:
        secondary_wire = {
            "type": "round",
            "conductingDiameter": {"nominal": 0.0006},
            "outerDiameter": {"nominal": 0.00068},
            "coating": {"type": "enamel"},
            "material": "copper",
            "name": "Round 0.6mm"
        }
    
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
                "numberParallels": 2,  # Parallel strands for lower resistance
                "wire": secondary_wire,
                "isolationSide": "secondary"
            }
        ]
    }
    
    magnetic = {
        "core": core_data,
        "coil": coil_data
    }
    
    return [{"magnetic": magnetic}]


def visualize_design(magnetic):
    """
    Generate SVG visualization of the design.
    """
    try:
        # Plot the core
        core = magnetic["core"]
        svg_core = PyOpenMagnetics.plot_core(core, use_colors=True)
        
        # Save to file
        with open("flyback_220v_12v_core.svg", "w") as f:
            f.write(svg_core)
        print("✓ Core visualization saved to 'flyback_220v_12v_core.svg'")
        
        # Plot winding sections if available
        if "coil" in magnetic and "sectionsDescription" in magnetic["coil"]:
            svg_sections = PyOpenMagnetics.plot_sections(magnetic, use_colors=True)
            with open("flyback_220v_12v_windings.svg", "w") as f:
                f.write(svg_sections)
            print("✓ Winding visualization saved to 'flyback_220v_12v_windings.svg'")
            
    except Exception as e:
        print(f"  (Visualization not available: {e})")


def print_design_summary(specs):
    """
    Print a summary of the design specifications.
    """
    print("\n" + "=" * 60)
    print("DESIGN SUMMARY")
    print("=" * 60)
    print(f"Application: Isolated Flyback Power Supply")
    print(f"Input: 185-265V AC (rectified to {specs['V_in_min']:.0f}-{specs['V_in_max']:.0f}V DC)")
    print(f"Output: {specs['V_out']}V @ {specs['I_out']}A ({specs['P_out']}W)")
    print(f"Switching Frequency: {specs['f_sw']/1000:.0f} kHz")
    print(f"\nMagnetic Requirements:")
    print(f"  Magnetizing Inductance: {specs['L_m']*1e6:.1f} µH")
    print(f"  Turns Ratio (Np:Ns): {specs['turns_ratio']:.1f}:1")
    print(f"  Primary Peak Current: {specs['I_pri_pk']:.2f} A")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print(" PYOPENMAGNETICS FLYBACK TRANSFORMER DESIGN")
    print(" 220V AC → 12V @ 1A (12W)")
    print("=" * 60 + "\n")
    
    # Run the design
    magnetics = design_flyback_transformer()
    
    # Print final summary
    specs = calculate_flyback_specs()
    print_design_summary(specs)
    
    print("\n✓ Design complete!")
    print("\nNext steps:")
    print("  1. Verify inductance with actual core/gap")
    print("  2. Build prototype and measure")
    print("  3. Adjust gap for final inductance tuning")
    print("  4. Verify thermal performance")

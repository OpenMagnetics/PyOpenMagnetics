#!/usr/bin/env python3
"""
PyOpenMagnetics - Converter-Based Magnetic Design Example

Goes from converter specifications to complete magnetic designs in two steps:

1. process_converter(topology, spec) -> MAS Inputs (via the Kirchhoff topology
   designer). design_magnetics_from_converter() is an alias for this step.
2. calculate_advised_magnetics(processed_inputs, n, core_mode) -> ranked designs
   (the MKF magnetic adviser).

Failures raise PyOpenMagnetics.EngineError (v1.7.0+) — there are no error-shaped
return values to check for.

Usage:
    python converter_design_example.py
"""

import PyOpenMagnetics


def describe_designs(designs, inputs, max_designs=3):
    """Print core/winding/loss summary for the top advised designs."""
    models = {
        "coreLosses": "IGSE",
        "reluctance": "ZHANG"
    }

    for i, design in enumerate(designs[:max_designs]):
        mas = design["mas"]
        magnetic = mas["magnetic"]
        core = magnetic["core"]

        shape = core["functionalDescription"]["shape"]
        shape_name = shape["name"] if isinstance(shape, dict) else shape
        material = core["functionalDescription"]["material"]
        material_name = material["name"] if isinstance(material, dict) else material

        print("-" * 60)
        print(f"Design #{i + 1}: {shape_name} / {material_name}")
        print(f"Score: {design['scoring']:.3f}")

        gapping = core["functionalDescription"].get("gapping", [])
        if gapping:
            gap_length = gapping[0].get("length", 0) * 1000
            print(f"Air Gap: {gap_length:.2f} mm")

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

        try:
            losses = PyOpenMagnetics.calculate_core_losses(
                core, magnetic["coil"], inputs, models
            )
            print(f"Core Losses: {losses['coreLosses']:.3f} W")
            print(f"Peak Flux Density: {losses['magneticFluxDensityPeak'] * 1000:.1f} mT")
        except PyOpenMagnetics.EngineError as e:
            print(f"  (Could not calculate losses: {e})")

        print()


def design_flyback_from_converter_spec():
    """Design a flyback transformer starting from converter specifications."""
    print("=" * 70)
    print("FLYBACK DESIGN FROM CONVERTER SPECS")
    print("220V AC → 12V @ 2A (24W)")
    print("=" * 70)

    flyback_specs = {
        "inputVoltage": {
            "minimum": 185,    # V DC bus minimum (low line)
            "maximum": 265     # V DC bus maximum (high line)
        },
        "desiredInductance": 800e-6,     # 800 µH magnetizing inductance
        "desiredTurnsRatios": [13.5],    # Np/Ns for 12V output
        "efficiency": 0.88,
        "operatingPoints": [{
            "outputVoltages": [12.0],     # 12V output
            "outputCurrents": [2.0],      # 2A output
            "switchingFrequency": 100000,  # 100 kHz
            "ambientTemperature": 40
        }]
    }

    print("\n[1] Building MAS Inputs with process_converter('flyback', ...)")
    inputs = PyOpenMagnetics.process_converter("flyback", flyback_specs, use_ngspice=False)
    print(f"    Turns ratios: {inputs['designRequirements']['turnsRatios']}")
    print(f"    Operating points: {len(inputs['operatingPoints'])}")

    print("\n[2] Processing inputs (harmonics + validation)...")
    processed = PyOpenMagnetics.process_inputs(inputs)

    print("\n[3] Running the magnetic adviser (may take 10-30 seconds)...")
    result = PyOpenMagnetics.calculate_advised_magnetics(processed, 3, "standard cores")
    designs = result["data"]
    print(f"\n✓ Found {len(designs)} suitable designs\n")

    describe_designs(designs, processed)
    return designs[0] if designs else None


def design_buck_from_converter_spec():
    """Design a buck output inductor starting from converter specifications."""
    print("\n" + "=" * 70)
    print("BUCK INDUCTOR DESIGN FROM CONVERTER SPECS")
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

    print("\n[1] Building MAS Inputs with process_converter('buck', ...)")
    inputs = PyOpenMagnetics.process_converter("buck", buck_specs, use_ngspice=False)

    print("\n[2] Processing inputs + running the magnetic adviser...")
    processed = PyOpenMagnetics.process_inputs(inputs)
    result = PyOpenMagnetics.calculate_advised_magnetics(processed, 2, "standard cores")
    designs = result["data"]
    print(f"\n✓ Found {len(designs)} suitable designs\n")

    for i, design in enumerate(designs[:2]):
        magnetic = design["mas"]["magnetic"]
        shape = magnetic["core"]["functionalDescription"]["shape"]
        shape_name = shape["name"] if isinstance(shape, dict) else shape
        print(f"Design #{i + 1}: {shape_name}")
        if "coil" in magnetic and "functionalDescription" in magnetic["coil"]:
            winding = magnetic["coil"]["functionalDescription"][0]
            wire = winding.get("wire", "?")
            if isinstance(wire, dict):
                wire = wire.get("name", wire.get("type", "?"))
            print(f"  Turns: {winding.get('numberTurns', '?')}")
            print(f"  Wire: {wire}")
        print()


def compare_topology_processors():
    """The three entry points that build MAS Inputs from a converter spec."""
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

    print("\n[1] process_converter() - generic dispatch:")
    result = PyOpenMagnetics.process_converter("flyback", flyback_specs, use_ngspice=False)
    print(f"    ✓ Has designRequirements: {'designRequirements' in result}")
    print(f"    ✓ Has operatingPoints: {'operatingPoints' in result}")

    print("\n[2] process_flyback() - per-topology wrapper (same result):")
    result = PyOpenMagnetics.process_flyback(flyback_specs)
    print(f"    ✓ Has designRequirements: {'designRequirements' in result}")

    print("\n[3] design_magnetics_from_converter() - alias of the design step:")
    result = PyOpenMagnetics.design_magnetics_from_converter("flyback", flyback_specs)
    print(f"    ✓ Has designRequirements: {'designRequirements' in result}")

    print("\n[4] Errors raise PyOpenMagnetics.EngineError:")
    try:
        PyOpenMagnetics.process_converter("no_such_topology", flyback_specs)
    except PyOpenMagnetics.EngineError as e:
        print(f"    ✓ EngineError: {e}")


def main():
    print("\n" + "=" * 70)
    print(" PYOPENMAGNETICS - CONVERTER-BASED DESIGN EXAMPLES")
    print("=" * 70)

    design_flyback_from_converter_spec()
    design_buck_from_converter_spec()
    compare_topology_processors()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("""
Converter-based design is a two-step pipeline:

1. process_converter(topology, spec) turns converter specifications
   (input/output voltage, current, frequency) into complete MAS Inputs —
   the Kirchhoff topology designer sizes inductance, turns ratios and
   waveforms for you.
2. process_inputs() + calculate_advised_magnetics() turn those Inputs into
   ranked, buildable magnetic designs.

Any failure raises PyOpenMagnetics.EngineError with the engine's message.

For more examples, see:
- AGENTS.md (Converter-Based Design section)
- tests/test_converter_endpoints.py
- llms.txt
""")


if __name__ == "__main__":
    main()

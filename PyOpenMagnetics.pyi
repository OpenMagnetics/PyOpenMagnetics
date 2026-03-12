"""
╔══════════════════════════════════════════════════════════════════════════════╗
║               ⛔  STOP — READ AGENTS.md BEFORE WRITING ANY CODE  ⛔         ║
╚══════════════════════════════════════════════════════════════════════════════╝

This file is a TYPE STUB only. It shows function signatures for autocomplete.
It is NOT a usage guide. The schemas, examples, and argument values shown
here are INCOMPLETE or WRONG in several critical ways.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 MANDATORY FIRST STEP — before writing a single line of code:

  1. Locate AGENTS.md in the same directory as this file.
  2. Read it in full.
  3. Use ONLY the schemas, function calls, and examples from AGENTS.md.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Why AGENTS.md is mandatory (not optional reading):

  ❌ THIS STUB IS WRONG ABOUT:          ✅ AGENTS.md HAS THE TRUTH:
  ─────────────────────────────────     ──────────────────────────────────────
  Keyword argument names                Positional args only (kwargs → TypeError)
  core_mode enum values                 Must be "available cores" (not enum name)
  Flyback JSON field names              Verified field names from C++ source
  Which schema to use when              BASE vs Advanced decision rules
  inputVoltage units                    DC bus voltage, NOT AC RMS
  Method A vs Method B differences      Method A wraps Method B (same schemas)

IF YOU DO NOT READ AGENTS.md AND FOLLOW IT, YOUR CODE WILL FAIL WITH:
  - TypeError: incompatible function arguments
  - RuntimeError: Input JSON does not conform to schema!
  - result["data"] == []  (empty — no designs found)

COMMON MISTAKES THAT CAUSE "Input JSON does not conform to schema!":
  ❌ Using json.dumps() on the converter dict
  ❌ Inventing your own JSON structure (e.g., "inputs"/"outputs" instead of "inputVoltage"/"operatingPoints")
  ❌ Using keyword arguments instead of positional arguments
  → See AGENTS.md Section 13.1 for wrong vs correct code examples

These are the three most common failure modes. All are 100% preventable
by reading AGENTS.md before starting.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 QUICK REMINDER OF THE MOST CRITICAL RULES (full detail in AGENTS.md):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  1. IMPORT — use importlib, NOT bare import:
       import importlib.util, os, glob
       so = glob.glob(os.path.join(<pkg_dir>, 'PyOpenMagnetics.cpython-*'))[0]
       spec = importlib.util.spec_from_file_location('PyOpenMagnetics', so)
       PyOM = importlib.util.module_from_spec(spec)
       spec.loader.exec_module(PyOM)
       PyOM.load_databases({})   # ← ALWAYS call this after loading

  2. CORE MODE — always lowercase with space:
       ✅ "available cores"   ❌ "AVAILABLE_CORES"   ❌ "Available Cores"
       ✅ "standard cores"    ❌ "STANDARD_CORES"    ❌ "Standard Cores"

  3. POSITIONAL ARGS — never keyword args for design functions:
       ✅ PyOM.design_magnetics_from_converter("flyback", conv, 3, "available cores", True, None)
       ❌ PyOM.design_magnetics_from_converter(topology="flyback", ...)

  3b. PASS PYTHON DICTS — NEVER json.dumps()!!! (most common mistake):
       ✅ PyOM.design_magnetics_from_converter("flyback", converter_dict, ...)
       ❌ PyOM.design_magnetics_from_converter("flyback", json.dumps(converter_dict), ...)
       json.dumps() turns your dict into a string → C++ gets a string → schema error.
       See AGENTS.md Section 13.1 for more wrong vs correct examples.

  4. DC BUS VOLTAGE — not AC RMS:
       ✅ inputVoltage minimum = 185 × √2 × 0.9 ≈ 235V
       ❌ inputVoltage minimum = 185  (AC RMS — wrong!)

  5. OFFLINE FLYBACK ≤50W — use Advanced schema with desiredInductance:
       ✅ {"desiredInductance": 600e-6, "desiredTurnsRatios": [13.5], ...}
       ❌ {"currentRippleRatio": 0.4, ...}  (auto-computes L ≈ 10 mH → no results)
       Both Method A and Method B accept the Advanced schema.

  6. operatingPoints[].mode — always set explicitly for flyback:
       ✅ "mode": "Discontinuous Conduction Mode"
       ✅ "mode": "Continuous Conduction Mode"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 READ AGENTS.md NOW. Then use this stub only for autocomplete.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from typing import Dict, List, Any, Optional, Union, Literal

# Type aliases for JSON-like structures
JsonDict = Dict[str, Any]
CoreShape = JsonDict
CoreMaterial = JsonDict
Core = JsonDict
Coil = JsonDict
Wire = JsonDict
Bobbin = JsonDict
Magnetic = JsonDict
Inputs = JsonDict
OperatingPoint = JsonDict
Mas = JsonDict
InsulationMaterial = JsonDict

# Loss model types
CoreLossesModel = Literal["STEINMETZ", "IGSE", "MSE", "BARG", "ROSHEN", "ALBACH", "PROPRIETARY"]
ReluctanceModel = Literal["ZHANG", "MUEHLETHALER", "PARTRIDGE", "EFFECTIVE_AREA", "EFFECTIVE_LENGTH", "STENGLEIN", "BALAKRISHNAN", "CLASSIC"]
TemperatureModel = Literal["MANIKTALA", "KAZIMIERCZUK", "TDK"]
GappingType = Literal["SUBTRACTIVE", "ADDITIVE", "DISTRIBUTED"]
WireType = Literal["round", "litz", "rectangular", "foil"]

ModelsDict = Dict[str, str]

# =============================================================================
# DATABASE ACCESS - Core Shapes
# =============================================================================

def get_core_shapes() -> List[CoreShape]:
    """Get all available core shapes from the database.
    
    Returns:
        List of core shape dictionaries with geometry data.
    """
    ...

def get_core_shape_names(include_toroidal: bool = True) -> List[str]:
    """Get names of all core shapes.
    
    Args:
        include_toroidal: If True, include toroidal core shapes.
        
    Returns:
        List of shape name strings (e.g., "E 42/21/15", "ETD 49/25/16").
    """
    ...

def get_core_shape_families() -> List[str]:
    """Get all core shape family names.

    ⚠️ Takes NO arguments — get_core_shape_families(True) raises TypeError.

    Returns:
        List of family names (e.g., "E", "ETD", "PQ", "RM", "T").
    """
    ...

def find_core_shape_by_name(name: str) -> CoreShape:
    """Find a specific core shape by its name.
    
    Args:
        name: Exact shape name (e.g., "E 42/21/15").
        
    Returns:
        Core shape dictionary with full geometry.
    """
    ...

# =============================================================================
# DATABASE ACCESS - Core Materials
# =============================================================================

def get_core_materials() -> List[CoreMaterial]:
    """Get all available core materials from the database.
    
    Returns:
        List of core material dictionaries with magnetic properties.
    """
    ...

def get_core_material_names() -> List[str]:
    """Get names of all core materials.
    
    Returns:
        List of material name strings (e.g., "3C95", "N87").
    """
    ...

def get_core_material_names_by_manufacturer(manufacturer: str) -> List[str]:
    """Get material names filtered by manufacturer.
    
    Args:
        manufacturer: Manufacturer name (e.g., "Ferroxcube", "TDK", "Magnetics").
        
    Returns:
        List of material names from that manufacturer.
    """
    ...

def find_core_material_by_name(name: str) -> CoreMaterial:
    """Find a specific core material by its name.
    
    Args:
        name: Material name (e.g., "3C95", "N87").
        
    Returns:
        Core material dictionary with magnetic properties.
    """
    ...

def get_material_permeability(material_name: str, temperature: float, dc_bias: float, frequency: float) -> float:
    """Get relative permeability at operating conditions.
    
    Args:
        material_name: Material name string.
        temperature: Temperature in Celsius.
        dc_bias: DC bias field in A/m.
        frequency: Operating frequency in Hz.
        
    Returns:
        Relative permeability (dimensionless).
    """
    ...

def get_material_resistivity(material_name: str, temperature: float) -> float:
    """Get electrical resistivity at temperature.
    
    Args:
        material_name: Material name string.
        temperature: Temperature in Celsius.
        
    Returns:
        Resistivity in Ohm·m.
    """
    ...

def get_core_material_steinmetz_coefficients(material: Union[str, CoreMaterial], frequency: float) -> JsonDict:
    """Get Steinmetz equation coefficients for core loss calculation.
    
    Args:
        material: Material name or full material dict.
        frequency: Operating frequency in Hz.
        
    Returns:
        Dict with keys: k, alpha, beta, minimumFrequency, maximumFrequency, ct0, ct1, ct2.
    """
    ...

# =============================================================================
# DATABASE ACCESS - Wires
# =============================================================================

def get_wires() -> List[Wire]:
    """Get all available wires from the database."""
    ...

def get_wire_names() -> List[str]:
    """Get names of all wires."""
    ...

def find_wire_by_name(name: str) -> Wire:
    """Find a specific wire by its name.
    
    Args:
        name: Wire name (e.g., "Round 0.5 - Grade 1").
    """
    ...

def find_wire_by_dimension(dimension: float, wire_type: WireType, standard: str) -> Wire:
    """Find wire closest to specified dimension.
    
    Args:
        dimension: Conducting diameter/width in meters.
        wire_type: "round", "litz", "rectangular", or "foil".
        standard: Wire standard (e.g., "IEC 60317", "NEMA MW 1000").
    """
    ...

def get_available_wire_types() -> List[str]:
    """Get list of available wire types."""
    ...

def get_available_wire_standards() -> List[str]:
    """Get list of available wire standards."""
    ...

def get_wire_outer_diameter_enamelled_round(wire: Wire) -> float:
    """Get outer diameter for round enamelled wire in meters."""
    ...

def get_wire_outer_diameter_served_litz(wire: Wire) -> float:
    """Get outer diameter for served litz wire in meters."""
    ...

def get_wire_outer_diameter_insulated_round(wire: Wire) -> float:
    """Get outer diameter for insulated round wire in meters."""
    ...

def get_outer_dimensions(wire: Wire) -> JsonDict:
    """Get outer dimensions for any wire type."""
    ...

def get_coating(wire: Wire) -> JsonDict:
    """Get coating/insulation data for wire."""
    ...

# =============================================================================
# DATABASE ACCESS - Bobbins
# =============================================================================

def get_bobbins() -> List[Bobbin]:
    """Get all available bobbins from the database."""
    ...

def find_bobbin_by_name(name: str) -> Bobbin:
    """Find a specific bobbin by its name."""
    ...

# =============================================================================
# DATABASE ACCESS - Insulation Materials
# =============================================================================

def get_insulation_materials() -> List[InsulationMaterial]:
    """Get all available insulation materials."""
    ...

def find_insulation_material_by_name(name: str) -> InsulationMaterial:
    """Find insulation material by name (e.g., "Kapton", "Nomex")."""
    ...

# =============================================================================
# CORE CALCULATIONS
# =============================================================================

def calculate_core_data(core: Core, include_material_data: bool = False) -> Core:
    """Calculate complete core data from functional description.
    
    Adds processedDescription (effective parameters) and geometricalDescription.
    
    Args:
        core: Core with functionalDescription.
        include_material_data: If True, embed full material data.
        
    Returns:
        Complete core dict with all descriptions populated.
    """
    ...

def get_core_temperature_dependant_parameters(core: Core, temperature: float) -> JsonDict:
    """Get core parameters at specific temperature.
    
    Returns:
        Dict with: magneticFluxDensitySaturation, initialPermeability,
        effectivePermeability, reluctance, permeance, resistivity.
    """
    ...

def calculate_core_maximum_magnetic_energy(core: Core, operating_point: OperatingPoint) -> float:
    """Calculate maximum magnetic energy storage in Joules."""
    ...

def calculate_saturation_current(magnetic: Magnetic, temperature: float = 25.0) -> float:
    """Calculate saturation current for complete magnetic assembly in Amperes."""
    ...

# =============================================================================
# INDUCTANCE CALCULATIONS
# =============================================================================

def calculate_inductance_from_number_turns_and_gapping(
    core: Core, 
    coil: Coil, 
    operating_point: OperatingPoint, 
    models: ModelsDict
) -> float:
    """Calculate inductance from turns count and gap configuration.
    
    Args:
        core: Core with gapping defined.
        coil: Coil with winding turns.
        operating_point: Operating conditions.
        models: Dict with "reluctance" model name.
        
    Returns:
        Inductance in Henries.
    """
    ...

def calculate_number_turns_from_gapping_and_inductance(
    core: Core, 
    inputs: Inputs, 
    models: ModelsDict
) -> int:
    """Calculate required turns for target inductance with given gap."""
    ...

def calculate_gapping_from_number_turns_and_inductance(
    core: Core,
    coil: Coil,
    inputs: Inputs,
    gapping_type: GappingType,
    decimals: int,
    models: ModelsDict
) -> Core:
    """Calculate gap length for target inductance with given turns.
    
    Returns:
        Core with gapping array populated.
    """
    ...

def calculate_gap_reluctance(gap: JsonDict, model: ReluctanceModel) -> JsonDict:
    """Calculate reluctance and fringing factor for a gap.
    
    Returns:
        Dict with: reluctance (H⁻¹), fringingFactor.
    """
    ...

# =============================================================================
# LOSS CALCULATIONS
# =============================================================================

def calculate_core_losses(
    core: Core, 
    coil: Coil, 
    inputs: Inputs, 
    models: ModelsDict
) -> JsonDict:
    """Calculate core losses for operating conditions.
    
    Args:
        models: Dict with "coreLosses", "reluctance", "coreTemperature" keys.
        
    Returns:
        Dict with: coreLosses (W), magneticFluxDensityPeak (T),
        magneticFluxDensityAcPeak (T), voltageRms (V), currentRms (A),
        apparentPower (VA), maximumCoreTemperature (°C),
        maximumCoreTemperatureRise (K).
    """
    ...

def calculate_winding_losses(
    magnetic: Magnetic, 
    operating_point: OperatingPoint, 
    temperature: float = 25.0
) -> JsonDict:
    """Calculate total winding losses (DC + AC).
    
    Returns:
        Dict with: windingLosses (W), windingLossesPerWinding (list),
        ohmicLosses, skinEffectLosses, proximityEffectLosses.
    """
    ...

def calculate_ohmic_losses(coil: Coil, operating_point: OperatingPoint, temperature: float) -> JsonDict:
    """Calculate DC ohmic losses only."""
    ...

def calculate_skin_effect_losses(coil: Coil, winding_losses: JsonDict, temperature: float) -> JsonDict:
    """Calculate skin effect AC losses."""
    ...

def calculate_proximity_effect_losses(
    coil: Coil, 
    temperature: float, 
    winding_losses: JsonDict, 
    field: JsonDict
) -> JsonDict:
    """Calculate proximity effect AC losses."""
    ...

def calculate_magnetic_field_strength_field(operating_point: OperatingPoint, magnetic: Magnetic) -> JsonDict:
    """Calculate magnetic field distribution in winding window."""
    ...

def calculate_dc_resistance_per_meter(wire: Wire, temperature: float) -> float:
    """DC resistance per meter in Ohm/m."""
    ...

def calculate_dc_losses_per_meter(wire: Wire, current: JsonDict, temperature: float) -> float:
    """DC losses per meter in W/m."""
    ...

def calculate_skin_ac_losses_per_meter(wire: Wire, current: JsonDict, temperature: float) -> float:
    """Skin effect AC losses per meter in W/m."""
    ...

def calculate_skin_ac_resistance_per_meter(wire: Wire, current: JsonDict, temperature: float) -> float:
    """Skin effect AC resistance per meter in Ohm/m."""
    ...

def calculate_skin_ac_factor(wire: Wire, current: JsonDict, temperature: float) -> float:
    """AC resistance factor (Rac/Rdc)."""
    ...

def calculate_effective_current_density(wire: Wire, current: JsonDict, temperature: float) -> float:
    """Effective current density in A/m²."""
    ...

def calculate_effective_skin_depth(material: str, current: JsonDict, temperature: float) -> float:
    """Skin depth in meters."""
    ...

def get_core_losses_model_information(material: CoreMaterial) -> JsonDict:
    """Get available loss models and data for material."""
    ...

# =============================================================================
# WINDING ENGINE
# =============================================================================

def wind(
    coil: Coil,
    repetitions: int = 1,
    proportion_per_winding: Optional[List[float]] = None,
    pattern: Optional[List[int]] = None,
    margin_pairs: Optional[List[List[float]]] = None
) -> Coil:
    """Wind coil placing turns in winding window.
    
    Args:
        coil: Coil with functionalDescription (turns, wire, parallels).
        repetitions: Number of times to repeat winding pattern.
        proportion_per_winding: Window share for each winding [0-1].
        pattern: Interleaving pattern, e.g., [0, 1] for P-S-P-S.
        margin_pairs: [[left, right], ...] margin tape per winding in meters.
        
    Returns:
        Coil with sectionsDescription, layersDescription, turnsDescription.
    """
    ...

def wind_by_sections(
    coil: Coil,
    repetitions: int,
    proportions: List[float],
    pattern: List[int],
    insulation_thickness: float
) -> Coil:
    """Wind with section-level control."""
    ...

def wind_by_layers(
    coil: Coil,
    insulation_layers: int,
    insulation_thickness: float
) -> Coil:
    """Wind with layer-level control."""
    ...

def wind_by_turns(coil: Coil) -> Coil:
    """Wind with turn-level precision."""
    ...

def wind_planar(
    coil: Coil,
    stack_up: List[JsonDict],
    border_distance: float,
    wire_spacing: float,
    insulation: JsonDict,
    core_distance: float
) -> Coil:
    """Wind planar (PCB) coil."""
    ...

def are_sections_and_layers_fitting(coil: Coil) -> bool:
    """Check if winding fits in available window."""
    ...

def get_layers_by_winding_index(coil: Coil, winding_index: int) -> List[JsonDict]:
    """Get layers belonging to specific winding."""
    ...

# =============================================================================
# DESIGN ADVISER
# =============================================================================

def process_inputs(inputs: Inputs) -> Inputs:
    """Process inputs adding harmonics and processed data.
    
    REQUIRED before calling adviser functions.
    """
    ...

def calculate_advised_cores(
    inputs: Inputs,
    weights: Dict[str, float],
    max_results: int = 10,
    core_mode: str = "available cores"
) -> List[JsonDict]:
    """Get recommended cores for design requirements.
    
    ⚠️ core_mode MUST be lowercase with space: "available cores" or "standard cores"
       Passing "AVAILABLE_CORES" or "STANDARD_CORES" throws RuntimeError.
    ⚠️ Use POSITIONAL arguments — keyword names in this stub may be wrong.
    
    Args:
        inputs: Processed inputs (from process_inputs).
        weights: {"EFFICIENCY": 1.0, "DIMENSIONS": 0.5, "COST": 0.3}.
        max_results: Maximum number of recommendations.
        core_mode: "available cores" or "standard cores" (lowercase with space!).
        
    Returns:
        JSON object with "data" array containing ranked results.
        Each result has:
        - "mas": Mas object with magnetic, inputs, and optionally outputs
        - "scoring": Overall float score
        - "scoringPerFilter": Object with individual scores per filter
    """
    ...

def calculate_advised_magnetics(
    inputs: Inputs,
    max_results: int = 5,
    core_mode: str = "available cores"
) -> JsonDict:
    """Get complete magnetic designs (core + winding).
    
    ⚠️ core_mode MUST be lowercase with space: "available cores" or "standard cores"
       Passing "AVAILABLE_CORES" or "STANDARD_CORES" throws RuntimeError.
    ⚠️ Use POSITIONAL arguments — keyword names in this stub may be wrong.
    
    Args:
        inputs: Processed inputs dict with "designRequirements" and "operatingPoints".
        max_results: Maximum number of recommendations.
        core_mode: "available cores" or "standard cores" (lowercase with space!).
    
    Returns:
        JSON object with "data" array containing ranked results.
        Each result has:
        - "mas": Mas object with magnetic, inputs, and optionally outputs
        - "scoring": Overall float score
        - "scoringPerFilter": Object with individual scores per filter

    Example (CORRECT — positional args, lowercase core_mode):
        >>> result = PyOM.calculate_advised_magnetics(mas_inputs, 3, "available cores")
        >>> for item in result["data"]:
        ...     mag = item["mas"]["magnetic"]
        ...     print(mag["core"]["functionalDescription"]["shape"]["name"])

    Example (WRONG — do not do this):
        >>> result = PyOM.calculate_advised_magnetics(inputs, 5, "STANDARD_CORES")  # throws!
        >>> result = PyOM.calculate_advised_magnetics(inputs=inputs, core_mode="available cores")  # wrong kwargs
    """
    ...

def calculate_advised_magnetics_from_catalog(
    inputs: Inputs,
    catalog: List[Magnetic],
    max_results: int = 5
) -> JsonDict:
    """Get designs from custom catalog of magnetics.
    
    Returns:
        JSON object with "data" array containing ranked results.
        Each result has:
        - "mas": Mas object with magnetic data
        - "scoring": Overall float score
        - "scoringPerFilter": Object with individual scores per filter
    """
    ...

# =============================================================================
# SIMULATION
# =============================================================================

def simulate(inputs: Inputs, magnetic: Magnetic, models: ModelsDict) -> Mas:
    """Run complete simulation.
    
    Returns:
        Mas object with outputs (losses, temperatures, etc.).
    """
    ...

def magnetic_autocomplete(magnetic: Magnetic, config: JsonDict) -> Magnetic:
    """Autocomplete partial magnetic specification."""
    ...

def mas_autocomplete(mas: Mas, config: JsonDict) -> Mas:
    """Autocomplete partial Mas specification."""
    ...

def extract_operating_point(
    spice_file: JsonDict,
    num_windings: int,
    frequency: float,
    target_inductance: float,
    column_mapping: List[Dict[str, str]]
) -> OperatingPoint:
    """Extract operating point from SPICE simulation results."""
    ...

def export_magnetic_as_subcircuit(magnetic: Magnetic) -> str:
    """Export magnetic as SPICE subcircuit string."""
    ...

# =============================================================================
# INSULATION
# =============================================================================

def calculate_insulation(inputs: Inputs) -> JsonDict:
    """Calculate safety distances per IEC standards.
    
    Returns:
        Dict with: creepageDistance (m), clearance (m),
        withstandVoltage (V), distanceThroughInsulation (m), errorMessage.
    """
    ...

# =============================================================================
# VISUALIZATION
# =============================================================================

def plot_core(core: Core, use_colors: bool = True) -> str:
    """Generate SVG visualization of core.
    
    Returns:
        SVG string.
    """
    ...

def plot_core_2d(
    core: Core, 
    axis: int = 1, 
    winding_windows: Optional[JsonDict] = None,
    use_colors: bool = True
) -> str:
    """Generate 2D cross-section SVG of core."""
    ...

def plot_coil_2d(
    coil: Coil,
    axis: int = 1,
    mirrored: bool = True,
    use_colors: bool = True
) -> str:
    """Generate 2D cross-section SVG of coil."""
    ...

def plot_field_2d(
    magnetic: Magnetic,
    operating_point: OperatingPoint,
    axis: int = 1,
    use_colors: bool = True
) -> str:
    """Generate 2D magnetic field visualization."""
    ...

def plot_field_map(
    magnetic: Magnetic,
    operating_point: OperatingPoint,
    axis: int = 1
) -> str:
    """Generate magnetic field heat map."""
    ...

def plot_wire(wire: Wire, use_colors: bool = True) -> str:
    """Generate SVG of wire cross-section."""
    ...

def plot_bobbin(bobbin: Bobbin, use_colors: bool = True) -> str:
    """Generate SVG of bobbin."""
    ...

# =============================================================================
# SETTINGS
# =============================================================================

def get_settings() -> JsonDict:
    """Get current library settings."""
    ...

def set_settings(settings: JsonDict) -> None:
    """Update library settings."""
    ...

def reset_settings() -> None:
    """Reset settings to defaults."""
    ...

def get_constants() -> JsonDict:
    """Get physical constants (vacuumPermeability, etc.)."""
    ...

def get_default_models() -> JsonDict:
    """Get default model selections."""
    ...

# =============================================================================
# CONVERTER TOPOLOGY PROCESSORS
# =============================================================================

def process_converter(topology: str, converter: JsonDict, use_ngspice: bool = True) -> JsonDict:
    """Process a converter topology specification to designRequirements + operatingPoints.
    
    Generic endpoint that dispatches to the appropriate topology processor.
    Accepts BOTH the BASE Flyback schema and the Advanced Flyback schema
    (with desiredInductance, desiredTurnsRatios, desiredDutyCycle).
    
    ⚠️ inputVoltage values MUST be DC bus voltage, NOT AC RMS.
       Convert: Vdc_min = Vac_min × √2 × holdup,  Vdc_max = Vac_max × √2
    
    Args:
        topology: Topology name — use LOWERCASE:
                  "flyback", "buck", "boost", "single_switch_forward",
                  "two_switch_forward", "active_clamp_forward", "push_pull",
                  "llc", "cllc", "dab", "phase_shifted_full_bridge",
                  "phase_shifted_half_bridge", "isolated_buck",
                  "isolated_buck_boost", "current_transformer"
        converter: JSON object — see AGENTS.md Section 5 for verified schemas.
                   DO NOT invent fields. Use exactly the schemas in AGENTS.md.
        use_ngspice: If True, uses ngspice simulation (bundled in wheel).
    
    Returns:
        {"designRequirements": {...}, "operatingPoints": [...]}
        On error: {"error": "..."}

    Example (Advanced Flyback — offline ≤50W):
        >>> processed = PyOM.process_converter("flyback", {
        ...     "inputVoltage": {"minimum": 235.0, "maximum": 375.0},  # DC bus!
        ...     "desiredInductance": 600e-6,
        ...     "desiredTurnsRatios": [13.5],
        ...     "desiredDutyCycle": [[0.45, 0.45]],
        ...     "maximumDutyCycle": 0.45,
        ...     "efficiency": 0.88,
        ...     "diodeVoltageDrop": 0.5,
        ...     "currentRippleRatio": 0.4,
        ...     "operatingPoints": [{
        ...         "outputVoltages": [12.0],
        ...         "outputCurrents": [2.0],
        ...         "switchingFrequency": 100000.0,
        ...         "ambientTemperature": 25.0,
        ...         "mode": "Discontinuous Conduction Mode"
        ...     }]
        ... }, use_ngspice=False)
        >>> processed["designRequirements"]["magnetizingInductance"]["nominal"]
        0.0006   # exactly matches desiredInductance
    """
    ...


def design_magnetics_from_converter(
    topology: str,
    converter: JsonDict,
    max_results: int = 1,
    core_mode: str = "available cores",
    use_ngspice: bool = True,
    weights: Optional[Dict[str, float]] = None
) -> JsonDict:
    """Design magnetic components from a converter specification.
    
    High-level endpoint: converter spec → ranked magnetic designs.
    Wraps process_converter() + calculate_advised_magnetics() internally.
    Accepts BOTH BASE and Advanced Flyback schemas (same as process_converter).
    
    ⚠️⚠️ USE POSITIONAL ARGUMENTS ONLY ⚠️⚠️
       The keyword names shown here DO NOT match the actual C++ pybind11 bindings.
       Calling with kwargs will raise:
         TypeError: design_magnetics_from_converter(): incompatible function arguments
    
    ⚠️ core_mode MUST be lowercase with space.
       "AVAILABLE_CORES" → RuntimeError. "available cores" → works.
    
    ⚠️ inputVoltage in converter MUST be DC bus voltage, NOT AC RMS.
    
    ✅ CORRECT call:
        result = PyOM.design_magnetics_from_converter(
            "flyback",        # positional 1: topology (lowercase)
            converter_dict,   # positional 2: converter JSON (see AGENTS.md §5)
            3,                # positional 3: max_results (int!)
            "available cores",# positional 4: core_mode (lowercase with space!)
            True,             # positional 5: use_ngspice
            None              # positional 6: weights (None or dict)
        )
    
    ❌ WRONG calls:
        PyOM.design_magnetics_from_converter(topology="flyback", ...)  # wrong kwargs → TypeError
        PyOM.design_magnetics_from_converter("flyback", c, 3, "AVAILABLE_CORES", ...)  # wrong mode → RuntimeError
        PyOM.design_magnetics_from_converter("flyback", c, 3.0, ...)   # float not int → TypeError
        PyOM.design_magnetics_from_converter("flyback", json.dumps(c), ...)  # json.dumps → schema error!
        PyOM.design_magnetics_from_converter("flyback", c, 3, json.dumps("standard cores"), ...)  # also wrong
    
    Args:
        topology: Topology name (lowercase). See process_converter for full list.
        converter: JSON object with converter specification. See AGENTS.md Section 5.
                   DO NOT invent fields — use only the schemas in AGENTS.md.
        max_results: Maximum number of magnetic designs to return (must be int).
        core_mode: "available cores" or "standard cores" (lowercase with space).
                   "available cores" searches 1300+ shapes (slower, ~60-120s).
                   "standard cores" searches generic shapes (faster).
        use_ngspice: ngspice is bundled in the wheel — no system install needed.
        weights: Optional scoring weights. None = defaults.
                 Keys: "maximizeEfficiency", "minimizeCost", "minimizeDimensions", etc.
                 See AGENTS.md Section 7 for verified weight key names.
    
    Returns:
        {"data": [{"mas": {...}, "scoring": float, "scoringPerFilter": {...}}, ...]}
        Access pattern: result["data"][0]["mas"]["magnetic"]["core"]["functionalDescription"]
    
    Example (≤50W offline flyback — Advanced schema):
        >>> import math
        >>> Vdc_min = round(185 * math.sqrt(2) * 0.9, 1)   # 235V DC bus
        >>> Vdc_max = round(265 * math.sqrt(2), 1)          # 375V DC bus
        >>> result = PyOM.design_magnetics_from_converter(
        ...     "flyback",
        ...     {
        ...         "inputVoltage": {"minimum": Vdc_min, "maximum": Vdc_max},
        ...         "desiredInductance": 600e-6,
        ...         "desiredTurnsRatios": [13.5],
        ...         "desiredDutyCycle": [[0.45, 0.45]],
        ...         "maximumDutyCycle": 0.45,
        ...         "efficiency": 0.88,
        ...         "diodeVoltageDrop": 0.5,
        ...         "currentRippleRatio": 0.4,
        ...         "operatingPoints": [{
        ...             "outputVoltages": [12.0],
        ...             "outputCurrents": [2.0],
        ...             "switchingFrequency": 100000.0,
        ...             "ambientTemperature": 25.0,
        ...             "mode": "Discontinuous Conduction Mode"
        ...         }]
        ...     },
        ...     3,                 # max_results — int!
        ...     "available cores", # lowercase with space!
        ...     True,
        ...     None
        ... )
        >>> designs = result["data"]
        >>> print(f"Found {len(designs)} designs")
    """
    ...


def process_flyback(flyback: JsonDict) -> Inputs:
    """Process Flyback converter specification to Inputs.
    ⚠️ See AGENTS.md Section 5 for the correct JSON schema.
    """
    ...

def process_buck(buck: JsonDict) -> Inputs:
    """Process Buck converter specification to Inputs."""
    ...

def process_boost(boost: JsonDict) -> Inputs:
    """Process Boost converter specification to Inputs."""
    ...

def process_single_switch_forward(forward: JsonDict) -> Inputs:
    """Process Single-Switch Forward converter to Inputs."""
    ...

def process_two_switch_forward(forward: JsonDict) -> Inputs:
    """Process Two-Switch Forward converter to Inputs."""
    ...

def process_active_clamp_forward(forward: JsonDict) -> Inputs:
    """Process Active Clamp Forward converter to Inputs."""
    ...

def process_push_pull(push_pull: JsonDict) -> Inputs:
    """Process Push-Pull converter specification to Inputs."""
    ...

def process_isolated_buck(isolated_buck: JsonDict) -> Inputs:
    """Process Isolated Buck converter to Inputs."""
    ...

def process_isolated_buck_boost(isolated_buck_boost: JsonDict) -> Inputs:
    """Process Isolated Buck-Boost converter to Inputs."""
    ...

def process_current_transformer(ct: JsonDict, turns_ratio: float, secondary_resistance: float = 0.0) -> Inputs:
    """Process Current Transformer specification to Inputs."""
    ...

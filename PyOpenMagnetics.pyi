"""
PyOpenMagnetics Type Stubs

This file provides type hints for the PyOpenMagnetics C++ extension module.
It enables IDE autocompletion and type checking for PyOpenMagnetics.

See llms.txt for comprehensive API documentation and examples.
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

# Wire-level loss calculations
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
    core_mode: str = "STANDARD_CORES"
) -> List[JsonDict]:
    """Get recommended cores for design requirements.
    
    Args:
        inputs: Processed inputs (from process_inputs).
        weights: {"EFFICIENCY": 1.0, "DIMENSIONS": 0.5, "COST": 0.3}.
        max_results: Maximum number of recommendations.
        core_mode: "STANDARD_CORES" or "AVAILABLE_CORES" (stock only).
    """
    ...

def calculate_advised_magnetics(
    inputs: Inputs,
    max_results: int = 5,
    core_mode: str = "STANDARD_CORES"
) -> List[Mas]:
    """Get complete magnetic designs (core + winding).
    
    Returns:
        List of Mas objects with magnetic and outputs populated.
    """
    ...

def calculate_advised_magnetics_from_catalog(
    inputs: Inputs,
    catalog: List[Magnetic],
    max_results: int = 5
) -> List[Mas]:
    """Get designs from custom catalog of magnetics."""
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

def process_flyback(flyback: JsonDict) -> Inputs:
    """Process Flyback converter specification to Inputs."""
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

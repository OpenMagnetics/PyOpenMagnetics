"""
Simplified MCP Tools for PyOpenMagnetics.

Two main tools:
1. design_magnetic - Design any magnetic component
2. query_database - Query cores, materials, wires
"""

# =============================================================================
# Predefined templates for common designs (works offline)
# =============================================================================

DESIGN_TEMPLATES = {
    "usb_pd_20w": {
        "description": "USB PD 20W charger (5V/9V/12V @ 20W)",
        "topology": "flyback",
        "vin_ac": [85, 265],
        "outputs": [{"voltage": 12, "current": 1.67}],
        "frequency_hz": 100000
    },
    "usb_pd_65w": {
        "description": "USB PD 65W laptop charger",
        "topology": "flyback",
        "vin_ac": [85, 265],
        "outputs": [{"voltage": 20, "current": 3.25}],
        "frequency_hz": 100000
    },
    "buck_5v_3a": {
        "description": "5V 3A DC-DC buck from 12V",
        "topology": "buck",
        "vin": [10, 14],
        "outputs": [{"voltage": 5, "current": 3}],
        "frequency_hz": 500000
    },
    "buck_3v3_2a": {
        "description": "3.3V 2A DC-DC buck from 5V",
        "topology": "buck",
        "vin": [4.5, 5.5],
        "outputs": [{"voltage": 3.3, "current": 2}],
        "frequency_hz": 1000000
    },
    "boost_5v_1a": {
        "description": "5V 1A boost from Li-Ion battery",
        "topology": "boost",
        "vin": [3.0, 4.2],
        "outputs": [{"voltage": 5, "current": 1}],
        "frequency_hz": 1000000
    },
    "led_driver_12v": {
        "description": "12V LED driver from 24V",
        "topology": "buck",
        "vin": [20, 28],
        "outputs": [{"voltage": 12, "current": 1}],
        "frequency_hz": 200000
    },
    "poe_12v_1a": {
        "description": "PoE 12V 1A isolated supply",
        "topology": "flyback",
        "vin_dc": [36, 57],
        "outputs": [{"voltage": 12, "current": 1}],
        "frequency_hz": 200000
    },
    "filter_100uh": {
        "description": "100uH filter inductor @ 5A",
        "topology": "inductor",
        "inductance": 100e-6,
        "current_dc": 5,
        "current_ac_pp": 0.5,
        "frequency_hz": 100000
    }
}


def get_templates() -> dict:
    """Get all available design templates."""
    return {k: v["description"] for k, v in DESIGN_TEMPLATES.items()}


def design_from_template(template_name: str, max_results: int = 3) -> dict:
    """Design magnetic from predefined template."""
    if template_name not in DESIGN_TEMPLATES:
        return {"error": f"Unknown template: {template_name}", "available": list(DESIGN_TEMPLATES.keys())}

    t = DESIGN_TEMPLATES[template_name]

    if t["topology"] == "inductor":
        return design_magnetic(topology="inductor", inductance=t["inductance"], current_dc=t["current_dc"],
                               current_ac_pp=t["current_ac_pp"], frequency_hz=t["frequency_hz"], max_results=max_results)
    elif "vin_ac" in t:
        return design_magnetic(topology=t["topology"], vin_min=t["vin_ac"][0], vin_max=t["vin_ac"][1],
                               vin_is_ac=True, outputs=t["outputs"], frequency_hz=t["frequency_hz"], max_results=max_results)
    else:
        vin = t.get("vin") or t.get("vin_dc")
        return design_magnetic(topology=t["topology"], vin_min=vin[0], vin_max=vin[1], vin_is_ac=False,
                               outputs=t["outputs"], frequency_hz=t["frequency_hz"], max_results=max_results)


# =============================================================================
# Main design tool
# =============================================================================

def design_magnetic(
    topology: str,
    vin_min: float = 0,
    vin_max: float = 0,
    vin_is_ac: bool = False,
    outputs: list[dict] = None,
    frequency_hz: float = 100000,
    inductance: float = None,
    current_dc: float = 0,
    current_ac_pp: float = 0,
    max_results: int = 3
) -> dict:
    """Design a magnetic component."""
    from ..design import Design

    try:
        topo = topology.lower()
        outputs = outputs or []

        if topo == "flyback":
            b = Design.flyback()
            if vin_is_ac:
                b.vin_ac(vin_min, vin_max)
            else:
                b.vin_dc(vin_min, vin_max)
            for o in outputs:
                b.output(o["voltage"], o["current"])
            b.fsw(frequency_hz)

        elif topo == "buck":
            b = Design.buck()
            b.vin(vin_min, vin_max)
            if outputs:
                b.vout(outputs[0]["voltage"]).iout(outputs[0]["current"])
            b.fsw(frequency_hz)

        elif topo == "boost":
            b = Design.boost()
            b.vin(vin_min, vin_max)
            if outputs:
                b.vout(outputs[0]["voltage"])
                b.pout(outputs[0]["voltage"] * outputs[0]["current"])
            b.fsw(frequency_hz)

        elif topo == "forward":
            b = Design.forward()
            b.vin_dc(vin_min, vin_max)
            for o in outputs:
                b.output(o["voltage"], o["current"])
            b.fsw(frequency_hz)

        elif topo == "llc":
            b = Design.llc()
            b.vin_dc(vin_min, vin_max)
            for o in outputs:
                b.output(o["voltage"], o["current"])
            b.resonant_frequency(frequency_hz)

        elif topo == "inductor":
            b = Design.inductor()
            if inductance:
                b.inductance(inductance)
            b.idc(current_dc).iac_pp(current_ac_pp or current_dc * 0.1)
            b.fsw(frequency_hz)

        else:
            return {"error": f"Unknown topology: {topology}"}

        params = b.get_calculated_parameters()
        results = b.solve(max_results=max_results)

        designs = []
        for r in results:
            designs.append({
                "core": r.core,
                "material": r.material,
                "gap_mm": round(r.air_gap_mm, 2),
                "turns": r.primary_turns,
                "wire": r.primary_wire,
                "loss_w": round(r.total_loss_w, 3)
            })

        return {"designs": designs, "parameters": params}

    except Exception as e:
        return {"error": str(e)}


# =============================================================================
# Database query tool
# =============================================================================

def query_database(
    query_type: str,
    name: str = None,
    family: str = None,
    manufacturer: str = None
) -> dict:
    """Query the component database."""
    import PyOpenMagnetics as PM

    try:
        if query_type == "shapes":
            shapes = PM.get_core_shape_names(True)
            if family:
                shapes = [s for s in shapes if s.upper().startswith(family.upper())]
            return {"shapes": shapes[:50], "total": len(shapes)}

        elif query_type == "materials":
            if manufacturer:
                mats = PM.get_core_material_names_by_manufacturer(manufacturer)
            else:
                mats = PM.get_core_material_names()
            return {"materials": mats, "count": len(mats)}

        elif query_type == "wires":
            return {"wire_types": PM.get_available_wire_types()}

        elif query_type == "shape_info" and name:
            shape = PM.find_core_shape_by_name(name)
            if isinstance(shape, dict):
                fd = shape.get("functionalDescription", {})
                return {"name": name, "family": fd.get("family"), "type": fd.get("type")}
            return {"error": "Shape not found"}

        elif query_type == "material_info" and name:
            mu = PM.get_material_permeability(name, 25, 0, 100000)
            steinmetz = PM.get_core_material_steinmetz_coefficients(PM.find_core_material_by_name(name), 100000)
            return {
                "name": name,
                "permeability_100kHz": mu,
                "steinmetz": {"k": steinmetz.get("k"), "alpha": steinmetz.get("alpha"),
                              "beta": steinmetz.get("beta")} if isinstance(steinmetz, dict) else None
            }

        elif query_type == "families":
            return {"families": PM.get_core_shape_families()}

        else:
            return {"error": f"Unknown query: {query_type}. Use: shapes, materials, wires, shape_info, material_info, families"}

    except Exception as e:
        return {"error": str(e)}

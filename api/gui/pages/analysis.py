"""
Analysis Page - Analyze existing magnetic designs.
"""

import streamlit as st
import PyOpenMagnetics as PM


def render():
    st.title("Design Analysis")
    st.write("Analyze an existing magnetic component design.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Core")
        # Core shape selection
        families = PM.get_core_shape_families()
        family = st.selectbox("Family", families, index=families.index("E") if "E" in families else 0)

        all_shapes = PM.get_core_shape_names(True)
        shapes = [s for s in all_shapes if s.upper().startswith(family.upper())]
        core_shape = st.selectbox("Shape", shapes[:50] if shapes else ["No shapes"])

        # Material selection
        materials = PM.get_core_material_names()[:30]
        core_material = st.selectbox("Material", materials)

        # Gap
        air_gap_mm = st.number_input("Air Gap (mm)", value=0.5, step=0.1, min_value=0.0)

    with col2:
        st.subheader("Winding")
        primary_turns = st.number_input("Primary Turns", value=20, step=1, min_value=1)
        secondary_turns = st.number_input("Secondary Turns (0 if none)", value=0, step=1, min_value=0)

        wire_type = st.selectbox("Wire Type", ["round", "litz"])
        wire_diameter = st.number_input("Wire Diameter (mm)", value=0.5, step=0.1, min_value=0.1)

    st.subheader("Operating Conditions")
    col1, col2, col3 = st.columns(3)

    with col1:
        frequency = st.number_input("Frequency (kHz)", value=100.0, step=10.0)
    with col2:
        current_rms = st.number_input("Primary Current RMS (A)", value=1.0, step=0.1)
    with col3:
        temperature = st.number_input("Temperature (C)", value=25.0, step=5.0)

    if st.button("Analyze", type="primary"):
        with st.spinner("Analyzing design..."):
            analyze_design(
                core_shape, core_material, air_gap_mm,
                primary_turns, secondary_turns,
                wire_type, wire_diameter,
                frequency * 1000, current_rms, temperature
            )


def analyze_design(core_shape, core_material, air_gap_mm,
                   primary_turns, secondary_turns,
                   wire_type, wire_diameter,
                   frequency, current_rms, temperature):
    """Perform analysis on the design."""

    try:
        results = {}

        # Material properties
        st.subheader("Material Properties")
        col1, col2 = st.columns(2)

        with col1:
            mu = PM.get_material_permeability(core_material, temperature, 0, frequency)
            st.metric("Permeability", f"{mu:.0f}")

        with col2:
            rho = PM.get_material_resistivity(core_material, temperature)
            st.metric("Resistivity", f"{rho:.2e} ohm-m")

        # Steinmetz coefficients
        mat = PM.find_core_material_by_name(core_material)
        steinmetz = PM.get_core_material_steinmetz_coefficients(mat, frequency)
        if isinstance(steinmetz, dict):
            st.write(f"Steinmetz: k={steinmetz.get('k', 0):.2e}, "
                     f"alpha={steinmetz.get('alpha', 0):.2f}, "
                     f"beta={steinmetz.get('beta', 0):.2f}")

        # Core data
        st.subheader("Core Geometry")
        shape = PM.find_core_shape_by_name(core_shape)
        if isinstance(shape, dict):
            fd = shape.get("functionalDescription", {})
            if "dimensions" in fd:
                dims = fd["dimensions"]
                c1, c2, c3 = st.columns(3)
                with c1:
                    if "A" in dims:
                        st.metric("Height (A)", f"{dims['A']*1000:.1f} mm")
                with c2:
                    if "B" in dims:
                        st.metric("Width (B)", f"{dims['B']*1000:.1f} mm")
                with c3:
                    if "C" in dims:
                        st.metric("Depth (C)", f"{dims['C']*1000:.1f} mm")

        # Wire properties
        st.subheader("Wire Properties")
        try:
            wire = PM.find_wire_by_dimension(wire_diameter / 1000, wire_type, "IEC 60317")
            if wire:
                r_dc = PM.calculate_dc_resistance_per_meter(wire, temperature)
                st.metric("DC Resistance", f"{r_dc*1000:.2f} mohm/m @ {temperature}C")
        except Exception as e:
            st.warning(f"Could not calculate wire properties: {e}")

        # Summary
        st.subheader("Design Summary")
        st.info(f"""
        **Core:** {core_shape} / {core_material}
        **Air Gap:** {air_gap_mm} mm
        **Primary:** {primary_turns} turns
        **Frequency:** {frequency/1000:.0f} kHz
        """)

    except Exception as e:
        st.error(f"Analysis failed: {e}")

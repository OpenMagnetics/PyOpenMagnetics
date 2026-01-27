"""
Database Page - Browse cores, materials, and wires.
"""

import streamlit as st
import PyOpenMagnetics as PM


def render():
    st.title("Component Database")

    tab1, tab2, tab3 = st.tabs(["Cores", "Materials", "Wires"])

    with tab1:
        render_cores_tab()

    with tab2:
        render_materials_tab()

    with tab3:
        render_wires_tab()


def render_cores_tab():
    st.subheader("Core Shapes")

    col1, col2 = st.columns([1, 3])

    with col1:
        # Get families
        families = PM.get_core_shape_families()
        selected_family = st.selectbox("Family", ["All"] + families)

    # Get shapes
    all_shapes = PM.get_core_shape_names(True)
    if selected_family != "All":
        shapes = [s for s in all_shapes if s.upper().startswith(selected_family.upper())]
    else:
        shapes = all_shapes

    with col2:
        st.write(f"Found {len(shapes)} shapes")

    # Display shapes in columns
    cols = st.columns(4)
    for i, shape in enumerate(shapes[:100]):  # Limit to 100
        with cols[i % 4]:
            if st.button(shape, key=f"shape_{shape}"):
                st.session_state["selected_shape"] = shape

    # Shape details
    if "selected_shape" in st.session_state:
        shape_name = st.session_state["selected_shape"]
        st.divider()
        st.subheader(f"Shape: {shape_name}")

        try:
            shape_data = PM.find_core_shape_by_name(shape_name)
            if isinstance(shape_data, dict):
                fd = shape_data.get("functionalDescription", {})

                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Family:** {fd.get('family', 'N/A')}")
                    st.write(f"**Type:** {fd.get('type', 'N/A')}")

                with col2:
                    if "dimensions" in fd:
                        st.write("**Dimensions:**")
                        for k, v in fd["dimensions"].items():
                            if isinstance(v, (int, float)):
                                st.write(f"  {k}: {v*1000:.2f} mm")
        except Exception as e:
            st.error(f"Could not load shape data: {e}")


def render_materials_tab():
    st.subheader("Core Materials")

    col1, col2 = st.columns([1, 3])

    with col1:
        # Manufacturer filter
        manufacturers = ["All", "Ferroxcube", "TDK", "MAGNETICS", "Fair-Rite"]
        selected_mfr = st.selectbox("Manufacturer", manufacturers)

    # Get materials
    if selected_mfr == "All":
        materials = PM.get_core_material_names()
    else:
        try:
            materials = PM.get_core_material_names_by_manufacturer(selected_mfr)
        except Exception:
            materials = []

    with col2:
        st.write(f"Found {len(materials)} materials")

    # Material selector
    selected_material = st.selectbox("Select Material", materials if materials else ["No materials found"])

    if selected_material and selected_material != "No materials found":
        st.divider()
        st.subheader(f"Material: {selected_material}")

        try:
            # Get material properties
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**Permeability**")
                for freq in [10000, 100000, 500000, 1000000]:
                    try:
                        mu = PM.get_material_permeability(selected_material, 25, 0, freq)
                        st.write(f"@ {freq/1000:.0f}kHz: {mu:.0f}")
                    except Exception:
                        pass

            with col2:
                st.markdown("**Resistivity**")
                try:
                    rho = PM.get_material_resistivity(selected_material, 25)
                    st.write(f"@ 25C: {rho:.2f} ohm-m")
                except Exception:
                    st.write("N/A")

            with col3:
                st.markdown("**Steinmetz @ 100kHz**")
                try:
                    mat = PM.find_core_material_by_name(selected_material)
                    steinmetz = PM.get_core_material_steinmetz_coefficients(mat, 100000)
                    if isinstance(steinmetz, dict):
                        st.write(f"k = {steinmetz.get('k', 0):.2e}")
                        st.write(f"alpha = {steinmetz.get('alpha', 0):.2f}")
                        st.write(f"beta = {steinmetz.get('beta', 0):.2f}")
                except Exception:
                    st.write("N/A")

        except Exception as e:
            st.error(f"Could not load material data: {e}")


def render_wires_tab():
    st.subheader("Wire Database")

    # Wire types
    try:
        wire_types = PM.get_available_wire_types()
        st.write(f"**Available types:** {', '.join(wire_types)}")
    except Exception:
        wire_types = []

    col1, col2 = st.columns(2)

    with col1:
        wire_type = st.selectbox("Wire Type", ["round", "litz", "foil", "rectangular"])

    with col2:
        diameter_mm = st.number_input("Diameter (mm)", value=0.5, step=0.1, min_value=0.1)

    if st.button("Find Wire"):
        try:
            wire = PM.find_wire_by_dimension(diameter_mm / 1000, wire_type, "IEC 60317")
            if wire:
                st.success("Wire found!")

                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Name:** {wire.get('name', 'N/A')}")
                    st.write(f"**Type:** {wire.get('type', wire_type)}")

                with col2:
                    r_dc = PM.calculate_dc_resistance_per_meter(wire, 25)
                    st.write(f"**DC Resistance:** {r_dc*1000:.2f} mohm/m @ 25C")

                    r_dc_hot = PM.calculate_dc_resistance_per_meter(wire, 100)
                    st.write(f"**DC Resistance:** {r_dc_hot*1000:.2f} mohm/m @ 100C")
            else:
                st.warning("Wire not found")
        except Exception as e:
            st.error(f"Error: {e}")

    # AWG reference table
    with st.expander("AWG Reference"):
        awg_data = [
            ("AWG 20", "0.812", "33.3"),
            ("AWG 22", "0.644", "53.0"),
            ("AWG 24", "0.511", "84.2"),
            ("AWG 26", "0.405", "134"),
            ("AWG 28", "0.321", "213"),
            ("AWG 30", "0.255", "339"),
        ]
        st.table({"AWG": [a[0] for a in awg_data],
                  "Diameter (mm)": [a[1] for a in awg_data],
                  "Resistance (mohm/m)": [a[2] for a in awg_data]})

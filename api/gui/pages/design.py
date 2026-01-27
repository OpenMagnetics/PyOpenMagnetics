"""
Design Page - Main magnetic component design interface.
"""

import streamlit as st
from api.design import Design


def render():
    st.title("Magnetic Component Designer")

    # Topology selector
    col1, col2 = st.columns([1, 3])

    with col1:
        topology = st.selectbox(
            "Topology",
            ["Flyback", "Buck", "Boost", "Forward", "LLC", "Inductor"],
            index=0
        )

    # Input forms based on topology
    st.subheader("Electrical Specifications")

    if topology == "Flyback":
        render_flyback_form()
    elif topology == "Buck":
        render_buck_form()
    elif topology == "Boost":
        render_boost_form()
    elif topology == "Forward":
        render_forward_form()
    elif topology == "LLC":
        render_llc_form()
    elif topology == "Inductor":
        render_inductor_form()


def render_flyback_form():
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Input**")
        vin_type = st.radio("Input Type", ["AC", "DC"], horizontal=True)
        vin_min = st.number_input("Vin Min (V)", value=85.0, step=1.0)
        vin_max = st.number_input("Vin Max (V)", value=265.0, step=1.0)

    with col2:
        st.markdown("**Output**")
        vout = st.number_input("Vout (V)", value=12.0, step=0.1)
        iout = st.number_input("Iout (A)", value=2.0, step=0.1)
        # Optional second output
        add_output = st.checkbox("Add secondary output")
        if add_output:
            vout2 = st.number_input("Vout2 (V)", value=5.0, step=0.1)
            iout2 = st.number_input("Iout2 (A)", value=1.0, step=0.1)

    with col3:
        st.markdown("**Parameters**")
        fsw = st.number_input("Frequency (kHz)", value=100.0, step=10.0)
        efficiency = st.slider("Target Efficiency", 0.80, 0.95, 0.87, 0.01)
        priority = st.selectbox("Optimize for", ["efficiency", "size", "cost"])

    # Constraints
    with st.expander("Size Constraints (optional)"):
        c1, c2, c3 = st.columns(3)
        with c1:
            max_height = st.number_input("Max Height (mm)", value=0.0, step=1.0)
        with c2:
            max_width = st.number_input("Max Width (mm)", value=0.0, step=1.0)
        with c3:
            max_depth = st.number_input("Max Depth (mm)", value=0.0, step=1.0)

    # Design button
    if st.button("Find Designs", type="primary"):
        with st.spinner("Searching for optimal designs..."):
            try:
                builder = Design.flyback()
                if vin_type == "AC":
                    builder.vin_ac(vin_min, vin_max)
                else:
                    builder.vin_dc(vin_min, vin_max)
                builder.output(vout, iout)
                if add_output:
                    builder.output(vout2, iout2)
                builder.fsw(fsw * 1000)
                builder.efficiency(efficiency)
                builder.prefer(priority)

                if max_height > 0:
                    builder.max_height(max_height)
                if max_width > 0:
                    builder.max_width(max_width)
                if max_depth > 0:
                    builder.max_depth(max_depth)

                # Show calculated parameters
                params = builder.get_calculated_parameters()
                st.info(f"Calculated: n={params['turns_ratio']:.2f}, Lm={params['magnetizing_inductance_uH']:.1f}uH")

                results = builder.solve(max_results=5)
                display_results(results)

            except Exception as e:
                st.error(f"Design failed: {e}")


def render_buck_form():
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Input**")
        vin_min = st.number_input("Vin Min (V)", value=10.0, step=0.5)
        vin_max = st.number_input("Vin Max (V)", value=14.0, step=0.5)

    with col2:
        st.markdown("**Output**")
        vout = st.number_input("Vout (V)", value=5.0, step=0.1)
        iout = st.number_input("Iout (A)", value=3.0, step=0.1)

    with col3:
        st.markdown("**Parameters**")
        fsw = st.number_input("Frequency (kHz)", value=500.0, step=50.0)
        ripple = st.slider("Ripple Ratio", 0.1, 0.5, 0.3, 0.05)
        priority = st.selectbox("Optimize for", ["efficiency", "size", "cost"])

    if st.button("Find Designs", type="primary"):
        with st.spinner("Searching for optimal designs..."):
            try:
                builder = Design.buck().vin(vin_min, vin_max).vout(vout).iout(iout)
                builder.fsw(fsw * 1000).ripple_ratio(ripple).prefer(priority)

                params = builder.get_calculated_parameters()
                st.info(f"Calculated: L={params['inductance_uH']:.1f}uH, D={params['duty_cycle']:.1%}")

                results = builder.solve(max_results=5)
                display_results(results)

            except Exception as e:
                st.error(f"Design failed: {e}")


def render_boost_form():
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Input**")
        vin_min = st.number_input("Vin Min (V)", value=3.0, step=0.1)
        vin_max = st.number_input("Vin Max (V)", value=4.2, step=0.1)

    with col2:
        st.markdown("**Output**")
        vout = st.number_input("Vout (V)", value=5.0, step=0.1)
        pout = st.number_input("Pout (W)", value=2.0, step=0.1)

    with col3:
        st.markdown("**Parameters**")
        fsw = st.number_input("Frequency (kHz)", value=1000.0, step=100.0)
        priority = st.selectbox("Optimize for", ["efficiency", "size", "cost"])

    if st.button("Find Designs", type="primary"):
        with st.spinner("Searching for optimal designs..."):
            try:
                builder = Design.boost().vin(vin_min, vin_max).vout(vout).pout(pout)
                builder.fsw(fsw * 1000).prefer(priority)

                params = builder.get_calculated_parameters()
                st.info(f"Calculated: L={params['inductance_uH']:.1f}uH")

                results = builder.solve(max_results=5)
                display_results(results)

            except Exception as e:
                st.error(f"Design failed: {e}")


def render_forward_form():
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Input**")
        vin_min = st.number_input("Vin Min (V)", value=380.0, step=10.0)
        vin_max = st.number_input("Vin Max (V)", value=420.0, step=10.0)

    with col2:
        st.markdown("**Output**")
        vout = st.number_input("Vout (V)", value=12.0, step=0.1)
        iout = st.number_input("Iout (A)", value=10.0, step=0.5)

    with col3:
        st.markdown("**Parameters**")
        fsw = st.number_input("Frequency (kHz)", value=100.0, step=10.0)
        variant = st.selectbox("Variant", ["two_switch", "single_switch", "active_clamp"])
        priority = st.selectbox("Optimize for", ["efficiency", "size", "cost"])

    if st.button("Find Designs", type="primary"):
        with st.spinner("Searching for optimal designs..."):
            try:
                builder = Design.forward().variant(variant).vin_dc(vin_min, vin_max)
                builder.output(vout, iout).fsw(fsw * 1000).prefer(priority)

                params = builder.get_calculated_parameters()
                st.info(f"Calculated: n={params['turns_ratio']:.2f}")

                results = builder.solve(max_results=5)
                display_results(results)

            except Exception as e:
                st.error(f"Design failed: {e}")


def render_llc_form():
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Input**")
        vin_min = st.number_input("Vin Min (V)", value=380.0, step=10.0)
        vin_max = st.number_input("Vin Max (V)", value=420.0, step=10.0)

    with col2:
        st.markdown("**Output**")
        vout = st.number_input("Vout (V)", value=48.0, step=1.0)
        iout = st.number_input("Iout (A)", value=20.0, step=1.0)

    with col3:
        st.markdown("**Parameters**")
        fres = st.number_input("Resonant Freq (kHz)", value=100.0, step=10.0)
        q_factor = st.slider("Q Factor", 0.1, 0.5, 0.3, 0.05)
        priority = st.selectbox("Optimize for", ["efficiency", "size", "cost"])

    if st.button("Find Designs", type="primary"):
        with st.spinner("Searching for optimal designs..."):
            try:
                builder = Design.llc().vin_dc(vin_min, vin_max).output(vout, iout)
                builder.resonant_frequency(fres * 1000).quality_factor(q_factor).prefer(priority)

                params = builder.get_calculated_parameters()
                st.info(f"Calculated: n={params['turns_ratio']:.2f}, Lm={params['magnetizing_inductance_uH']:.1f}uH")

                results = builder.solve(max_results=5)
                display_results(results)

            except Exception as e:
                st.error(f"Design failed: {e}")


def render_inductor_form():
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Inductance**")
        inductance = st.number_input("Inductance (uH)", value=100.0, step=10.0)

    with col2:
        st.markdown("**Current**")
        idc = st.number_input("DC Current (A)", value=5.0, step=0.5)
        iac_pp = st.number_input("AC Ripple (A pk-pk)", value=1.0, step=0.1)

    with col3:
        st.markdown("**Parameters**")
        fsw = st.number_input("Frequency (kHz)", value=100.0, step=10.0)
        priority = st.selectbox("Optimize for", ["efficiency", "size", "cost"])

    if st.button("Find Designs", type="primary"):
        with st.spinner("Searching for optimal designs..."):
            try:
                builder = Design.inductor().inductance(inductance * 1e-6).idc(idc).iac_pp(iac_pp)
                builder.fsw(fsw * 1000).prefer(priority)

                params = builder.get_calculated_parameters()
                st.info(f"Peak current: {params['i_peak']:.1f}A")

                results = builder.solve(max_results=5)
                display_results(results)

            except Exception as e:
                st.error(f"Design failed: {e}")


def display_results(results):
    """Display design results in a nice format."""
    if not results:
        st.warning("No suitable designs found. Try relaxing constraints.")
        return

    st.success(f"Found {len(results)} designs")

    # Results table
    for i, r in enumerate(results):
        with st.expander(f"Design #{i+1}: {r.core} / {r.material}", expanded=(i == 0)):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**Core**")
                st.write(f"Shape: {r.core}")
                st.write(f"Material: {r.material}")
                st.write(f"Air Gap: {r.air_gap_mm:.2f} mm")

            with col2:
                st.markdown("**Winding**")
                st.write(f"Primary: {r.primary_turns}T")
                st.write(f"Wire: {r.primary_wire}")
                if r.secondary_turns:
                    st.write(f"Secondary: {r.secondary_turns}T")

            with col3:
                st.markdown("**Losses**")
                st.write(f"Core: {r.core_loss_w:.3f} W")
                st.write(f"Copper: {r.copper_loss_w:.3f} W")
                st.write(f"Total: {r.total_loss_w:.3f} W")

            # Warnings
            if r.warnings:
                for warning in r.warnings:
                    st.warning(warning)

    # Store results in session for comparison
    st.session_state["last_results"] = results

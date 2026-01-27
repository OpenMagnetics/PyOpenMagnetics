"""
Compare Page - Compare multiple design results.
"""

import streamlit as st


def render():
    st.title("Compare Designs")

    # Check for stored results
    if "last_results" not in st.session_state or not st.session_state["last_results"]:
        st.info("No designs to compare. Run a design first from the Design page.")
        return

    results = st.session_state["last_results"]
    st.write(f"Comparing {len(results)} designs from last search")

    # Comparison table
    st.subheader("Comparison Table")

    # Build comparison data
    table_data = {
        "Design": [],
        "Core": [],
        "Material": [],
        "Gap (mm)": [],
        "Turns": [],
        "Wire": [],
        "Core Loss (W)": [],
        "Cu Loss (W)": [],
        "Total Loss (W)": [],
    }

    for i, r in enumerate(results):
        table_data["Design"].append(f"#{i+1}")
        table_data["Core"].append(r.core)
        table_data["Material"].append(r.material)
        table_data["Gap (mm)"].append(f"{r.air_gap_mm:.2f}")
        table_data["Turns"].append(str(r.primary_turns))
        table_data["Wire"].append(r.primary_wire or "N/A")
        table_data["Core Loss (W)"].append(f"{r.core_loss_w:.3f}")
        table_data["Cu Loss (W)"].append(f"{r.copper_loss_w:.3f}")
        table_data["Total Loss (W)"].append(f"{r.total_loss_w:.3f}")

    st.dataframe(table_data, use_container_width=True)

    # Loss comparison chart
    st.subheader("Loss Comparison")

    chart_data = {
        "Design": [f"#{i+1}: {r.core}" for i, r in enumerate(results)],
        "Core Loss": [r.core_loss_w for r in results],
        "Copper Loss": [r.copper_loss_w for r in results],
    }

    st.bar_chart(chart_data, x="Design", y=["Core Loss", "Copper Loss"], stack=False)

    # Detailed comparison
    st.subheader("Side-by-Side Details")

    cols = st.columns(min(len(results), 3))
    for i, (col, r) in enumerate(zip(cols, results[:3])):
        with col:
            st.markdown(f"### Design #{i+1}")
            st.write(f"**Core:** {r.core}")
            st.write(f"**Material:** {r.material}")
            st.write(f"**Air Gap:** {r.air_gap_mm:.2f} mm")
            st.write(f"**Primary:** {r.primary_turns}T")
            st.write(f"**Wire:** {r.primary_wire}")
            st.divider()
            st.write(f"**Core Loss:** {r.core_loss_w:.3f} W")
            st.write(f"**Cu Loss:** {r.copper_loss_w:.3f} W")
            st.write(f"**Total:** {r.total_loss_w:.3f} W")

            if r.warnings:
                st.warning("\n".join(r.warnings))

    # Export option
    st.subheader("Export")
    if st.button("Export to CSV"):
        import csv
        import io

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=table_data.keys())
        writer.writeheader()
        for i in range(len(results)):
            row = {k: table_data[k][i] for k in table_data.keys()}
            writer.writerow(row)

        st.download_button(
            label="Download CSV",
            data=output.getvalue(),
            file_name="design_comparison.csv",
            mime="text/csv"
        )

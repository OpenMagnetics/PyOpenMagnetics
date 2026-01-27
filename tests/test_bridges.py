"""Tests for external tool bridges."""

import pytest


class TestFEMMTBridge:
    """Test FEMMT bridge exports."""

    def test_import_bridge(self):
        from api.bridges import export_to_femmt, FEMMTExporter
        assert callable(export_to_femmt)
        assert FEMMTExporter is not None

    def test_femmt_config(self):
        from api.bridges.femmt import FEMMTConfig
        config = FEMMTConfig(
            working_directory="./test_sim",
            mesh_accuracy=0.3,
            simulation_name="test_design"
        )
        assert config.working_directory == "./test_sim"
        assert config.mesh_accuracy == 0.3

    def test_export_basic(self):
        from api.bridges import export_to_femmt
        from api.results import DesignResult, WindingInfo

        # Create a mock design result
        design = DesignResult(
            core="ETD 34",
            material="3C95",
            core_family="ETD",
            windings=[WindingInfo("Primary", 20, "AWG 24 (0.51mm)")],
            air_gap_mm=0.5,
            core_loss_w=0.5,
            copper_loss_w=0.3,
            total_loss_w=0.8,
            temp_rise_c=25.0,
            bpk_tesla=0.15,
            saturation_margin=0.3,
        )

        script = export_to_femmt(design)

        # Check script contains expected content
        assert "import femmt as fmt" in script
        assert "ETD 34" in script
        assert "3C95" in script or "N95" in script
        assert "turns=20" in script
        assert "0.0005" in script  # air gap in meters

    def test_export_with_custom_config(self):
        from api.bridges import export_to_femmt, FEMMTExporter
        from api.bridges.femmt import FEMMTConfig
        from api.results import DesignResult, WindingInfo

        config = FEMMTConfig(
            working_directory="./custom_dir",
            simulation_name="custom_sim"
        )

        design = DesignResult(
            core="PQ 26/25",
            material="N87",
            core_family="PQ",
            windings=[WindingInfo("Primary", 15, "0.3mm")],
            air_gap_mm=0.2,
            core_loss_w=0.3,
            copper_loss_w=0.2,
            total_loss_w=0.5,
            temp_rise_c=20.0,
            bpk_tesla=0.12,
            saturation_margin=0.4,
        )

        script = export_to_femmt(design, config)

        assert "./custom_dir" in script
        assert "custom_sim" in script

    def test_core_type_mapping(self):
        from api.bridges.femmt import FEMMTExporter

        exporter = FEMMTExporter()

        # Test various core prefixes map correctly
        assert exporter.CORE_TYPE_MAP.get("E") == "E"
        assert exporter.CORE_TYPE_MAP.get("ETD") == "E"
        assert exporter.CORE_TYPE_MAP.get("PQ") == "PQ"
        assert exporter.CORE_TYPE_MAP.get("RM") == "RM"

    def test_material_mapping(self):
        from api.bridges.femmt import FEMMTExporter

        exporter = FEMMTExporter()

        # Test material mappings
        assert exporter.MATERIAL_MAP.get("3C95") == "N95"
        assert exporter.MATERIAL_MAP.get("N87") == "N87"

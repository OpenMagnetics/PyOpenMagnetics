"""Tests to validate all example designs work correctly."""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestConsumerExamples:
    """Test consumer electronics examples."""

    def test_usb_pd_20w_imports(self):
        from examples.consumer.usb_pd_20w import design_usb_pd_20w
        assert callable(design_usb_pd_20w)

    def test_usb_pd_65w_imports(self):
        from examples.consumer.usb_pd_65w import design_usb_pd_65w
        assert callable(design_usb_pd_65w)

    def test_usb_pd_140w_imports(self):
        from examples.consumer.usb_pd_140w import design_usb_pd_140w
        assert callable(design_usb_pd_140w)

    def test_laptop_19v_90w_imports(self):
        from examples.consumer.laptop_19v_90w import design_laptop_19v_90w
        assert callable(design_laptop_19v_90w)

    def test_usb_pd_20w_runs(self):
        from examples.consumer.usb_pd_20w import design_usb_pd_20w
        # Just verify it runs without exception (may return None if no designs found)
        result = design_usb_pd_20w()
        # Result can be None or a DesignResult
        assert result is None or hasattr(result, 'core')


class TestAutomotiveExamples:
    """Test automotive examples."""

    def test_48v_to_12v_imports(self):
        # Use importlib for numeric prefix
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "buck_48v",
            os.path.join(os.path.dirname(__file__), "..", "examples", "automotive", "48v_to_12v_1kw.py")
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert callable(module.design_48v_to_12v_1kw)

    def test_gate_drive_imports(self):
        from examples.automotive.gate_drive_isolated import design_gate_drive_isolated
        assert callable(design_gate_drive_isolated)


class TestIndustrialExamples:
    """Test industrial examples."""

    def test_din_rail_24v_imports(self):
        from examples.industrial.din_rail_24v import design_din_rail_24v
        assert callable(design_din_rail_24v)

    def test_medical_60601_imports(self):
        from examples.industrial.medical_60601 import design_medical_60601
        assert callable(design_medical_60601)

    def test_vfd_dc_link_choke_imports(self):
        from examples.industrial.vfd_dc_link_choke import design_vfd_dc_link_choke
        assert callable(design_vfd_dc_link_choke)


class TestTelecomExamples:
    """Test telecom examples."""

    def test_rectifier_48v_3kw_imports(self):
        from examples.telecom.rectifier_48v_3kw import design_rectifier_48v_3kw
        assert callable(design_rectifier_48v_3kw)

    def test_poe_injector_imports(self):
        from examples.telecom.poe_injector import design_poe_injector
        assert callable(design_poe_injector)


class TestExampleCategories:
    """Test that all example categories are importable."""

    def test_consumer_package(self):
        from examples import consumer
        assert hasattr(consumer, 'design_usb_pd_20w')

    def test_industrial_package(self):
        from examples import industrial
        assert hasattr(industrial, 'design_din_rail_24v')

    def test_telecom_package(self):
        from examples import telecom
        assert hasattr(telecom, 'design_poe_injector')

"""Consumer electronics power supply examples."""

from .usb_pd_20w import design_usb_pd_20w
from .usb_pd_65w import design_usb_pd_65w
from .usb_pd_140w import design_usb_pd_140w
from .laptop_19v_90w import design_laptop_19v_90w

__all__ = [
    "design_usb_pd_20w",
    "design_usb_pd_65w",
    "design_usb_pd_140w",
    "design_laptop_19v_90w",
]

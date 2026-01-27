"""Industrial power supply examples."""

from .din_rail_24v import design_din_rail_24v
from .medical_60601 import design_medical_60601
from .vfd_dc_link_choke import design_vfd_dc_link_choke

__all__ = [
    "design_din_rail_24v",
    "design_medical_60601",
    "design_vfd_dc_link_choke",
]

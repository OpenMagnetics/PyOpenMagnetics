"""
TAS Root document - Simplified format for basic DC-DC converters.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

from tas.models.inputs import TASInputs
from tas.models.outputs import TASOutputs
from tas.models.components import TASComponentList


@dataclass
class TASMetadata:
    """Document metadata."""
    name: str = ""
    version: str = "0.1.0"
    description: str = ""
    author: str = ""
    created: str = ""
    modified: str = ""

    def to_dict(self) -> dict:
        result = {"name": self.name, "version": self.version}
        if self.description:
            result["description"] = self.description
        if self.author:
            result["author"] = self.author
        if self.created:
            result["created"] = self.created
        if self.modified:
            result["modified"] = self.modified
        return result

    @classmethod
    def from_dict(cls, d: dict) -> "TASMetadata":
        return cls(
            name=d.get("name", ""),
            version=d.get("version", "0.1.0"),
            description=d.get("description", ""),
            author=d.get("author", ""),
            created=d.get("created", ""),
            modified=d.get("modified", ""),
        )


@dataclass
class TASDocument:
    """
    Simplified TAS document for basic DC-DC converters.

    Structure:
    - metadata: Document info (name, version, author)
    - inputs: Requirements and operating points
    - components: Inductors, capacitors, switches, diodes
    - outputs: Losses, KPIs, results
    """
    metadata: TASMetadata = field(default_factory=TASMetadata)
    inputs: TASInputs = field(default_factory=TASInputs)
    components: TASComponentList = field(default_factory=TASComponentList)
    outputs: Optional[TASOutputs] = None

    def to_dict(self) -> dict:
        result = {
            "metadata": self.metadata.to_dict(),
            "inputs": self.inputs.to_dict(),
        }
        if self.components.all_components:
            result["components"] = self.components.to_dict()
        if self.outputs:
            result["outputs"] = self.outputs.to_dict()
        return result

    @classmethod
    def from_dict(cls, d: dict) -> "TASDocument":
        return cls(
            metadata=TASMetadata.from_dict(d.get("metadata", {})),
            inputs=TASInputs.from_dict(d.get("inputs", {})),
            components=TASComponentList.from_dict(d.get("components", {})),
            outputs=TASOutputs.from_dict(d["outputs"]) if d.get("outputs") else None,
        )

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        import json
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, json_str: str) -> "TASDocument":
        """Deserialize from JSON string."""
        import json
        return cls.from_dict(json.loads(json_str))

    def save(self, filepath: str) -> None:
        """Save to JSON file."""
        with open(filepath, "w") as f:
            f.write(self.to_json())

    @classmethod
    def load(cls, filepath: str) -> "TASDocument":
        """Load from JSON file."""
        with open(filepath, "r") as f:
            return cls.from_json(f.read())


def create_buck_tas(
    name: str,
    v_in_min: float,
    v_in_max: float,
    v_out: float,
    i_out: float,
    frequency: float,
) -> TASDocument:
    """Factory function for buck converter TAS."""
    from tas.models.inputs import TASRequirements, TASOperatingPoint, TASInputs

    now = datetime.now().isoformat()
    return TASDocument(
        metadata=TASMetadata(
            name=name,
            description="Buck converter design",
            created=now,
            modified=now,
        ),
        inputs=TASInputs(
            requirements=TASRequirements(
                v_in_min=v_in_min,
                v_in_max=v_in_max,
                v_out=v_out,
                i_out_max=i_out,
            ),
            operating_points=[
                TASOperatingPoint(
                    name="nominal",
                    frequency=frequency,
                    duty_cycle=v_out / ((v_in_min + v_in_max) / 2),
                )
            ],
        ),
    )


def create_boost_tas(
    name: str,
    v_in_min: float,
    v_in_max: float,
    v_out: float,
    i_out: float,
    frequency: float,
) -> TASDocument:
    """Factory function for boost converter TAS."""
    from tas.models.inputs import TASRequirements, TASOperatingPoint, TASInputs

    v_in_nom = (v_in_min + v_in_max) / 2
    duty = 1 - (v_in_nom / v_out) if v_out > v_in_nom else 0.5

    now = datetime.now().isoformat()
    return TASDocument(
        metadata=TASMetadata(
            name=name,
            description="Boost converter design",
            created=now,
            modified=now,
        ),
        inputs=TASInputs(
            requirements=TASRequirements(
                v_in_min=v_in_min,
                v_in_max=v_in_max,
                v_out=v_out,
                i_out_max=i_out,
            ),
            operating_points=[
                TASOperatingPoint(
                    name="nominal",
                    frequency=frequency,
                    duty_cycle=duty,
                )
            ],
        ),
    )


def create_flyback_tas(
    name: str,
    v_in_min: float,
    v_in_max: float,
    v_out: float,
    i_out: float,
    frequency: float,
    turns_ratio: float = 1.0,
) -> TASDocument:
    """Factory function for flyback converter TAS."""
    from tas.models.inputs import TASRequirements, TASOperatingPoint, TASInputs

    v_in_nom = (v_in_min + v_in_max) / 2
    duty = (v_out * turns_ratio) / (v_in_nom + v_out * turns_ratio)

    now = datetime.now().isoformat()
    return TASDocument(
        metadata=TASMetadata(
            name=name,
            description="Flyback converter design",
            created=now,
            modified=now,
        ),
        inputs=TASInputs(
            requirements=TASRequirements(
                v_in_min=v_in_min,
                v_in_max=v_in_max,
                v_out=v_out,
                i_out_max=i_out,
                isolation_voltage=1500.0,  # Basic isolation
            ),
            operating_points=[
                TASOperatingPoint(
                    name="nominal",
                    frequency=frequency,
                    duty_cycle=duty,
                )
            ],
        ),
    )

"""
Magnetic Design Knowledge Base.

Domain expertise for power electronics applications.
Written for hardware engineers, not software developers.
"""

# =============================================================================
# APPLICATION KNOWLEDGE
# =============================================================================

APPLICATIONS = {
    # -------------------------------------------------------------------------
    # CONSUMER ELECTRONICS
    # -------------------------------------------------------------------------
    "usb_charger": {
        "name": "USB Charger / Power Adapter",
        "description": "Wall charger for phones, tablets, and small devices",
        "power_range": (5, 240),  # Watts
        "variants": {
            "5w_basic": {"power": 5, "vout": 5, "profile": "USB-A legacy"},
            "10w_ipad": {"power": 10, "vout": 5, "profile": "Apple 2.1A"},
            "18w_qc": {"power": 18, "vout": [5, 9, 12], "profile": "QC3.0"},
            "20w_pd": {"power": 20, "vout": [5, 9, 12], "profile": "PD 20W"},
            "30w_pd": {"power": 30, "vout": [5, 9, 15, 20], "profile": "PD 30W"},
            "45w_pd": {"power": 45, "vout": [5, 9, 15, 20], "profile": "PD 45W"},
            "65w_pd": {"power": 65, "vout": [5, 9, 15, 20], "profile": "PD 65W"},
            "100w_pd": {"power": 100, "vout": [5, 9, 15, 20], "profile": "PD 100W"},
            "140w_pd": {"power": 140, "vout": [5, 9, 15, 20, 28], "profile": "PD 3.1 EPR"},
            "240w_pd": {"power": 240, "vout": [5, 9, 15, 20, 28, 48], "profile": "PD 3.1 EPR"},
        },
        "typical_topology": "flyback",
        "alternative_topologies": ["active_clamp_flyback", "LLC"],
        "input_voltage": {"universal_ac": (85, 265), "us_only": (100, 130), "eu_only": (200, 240)},
        "key_constraints": ["size", "cost", "efficiency", "standby_power", "EMI"],
        "standards": ["IEC 62368-1", "DoE Level VI", "CoC Tier 2", "FCC Part 15"],
        "design_tips": [
            "EFD cores for flat adapters, ETD for cubes",
            "Higher frequency (>100kHz) enables smaller size but needs GaN",
            "Standby power <75mW required for efficiency standards",
            "Primary-side regulation can eliminate optocoupler",
        ],
        "common_mistakes": [
            "Undersized transformer for thermal (runs too hot)",
            "Insufficient creepage for safety standards",
            "EMI filter too small for Class B",
            "Not accounting for cable voltage drop",
        ],
        "questions_to_ask": [
            "What power level? (affects topology choice)",
            "Single output or PPS (programmable)?",
            "GaN or Silicon? (affects frequency/size)",
            "Target market? (affects standards)",
            "Form factor preference? (cube, flat, travel)",
        ],
    },

    "laptop_adapter": {
        "name": "Laptop Power Adapter",
        "description": "AC-DC adapter for laptops and notebooks",
        "power_range": (45, 330),
        "variants": {
            "45w_ultrabook": {"power": 45, "vout": 20, "connector": "USB-C"},
            "65w_standard": {"power": 65, "vout": [19, 20], "connector": "barrel/USB-C"},
            "90w_workstation": {"power": 90, "vout": 19.5, "connector": "barrel"},
            "100w_usbc": {"power": 100, "vout": 20, "connector": "USB-C"},
            "140w_macbook": {"power": 140, "vout": 28, "connector": "MagSafe/USB-C"},
            "180w_gaming": {"power": 180, "vout": 19.5, "connector": "barrel"},
            "230w_gaming": {"power": 230, "vout": 19.5, "connector": "barrel"},
            "330w_workstation": {"power": 330, "vout": 19.5, "connector": "barrel"},
        },
        "typical_topology": "flyback",
        "topology_by_power": {
            (0, 100): "flyback",
            (100, 200): "active_clamp_flyback",
            (200, 400): "LLC",
        },
        "key_constraints": ["efficiency", "weight", "slim_profile", "thermal"],
        "design_tips": [
            "LLC preferred >150W for efficiency",
            "Slim adapters need EFD/ELP cores",
            "Consider interleaved PFC for >100W",
            "Heat pipes common in slim high-power designs",
        ],
    },

    "led_driver": {
        "name": "LED Driver",
        "description": "Power supply for LED lighting",
        "power_range": (3, 500),
        "variants": {
            "bulb_retrofit": {"power": (3, 15), "output": "constant_current"},
            "tube_retrofit": {"power": (10, 30), "output": "constant_current"},
            "panel_driver": {"power": (20, 60), "output": "constant_current"},
            "high_bay": {"power": (100, 300), "output": "constant_current"},
            "street_light": {"power": (50, 200), "output": "constant_current"},
            "rgb_strip": {"power": (30, 150), "output": "constant_voltage"},
        },
        "typical_topology": "flyback",
        "key_constraints": ["flicker", "PF", "THD", "dimming", "lifetime"],
        "standards": ["ENERGY STAR", "DLC", "Title 24", "Zhaga"],
        "design_tips": [
            "Electrolytic-free for long life (>50k hours)",
            "Valley-fill for high PF without boost PFC",
            "Single-stage flyback for cost, two-stage for performance",
            "TRIAC dimming needs specific control IC",
        ],
        "questions_to_ask": [
            "Indoor or outdoor (IP rating)?",
            "Dimming required? What method?",
            "Flicker requirements (IEEE 1789)?",
            "LED forward voltage and current?",
            "Operating temperature range?",
        ],
    },

    # -------------------------------------------------------------------------
    # AUTOMOTIVE
    # -------------------------------------------------------------------------
    "automotive_dcdc": {
        "name": "Automotive DC-DC Converter",
        "description": "Voltage conversion for automotive systems",
        "variants": {
            "12v_aux": {
                "description": "12V auxiliary from 48V mild hybrid",
                "vin": (36, 52),
                "vout": 12,
                "power": (100, 3000),
            },
            "48v_from_hv": {
                "description": "48V from high-voltage battery",
                "vin": (250, 450),
                "vout": 48,
                "power": (1000, 5000),
            },
            "lv_from_hv": {
                "description": "12V from high-voltage battery (main LDC)",
                "vin": (250, 450),
                "vout": 12,
                "power": (1500, 3500),
            },
        },
        "typical_topology": "phase_shifted_full_bridge",
        "key_constraints": ["efficiency", "EMC", "temperature", "isolation", "weight"],
        "standards": ["AEC-Q200", "ISO 16750", "CISPR 25", "LV 124"],
        "design_tips": [
            "Use nanocrystalline for EMI common mode chokes",
            "Planar transformers common for high power density",
            "Consider interleaving for current ripple",
            "-40°C to +105°C ambient typical",
        ],
        "questions_to_ask": [
            "Voltage class (LV / 48V / HV)?",
            "Continuous vs peak power?",
            "Bidirectional required?",
            "Cooling method (air/liquid)?",
            "ASIL safety level?",
        ],
    },

    "ev_onboard_charger": {
        "name": "EV On-Board Charger (OBC)",
        "description": "AC-DC charger integrated in electric vehicle",
        "variants": {
            "3kw_level1": {"power": 3300, "input": "1-phase", "vout": (250, 450)},
            "7kw_level2": {"power": 7000, "input": "1-phase", "vout": (250, 450)},
            "11kw_level2": {"power": 11000, "input": "3-phase", "vout": (250, 450)},
            "22kw_level2": {"power": 22000, "input": "3-phase", "vout": (250, 800)},
        },
        "typical_topology": "CLLC",  # For bidirectional
        "key_constraints": ["efficiency", "power_density", "bidirectional", "isolation"],
        "design_tips": [
            "CLLC topology for V2G bidirectional",
            "SiC MOSFETs essential for high efficiency",
            "Integrated OBC+DC-DC saves space",
            "Nanocrystalline or ferrite for transformer",
        ],
    },

    "gate_driver_isolated": {
        "name": "Isolated Gate Driver Transformer",
        "description": "Isolation transformer for driving power switches",
        "applications": ["half_bridge", "full_bridge", "SiC", "GaN", "IGBT"],
        "typical_specs": {
            "vout_positive": (12, 20),  # +Vg
            "vout_negative": (-5, -8),   # -Vg (for SiC/IGBT)
            "isolation": (1500, 5000),   # Vrms
            "frequency": (100e3, 1e6),
        },
        "typical_topology": "flyback",
        "key_constraints": ["propagation_delay", "CMTI", "isolation", "size"],
        "design_tips": [
            "Small EE or EP cores for gate drivers",
            "Low interwinding capacitance critical for CMTI",
            "Symmetric construction for matched delay",
            "Triple-insulated wire for reinforced isolation",
        ],
    },

    # -------------------------------------------------------------------------
    # INDUSTRIAL
    # -------------------------------------------------------------------------
    "din_rail_psu": {
        "name": "DIN Rail Power Supply",
        "description": "Industrial power supply for control cabinets",
        "variants": {
            "5v_15w": {"vout": 5, "power": 15},
            "12v_30w": {"vout": 12, "power": 30},
            "24v_60w": {"vout": 24, "power": 60},
            "24v_120w": {"vout": 24, "power": 120},
            "24v_240w": {"vout": 24, "power": 240},
            "24v_480w": {"vout": 24, "power": 480},
            "48v_240w": {"vout": 48, "power": 240},
        },
        "typical_topology": "flyback",
        "topology_by_power": {
            (0, 150): "flyback",
            (150, 300): "forward",
            (300, 600): "LLC",
        },
        "key_constraints": ["efficiency", "reliability", "parallel_operation", "wide_temp"],
        "standards": ["IEC 62368-1", "EN 61000-3-2", "UL 508"],
        "design_tips": [
            "DIN rail width limits core height",
            "Spring terminals preferred over screw",
            "Consider N+1 redundancy capability",
            "Long-life electrolytic or film caps",
        ],
    },

    "medical_psu": {
        "name": "Medical Power Supply",
        "description": "Isolated power supply for medical equipment",
        "classifications": {
            "BF": "Body Floating - patient contact, not cardiac",
            "CF": "Cardiac Floating - direct cardiac connection",
            "2xMOPP": "2 Means of Patient Protection",
            "2xMOOP": "2 Means of Operator Protection",
        },
        "key_constraints": ["leakage_current", "isolation", "EMC", "reliability"],
        "standards": ["IEC 60601-1", "IEC 60601-1-2", "IEC 60601-1-11"],
        "design_tips": [
            "8mm creepage/clearance for 2xMOPP",
            "Earth leakage <300µA (NC), <500µA (SFC)",
            "Patient leakage <100µA (BF), <10µA (CF)",
            "EMC limits 6dB stricter than industrial",
            "Triple insulated wire or margin tape",
        ],
        "questions_to_ask": [
            "Applied part (patient contact)?",
            "Classification needed (BF/CF)?",
            "Home healthcare or clinical?",
            "Defibrillator-proof required?",
        ],
    },

    "vfd_magnetics": {
        "name": "VFD Magnetics (Chokes & Filters)",
        "description": "Inductors and filters for variable frequency drives",
        "components": {
            "dc_link_choke": {
                "purpose": "Smooth DC bus ripple",
                "typical_L": (0.5e-3, 5e-3),
                "typical_I": (5, 500),
            },
            "output_filter": {
                "purpose": "dV/dt filter for motor cable",
                "typical_L": (50e-6, 500e-6),
            },
            "common_mode_choke": {
                "purpose": "EMI suppression",
                "typical_L": (1e-3, 50e-3),
            },
            "line_reactor": {
                "purpose": "Input harmonic reduction",
                "typical_L": (1e-3, 10e-3),
            },
        },
        "core_materials": {
            "dc_link": "powder_core",  # Sendust, MPP, High Flux
            "output": "powder_core",
            "common_mode": "nanocrystalline",
            "line_reactor": "silicon_steel",
        },
    },

    # -------------------------------------------------------------------------
    # TELECOM / DATACENTER
    # -------------------------------------------------------------------------
    "server_psu": {
        "name": "Server Power Supply",
        "description": "High-efficiency PSU for servers and datacenters",
        "form_factors": {
            "atx": {"width": 150, "height": 86, "depth": 140},
            "1u": {"width": 40, "height": 40, "depth": 200},
            "crps": {"width": 73.5, "height": 39, "depth": 185},
        },
        "power_levels": [500, 800, 1200, 1600, 2000, 2400, 3000],
        "efficiency_tiers": {
            "80_plus": 0.80,
            "bronze": 0.82,
            "silver": 0.85,
            "gold": 0.87,
            "platinum": 0.90,
            "titanium": 0.94,
        },
        "typical_topology": "LLC",
        "key_constraints": ["efficiency", "power_density", "holdup_time", "hot_swap"],
        "design_tips": [
            "Interleaved bridgeless totem-pole PFC",
            "LLC with synchronous rectification",
            "GaN for Titanium efficiency",
            "Digital control for adaptive tuning",
        ],
    },

    "poe_psu": {
        "name": "Power over Ethernet",
        "description": "Power delivery over Ethernet cable",
        "standards": {
            "802.3af": {"power": 15.4, "voltage": (44, 57), "name": "PoE"},
            "802.3at": {"power": 30, "voltage": (50, 57), "name": "PoE+"},
            "802.3bt_type3": {"power": 60, "voltage": (50, 57), "name": "PoE++"},
            "802.3bt_type4": {"power": 90, "voltage": (52, 57), "name": "PoE++"},
        },
        "sides": {
            "PSE": "Power Sourcing Equipment (switch/injector)",
            "PD": "Powered Device (camera, AP, phone)",
        },
        "typical_topology": "flyback",
        "design_tips": [
            "Input voltage is already DC (from PoE)",
            "PD-side needs flyback for isolation",
            "Low standby power for PoE budget",
            "Consider 4-pair for high power",
        ],
    },

    "telecom_rectifier": {
        "name": "Telecom Rectifier Module",
        "description": "AC-DC module for -48V telecom systems",
        "power_levels": [1000, 2000, 3000, 4000, 6000],
        "output": {"voltage": -48, "range": (-42, -58)},
        "typical_topology": "LLC",
        "key_constraints": ["efficiency", "power_factor", "hot_swap", "N+1"],
        "standards": ["ETSI EN 300 132-2", "Bellcore GR-1089"],
    },

    # -------------------------------------------------------------------------
    # MAGNETICS-SPECIFIC (Not power supplies)
    # -------------------------------------------------------------------------
    "emi_filter": {
        "name": "EMI Filter Components",
        "description": "Common mode and differential mode chokes",
        "components": {
            "common_mode_choke": {
                "purpose": "Attenuate common mode noise",
                "frequency_range": (10e3, 30e6),
                "core_material": "nanocrystalline",
                "typical_L": (1e-3, 100e-3),
            },
            "differential_mode_choke": {
                "purpose": "Attenuate differential mode noise",
                "core_material": "powder_core",
                "typical_L": (10e-6, 1e-3),
            },
        },
        "design_tips": [
            "CM choke: high impedance at noise frequency, low at 50/60Hz",
            "Nanocrystalline best for broadband CM suppression",
            "DM choke must handle DC bias without saturation",
            "Split-winding reduces interwinding capacitance",
        ],
    },

    "current_transformer": {
        "name": "Current Transformer / Current Sense",
        "description": "Galvanically isolated current measurement",
        "applications": {
            "metering": {"accuracy": "0.1-0.5%", "phase": "<0.5°"},
            "protection": {"accuracy": "1-5%", "saturation_factor": ">20"},
            "control": {"bandwidth": ">100kHz", "accuracy": "1-3%"},
        },
        "core_materials": {
            "metering": "nanocrystalline",  # Low loss, high permeability
            "protection": "silicon_steel",   # High saturation
            "control": "ferrite",            # High frequency
        },
    },

    "pfc_choke": {
        "name": "PFC Boost Inductor",
        "description": "Inductor for power factor correction",
        "modes": {
            "CCM": "Continuous conduction mode - large L, low ripple",
            "CrCM": "Critical conduction mode - variable freq, zero crossing",
            "DCM": "Discontinuous mode - small L, high peak current",
        },
        "typical_topology": "boost",
        "core_materials": {
            "low_power": "ferrite",  # <200W
            "medium_power": "powder_core",  # 200W-2kW (Kool Mu, sendust)
            "high_power": "amorphous",  # >2kW
        },
        "design_tips": [
            "Powder cores have distributed gap - lower fringing EMI",
            "Ferrite needs discrete gap - watch for fringing",
            "DC bias rating critical - check µ vs H curves",
            "Thermal management often limits inductor, not saturation",
        ],
    },
}


# =============================================================================
# TOPOLOGY KNOWLEDGE
# =============================================================================

TOPOLOGIES = {
    "flyback": {
        "name": "Flyback",
        "type": "isolated",
        "power_range": (1, 200),  # Typical watts
        "advantages": [
            "Simple, low component count",
            "Multiple outputs easy",
            "Wide input range",
            "No output inductor",
        ],
        "disadvantages": [
            "High peak currents",
            "Transformer stress",
            "EMI from fast edges",
            "Efficiency limited >150W",
        ],
        "best_for": ["USB chargers", "auxiliary supplies", "LED drivers"],
        "when_to_use": "Power <150W, multiple outputs, cost sensitive",
    },

    "forward": {
        "name": "Forward",
        "type": "isolated",
        "power_range": (50, 500),
        "variants": ["single_switch", "two_switch", "active_clamp"],
        "advantages": [
            "Lower peak currents than flyback",
            "Better transformer utilization",
            "Easier EMI filtering",
        ],
        "disadvantages": [
            "Needs reset winding or clamp",
            "Output inductor required",
            "Core reset limits duty cycle",
        ],
        "best_for": ["Industrial PSU", "telecom", "medium power"],
        "when_to_use": "Power 100-500W, single output, efficiency important",
    },

    "LLC": {
        "name": "LLC Resonant",
        "type": "isolated",
        "power_range": (100, 10000),
        "advantages": [
            "Soft switching (ZVS/ZCS)",
            "High efficiency",
            "Low EMI",
            "High power density",
        ],
        "disadvantages": [
            "Complex control",
            "Narrow gain range",
            "Sensitive to component variation",
            "Needs PFC front-end",
        ],
        "best_for": ["Server PSU", "EV chargers", "high efficiency apps"],
        "when_to_use": "Power >200W, efficiency critical, DC input",
    },

    "buck": {
        "name": "Buck (Step-Down)",
        "type": "non-isolated",
        "power_range": (0.1, 1000),
        "advantages": [
            "Simple, efficient",
            "Continuous output current",
            "Easy to parallel",
        ],
        "disadvantages": [
            "Vout must be < Vin",
            "No isolation",
            "Input current discontinuous",
        ],
        "best_for": ["POL converters", "battery charging", "LED current"],
    },

    "boost": {
        "name": "Boost (Step-Up)",
        "type": "non-isolated",
        "power_range": (1, 5000),
        "advantages": [
            "Step-up capability",
            "Continuous input current",
            "Good for PFC",
        ],
        "disadvantages": [
            "Vout must be > Vin",
            "Output current discontinuous",
            "No short circuit protection inherent",
        ],
        "best_for": ["PFC", "battery boost", "solar MPPT"],
    },

    "phase_shifted_full_bridge": {
        "name": "Phase-Shifted Full Bridge",
        "type": "isolated",
        "power_range": (500, 10000),
        "advantages": [
            "ZVS switching",
            "Handles high power",
            "Bidirectional capable",
        ],
        "disadvantages": [
            "Complex control",
            "Duty cycle loss",
            "Many components",
        ],
        "best_for": ["EV DC-DC", "server PSU", "welding"],
    },
}


# =============================================================================
# MATERIAL GUIDE
# =============================================================================

MATERIALS_GUIDE = {
    "ferrite": {
        "types": {
            "power": {
                "examples": ["3C90", "3C95", "3C97", "N87", "N97", "PC95"],
                "frequency": (20e3, 500e3),
                "applications": ["transformers", "inductors"],
            },
            "high_frequency": {
                "examples": ["3F3", "3F4", "N49", "PC200"],
                "frequency": (500e3, 3e6),
                "applications": ["resonant converters", "GaN designs"],
            },
        },
        "advantages": ["Low cost", "High resistivity", "Many shapes"],
        "disadvantages": ["Low saturation (~400mT)", "Temperature sensitive"],
        "selection_tips": [
            "3C95/N95 - General purpose 100kHz",
            "3C97/N97 - Low loss at 100-300kHz",
            "3F4/N49 - 500kHz-1MHz",
        ],
    },

    "powder_core": {
        "types": {
            "MPP": {
                "permeability": (14, 550),
                "saturation": "1.5T",
                "best_for": "Lowest loss, highest cost",
            },
            "High_Flux": {
                "permeability": (14, 160),
                "saturation": "1.5T",
                "best_for": "DC bias, moderate loss",
            },
            "Kool_Mu": {
                "permeability": (26, 125),
                "saturation": "1.0T",
                "best_for": "Good all-around, PFC",
            },
            "XFlux": {
                "permeability": (26, 60),
                "saturation": "1.6T",
                "best_for": "Highest DC bias, lowest cost",
            },
        },
        "advantages": ["Distributed gap", "High saturation", "DC bias tolerant"],
        "disadvantages": ["Higher loss than ferrite", "Limited shapes"],
        "selection_tips": [
            "Kool Mu for PFC - good balance",
            "High Flux for DC chokes - handles bias",
            "MPP for filters - lowest loss",
        ],
    },

    "nanocrystalline": {
        "properties": {
            "saturation": "1.2T",
            "permeability": (15000, 150000),
            "frequency": (1e3, 1e6),
        },
        "advantages": ["Very high permeability", "Low loss", "Excellent EMI suppression"],
        "disadvantages": ["Brittle", "Limited shapes", "Higher cost"],
        "best_for": ["Common mode chokes", "Current transformers", "High-end EMI filters"],
    },

    "amorphous": {
        "properties": {
            "saturation": "1.56T",
            "frequency": (50, 100e3),
        },
        "advantages": ["High saturation", "Low loss at low frequency"],
        "disadvantages": ["Difficult to cut", "Lower frequency than ferrite"],
        "best_for": ["High power PFC", "Solar inverters", "Medium frequency transformers"],
    },
}


# =============================================================================
# POWDER CORE MATERIAL DATABASE
# =============================================================================
# Steinmetz parameters for core loss calculation: Pv = k * f^alpha * B^beta
# Where Pv is in W/m³, f in Hz, B in Tesla
# Permeability curve: mu_r = mu_i / (a + b * |H/oersted|^c) / 100
# H in A/m, oersted = 79.5775 A/m

POWDER_CORE_MATERIALS = {
    # -------------------------------------------------------------------------
    # MPP (Molypermalloy Powder) - Lowest loss, highest cost
    # -------------------------------------------------------------------------
    "CSC_MPP_26u": {
        "name": "CSC MPP 26µ",
        "family": "MPP",
        "manufacturer": "CSC (Chang Sung)",
        "permeability": 26,
        "saturation_T": 0.75,
        "steinmetz": {"k": 32.0, "alpha": 1.27, "beta": 2.18},
        "permeability_curve": {"a": 0.01, "b": 1.42e-07, "c": 2.030},
        "frequency_range": (10e3, 500e3),
        "applications": ["High Q filters", "Resonant inductors", "Low loss PFC"],
        "notes": "Lowest core loss among powder cores, excellent for high frequency",
    },
    "CSC_MPP_60u": {
        "name": "CSC MPP 60µ",
        "family": "MPP",
        "manufacturer": "CSC (Chang Sung)",
        "permeability": 60,
        "saturation_T": 0.75,
        "steinmetz": {"k": 32.0, "alpha": 1.27, "beta": 2.18},
        "permeability_curve": {"a": 0.01, "b": 1.27e-07, "c": 2.412},
        "frequency_range": (10e3, 500e3),
        "applications": ["Flyback inductors", "Switching regulators"],
    },
    "Magnetics_MPP_60u": {
        "name": "Magnetics MPP 60µ",
        "family": "MPP",
        "manufacturer": "Magnetics Inc",
        "permeability": 60,
        "saturation_T": 0.75,
        "steinmetz": {"k": 52.3, "alpha": 1.15, "beta": 2.47},
        "permeability_curve": {"a": 0.01, "b": 2.033e-07, "c": 2.436},
        "frequency_range": (10e3, 500e3),
        "applications": ["Flyback inductors", "Switching regulators"],
    },
    "CSC_MPP_125u": {
        "name": "CSC MPP 125µ",
        "family": "MPP",
        "manufacturer": "CSC (Chang Sung)",
        "permeability": 125,
        "saturation_T": 0.75,
        "steinmetz": {"k": 17.8, "alpha": 1.35, "beta": 2.03},
        "permeability_curve": {"a": 0.01, "b": 4.07e-07, "c": 2.523},
        "frequency_range": (10e3, 300e3),
        "applications": ["Output filters", "EMI filters"],
    },
    "CSC_MPP_147u": {
        "name": "CSC MPP 147µ",
        "family": "MPP",
        "manufacturer": "CSC (Chang Sung)",
        "permeability": 147,
        "saturation_T": 0.75,
        "steinmetz": {"k": 13.7, "alpha": 1.38, "beta": 2.03},
        "permeability_curve": {"a": 0.01, "b": 7.58e-07, "c": 2.471},
        "frequency_range": (10e3, 300e3),
        "applications": ["Output filters", "Noise filters"],
    },
    "CSC_MPP_160u": {
        "name": "CSC MPP 160µ",
        "family": "MPP",
        "manufacturer": "CSC (Chang Sung)",
        "permeability": 160,
        "saturation_T": 0.75,
        "steinmetz": {"k": 13.7, "alpha": 1.38, "beta": 2.03},
        "permeability_curve": {"a": 0.01, "b": 8.20e-07, "c": 2.495},
        "frequency_range": (10e3, 200e3),
        "applications": ["Line filters", "Smoothing chokes"],
    },
    "CSC_MPP_173u": {
        "name": "CSC MPP 173µ",
        "family": "MPP",
        "manufacturer": "CSC (Chang Sung)",
        "permeability": 173,
        "saturation_T": 0.75,
        "steinmetz": {"k": 13.7, "alpha": 1.38, "beta": 2.03},
        "permeability_curve": {"a": 0.01, "b": 1.03e-06, "c": 2.513},
        "frequency_range": (10e3, 200e3),
        "applications": ["Line filters"],
    },
    "CSC_MPP_200u": {
        "name": "CSC MPP 200µ",
        "family": "MPP",
        "manufacturer": "CSC (Chang Sung)",
        "permeability": 200,
        "saturation_T": 0.75,
        "steinmetz": {"k": 14.7, "alpha": 1.37, "beta": 2.05},
        "permeability_curve": {"a": 0.01, "b": 1.18e-06, "c": 2.524},
        "frequency_range": (10e3, 150e3),
        "applications": ["Line filters", "60Hz transformers"],
    },

    # -------------------------------------------------------------------------
    # HIGH FLUX - Best DC bias, moderate loss
    # -------------------------------------------------------------------------
    "Magnetics_High_Flux_125u": {
        "name": "Magnetics High Flux 125µ",
        "family": "High_Flux",
        "manufacturer": "Magnetics Inc",
        "permeability": 125,
        "saturation_T": 1.5,
        "steinmetz": {"k": 0.0475, "alpha": 1.585, "beta": 1.43},
        "permeability_curve": {"a": 0.01, "b": 1.46e-06, "c": 2.108},
        "frequency_range": (10e3, 200e3),
        "applications": ["DC chokes", "PFC inductors", "Buck/Boost inductors"],
        "notes": "Highest saturation flux density among powder cores",
    },
    "CSC_High_Flux_26u": {
        "name": "CSC High Flux 26µ",
        "family": "High_Flux",
        "manufacturer": "CSC (Chang Sung)",
        "permeability": 26,
        "saturation_T": 1.5,
        "steinmetz": {"k": 52.3, "alpha": 1.09, "beta": 2.25},
        "permeability_curve": {"a": 0.01, "b": 3.41e-08, "c": 2.087},
        "frequency_range": (10e3, 300e3),
        "applications": ["High current DC chokes", "Energy storage"],
    },
    "CSC_High_Flux_60u": {
        "name": "CSC High Flux 60µ",
        "family": "High_Flux",
        "manufacturer": "CSC (Chang Sung)",
        "permeability": 60,
        "saturation_T": 1.5,
        "steinmetz": {"k": 45.6, "alpha": 1.11, "beta": 2.28},
        "permeability_curve": {"a": 0.01, "b": 5.42e-08, "c": 2.326},
        "frequency_range": (10e3, 250e3),
        "applications": ["PFC boost inductors", "Buck converters"],
    },
    "CSC_High_Flux_125u": {
        "name": "CSC High Flux 125µ",
        "family": "High_Flux",
        "manufacturer": "CSC (Chang Sung)",
        "permeability": 125,
        "saturation_T": 1.5,
        "steinmetz": {"k": 27.0, "alpha": 1.23, "beta": 2.17},
        "permeability_curve": {"a": 0.01, "b": 2.09e-07, "c": 2.386},
        "frequency_range": (10e3, 200e3),
        "applications": ["DC-DC converters", "Output chokes"],
    },
    "CSC_High_Flux_147u": {
        "name": "CSC High Flux 147µ",
        "family": "High_Flux",
        "manufacturer": "CSC (Chang Sung)",
        "permeability": 147,
        "saturation_T": 1.5,
        "steinmetz": {"k": 34.4, "alpha": 1.17, "beta": 2.10},
        "permeability_curve": {"a": 0.01, "b": 1.16e-07, "c": 2.619},
        "frequency_range": (10e3, 150e3),
        "applications": ["Smoothing inductors"],
    },
    "CSC_High_Flux_160u": {
        "name": "CSC High Flux 160µ",
        "family": "High_Flux",
        "manufacturer": "CSC (Chang Sung)",
        "permeability": 160,
        "saturation_T": 1.5,
        "steinmetz": {"k": 34.4, "alpha": 1.17, "beta": 2.10},
        "permeability_curve": {"a": 0.01, "b": 2.50e-07, "c": 2.475},
        "frequency_range": (10e3, 150e3),
        "applications": ["Line inductors"],
    },

    # -------------------------------------------------------------------------
    # SENDUST (Kool Mu equivalent) - Good all-around, cost effective
    # -------------------------------------------------------------------------
    "CSC_Sendust_26u": {
        "name": "CSC Sendust 26µ",
        "family": "Sendust",
        "manufacturer": "CSC (Chang Sung)",
        "permeability": 26,
        "saturation_T": 1.0,
        "steinmetz": {"k": 53.4, "alpha": 1.10, "beta": 2.05},
        "permeability_curve": {"a": 0.01, "b": 1.23e-06, "c": 1.697},
        "frequency_range": (10e3, 500e3),
        "applications": ["PFC inductors", "High frequency chokes"],
        "notes": "Good balance of cost, loss, and DC bias capability",
    },
    "CSC_Sendust_60u": {
        "name": "CSC Sendust 60µ",
        "family": "Sendust",
        "manufacturer": "CSC (Chang Sung)",
        "permeability": 60,
        "saturation_T": 1.0,
        "steinmetz": {"k": 62.3, "alpha": 1.10, "beta": 2.21},
        "permeability_curve": {"a": 0.01, "b": 2.75e-06, "c": 1.782},
        "frequency_range": (10e3, 300e3),
        "applications": ["PFC boost inductors", "Output filters"],
    },
    "CSC_Sendust_75u": {
        "name": "CSC Sendust 75µ",
        "family": "Sendust",
        "manufacturer": "CSC (Chang Sung)",
        "permeability": 75,
        "saturation_T": 1.0,
        "steinmetz": {"k": 62.3, "alpha": 1.10, "beta": 2.21},
        "permeability_curve": {"a": 0.01, "b": 4.58e-06, "c": 1.755},
        "frequency_range": (10e3, 250e3),
        "applications": ["General purpose inductors"],
    },
    "CSC_Sendust_90u": {
        "name": "CSC Sendust 90µ",
        "family": "Sendust",
        "manufacturer": "CSC (Chang Sung)",
        "permeability": 90,
        "saturation_T": 1.0,
        "steinmetz": {"k": 62.3, "alpha": 1.10, "beta": 2.21},
        "permeability_curve": {"a": 0.01, "b": 9.54e-06, "c": 1.676},
        "frequency_range": (10e3, 200e3),
        "applications": ["Line filters", "Output chokes"],
    },
    "CSC_Sendust_125u": {
        "name": "CSC Sendust 125µ",
        "family": "Sendust",
        "manufacturer": "CSC (Chang Sung)",
        "permeability": 125,
        "saturation_T": 1.0,
        "steinmetz": {"k": 62.3, "alpha": 1.10, "beta": 2.21},
        "permeability_curve": {"a": 0.01, "b": 2.41e-05, "c": 1.626},
        "frequency_range": (10e3, 150e3),
        "applications": ["EMI filters", "Smoothing chokes"],
    },

    # -------------------------------------------------------------------------
    # MEGA FLUX (XFlux equivalent) - Highest DC bias, lowest cost
    # -------------------------------------------------------------------------
    "CSC_Mega_Flux_26u": {
        "name": "CSC Mega Flux 26µ",
        "family": "Mega_Flux",
        "manufacturer": "CSC (Chang Sung)",
        "permeability": 26,
        "saturation_T": 1.6,
        "steinmetz": {"k": 117.0, "alpha": 1.10, "beta": 2.17},
        "permeability_curve": {"a": 0.01, "b": 9.96e-08, "c": 1.883},
        "frequency_range": (10e3, 200e3),
        "applications": ["High DC bias chokes", "Extreme energy storage"],
        "notes": "Highest saturation, best for extreme DC bias applications",
    },
    "CSC_Mega_Flux_50u": {
        "name": "CSC Mega Flux 50µ",
        "family": "Mega_Flux",
        "manufacturer": "CSC (Chang Sung)",
        "permeability": 50,
        "saturation_T": 1.6,
        "steinmetz": {"k": 108.0, "alpha": 1.10, "beta": 2.15},
        "permeability_curve": {"a": 0.01, "b": 7.35e-08, "c": 2.177},
        "frequency_range": (10e3, 150e3),
        "applications": ["DC-DC converters", "Solar inverters"],
    },
    "CSC_Mega_Flux_60u": {
        "name": "CSC Mega Flux 60µ",
        "family": "Mega_Flux",
        "manufacturer": "CSC (Chang Sung)",
        "permeability": 60,
        "saturation_T": 1.6,
        "steinmetz": {"k": 108.0, "alpha": 1.10, "beta": 2.15},
        "permeability_curve": {"a": 0.01, "b": 3.30e-07, "c": 1.982},
        "frequency_range": (10e3, 150e3),
        "applications": ["EV charger inductors", "High power DC chokes"],
    },
    "CSC_Mega_Flux_75u": {
        "name": "CSC Mega Flux 75µ",
        "family": "Mega_Flux",
        "manufacturer": "CSC (Chang Sung)",
        "permeability": 75,
        "saturation_T": 1.6,
        "steinmetz": {"k": 108.0, "alpha": 1.10, "beta": 2.15},
        "permeability_curve": {"a": 0.01, "b": 1.11e-06, "c": 1.841},
        "frequency_range": (10e3, 120e3),
        "applications": ["Automotive DC-DC", "Welding power supplies"],
    },
    "CSC_Mega_Flux_90u": {
        "name": "CSC Mega Flux 90µ",
        "family": "Mega_Flux",
        "manufacturer": "CSC (Chang Sung)",
        "permeability": 90,
        "saturation_T": 1.6,
        "steinmetz": {"k": 108.0, "alpha": 1.10, "beta": 2.15},
        "permeability_curve": {"a": 0.01, "b": 2.01e-06, "c": 1.828},
        "frequency_range": (10e3, 100e3),
        "applications": ["Line reactors", "Heavy duty chokes"],
    },

    # -------------------------------------------------------------------------
    # FERRITE MATERIALS (for comparison)
    # -------------------------------------------------------------------------
    "EPCOS_N97": {
        "name": "EPCOS N97",
        "family": "Ferrite",
        "manufacturer": "TDK/EPCOS",
        "permeability": 2300,
        "saturation_T": 0.41,
        "steinmetz": {"k": 9.76, "alpha": 1.72, "beta": 2.91},
        "frequency_range": (25e3, 500e3),
        "applications": ["Power transformers", "Flyback converters"],
        "notes": "Low loss ferrite, good for 100-300kHz",
    },
    "TDK_PC95": {
        "name": "TDK PC95",
        "family": "Ferrite",
        "manufacturer": "TDK",
        "permeability": 3300,
        "saturation_T": 0.41,
        "steinmetz": {"k": 11.8, "alpha": 2.00, "beta": 2.64},
        "frequency_range": (25e3, 500e3),
        "applications": ["Power transformers", "High efficiency designs"],
        "notes": "Lowest loss at 100kHz among standard ferrites",
    },
}


def get_powder_core_material(name: str) -> dict:
    """Get material parameters by name."""
    return POWDER_CORE_MATERIALS.get(name, {})


def get_materials_by_family(family: str) -> list[str]:
    """Get all materials in a family (MPP, High_Flux, Sendust, Mega_Flux, Ferrite)."""
    return [k for k, v in POWDER_CORE_MATERIALS.items() if v.get("family") == family]


def suggest_powder_core_material(
    dc_bias_amps: float,
    frequency_hz: float,
    priority: str = "balanced"
) -> list[str]:
    """
    Suggest appropriate powder core materials based on application requirements.

    Args:
        dc_bias_amps: DC bias current (higher = need High Flux or Mega Flux)
        frequency_hz: Operating frequency in Hz
        priority: "low_loss", "high_bias", "cost", or "balanced"

    Returns:
        List of recommended material names, best first
    """
    suggestions = []

    for name, mat in POWDER_CORE_MATERIALS.items():
        if mat.get("family") == "Ferrite":
            continue  # Skip ferrites for powder core suggestion

        freq_range = mat.get("frequency_range", (0, 1e6))
        if not (freq_range[0] <= frequency_hz <= freq_range[1]):
            continue

        # Score based on priority
        score = 0
        family = mat.get("family", "")

        if priority == "low_loss":
            if family == "MPP":
                score = 100
            elif family == "High_Flux":
                score = 60
            elif family == "Sendust":
                score = 70
            elif family == "Mega_Flux":
                score = 40
        elif priority == "high_bias":
            if family == "Mega_Flux":
                score = 100
            elif family == "High_Flux":
                score = 90
            elif family == "Sendust":
                score = 60
            elif family == "MPP":
                score = 40
        elif priority == "cost":
            if family == "Mega_Flux":
                score = 100
            elif family == "Sendust":
                score = 90
            elif family == "High_Flux":
                score = 60
            elif family == "MPP":
                score = 40
        else:  # balanced
            if family == "High_Flux":
                score = 85
            elif family == "Sendust":
                score = 80
            elif family == "MPP":
                score = 70
            elif family == "Mega_Flux":
                score = 75

        # Adjust for DC bias - prefer lower permeability for high bias
        perm = mat.get("permeability", 60)
        if dc_bias_amps > 50:
            if perm <= 60:
                score += 20
        elif dc_bias_amps > 20:
            if perm <= 90:
                score += 10

        suggestions.append((name, score))

    suggestions.sort(key=lambda x: -x[1])
    return [name for name, score in suggestions[:5]]


def calculate_core_loss(
    material_name: str,
    frequency_hz: float,
    flux_density_t: float,
    volume_m3: float
) -> float:
    """
    Calculate core loss using Steinmetz equation.

    Pv = k * f^alpha * B^beta (W/m³)

    Args:
        material_name: Material identifier from POWDER_CORE_MATERIALS
        frequency_hz: Operating frequency in Hz
        flux_density_t: Peak flux density in Tesla
        volume_m3: Core volume in m³

    Returns:
        Core loss in Watts
    """
    mat = POWDER_CORE_MATERIALS.get(material_name)
    if not mat:
        raise ValueError(f"Unknown material: {material_name}")

    steinmetz = mat.get("steinmetz", {})
    k = steinmetz.get("k", 1.0)
    alpha = steinmetz.get("alpha", 1.5)
    beta = steinmetz.get("beta", 2.5)

    # Steinmetz equation: Pv = k * f^alpha * B^beta
    pv = k * (frequency_hz ** alpha) * (flux_density_t ** beta)
    return pv * volume_m3


# =============================================================================
# DESIGN TRADEOFFS
# =============================================================================

TRADEOFFS = {
    "core_size_vs_loss": {
        "description": "Core size vs power loss tradeoff",
        "explanation": """
Smaller core → Higher flux density → More core loss → Hotter

Larger core → Lower flux density → Less loss → Cooler but bigger

The sweet spot depends on:
- Cooling capability (natural convection vs forced air)
- Efficiency requirements
- Size constraints
- Operating temperature

Rule of thumb: Design for 150-200mT at worst case for ferrite.
Higher (250-300mT) acceptable if good cooling available.
        """,
    },

    "frequency_vs_size": {
        "description": "Switching frequency vs magnetics size",
        "explanation": """
Higher frequency → Smaller magnetics BUT:

- More switching loss in MOSFETs
- More AC winding loss (skin effect, proximity effect)
- More EMI to filter
- Core material must support frequency

Typical sweet spots:
- 65-100kHz: Silicon MOSFETs, standard ferrite
- 100-200kHz: High performance Si or SiC
- 200-500kHz: GaN, low-loss ferrite (3F4, N49)
- 500kHz-1MHz: GaN only, specialized cores
        """,
    },

    "gap_vs_inductance": {
        "description": "Air gap vs inductance and saturation",
        "explanation": """
More gap → Lower inductance factor (AL) BUT:
- Higher saturation current (stores more energy)
- More turns needed for same inductance
- More fringing flux (EMI, eddy loss nearby)

Less gap (or no gap):
- Higher AL, fewer turns
- Lower saturation current
- Core material limits energy storage

For energy storage (flyback, PFC): Gap is essential
For transformers (LLC, forward): Minimal or no gap
        """,
    },

    "wire_solid_vs_litz": {
        "description": "Solid wire vs Litz wire selection",
        "explanation": """
Litz wire reduces AC resistance by mitigating skin/proximity effect.

Use Litz when: skin depth < wire radius
Skin depth = 66mm / sqrt(f_kHz) for copper

At 100kHz: δ = 0.21mm → Litz helps for wire > 0.4mm
At 500kHz: δ = 0.09mm → Litz helps for wire > 0.2mm

Litz downsides:
- Lower fill factor (30-40% vs 60%)
- More expensive (3-5x)
- Harder to terminate
- Worse thermal conductivity

Often better to use multiple paralleled smaller solid wires
instead of expensive Litz.
        """,
    },

    "turns_ratio_optimization": {
        "description": "Flyback turns ratio selection",
        "explanation": """
Higher turns ratio (more primary turns per secondary):
- Lower secondary current, smaller rectifier
- Higher primary voltage stress
- Better cross-regulation on multi-output

Lower turns ratio:
- Higher secondary current
- Lower primary voltage stress
- Lower leakage inductance

Optimal ratio balances:
- Duty cycle around 40-50% at low line
- Primary voltage < MOSFET rating
- Manageable secondary current
        """,
    },
}


def get_application_info(app_key: str) -> dict:
    """Get detailed information about an application."""
    return APPLICATIONS.get(app_key, {})


def get_topology_info(topology: str) -> dict:
    """Get information about a topology."""
    return TOPOLOGIES.get(topology, {})


def suggest_topology(power: float, isolated: bool = True, efficiency_priority: bool = False) -> str:
    """Suggest appropriate topology based on requirements."""
    if not isolated:
        return "buck" if power < 100 else "interleaved_buck"

    if power < 50:
        return "flyback"
    elif power < 150:
        return "flyback" if not efficiency_priority else "active_clamp_flyback"
    elif power < 300:
        return "forward" if not efficiency_priority else "LLC"
    else:
        return "LLC" if efficiency_priority else "phase_shifted_full_bridge"


def suggest_core_material(frequency: float, topology: str) -> list[str]:
    """Suggest appropriate core materials."""
    suggestions = []

    if frequency < 100e3:
        suggestions = ["3C90", "3C95", "N87"]
    elif frequency < 300e3:
        suggestions = ["3C95", "3C97", "N95", "N97"]
    elif frequency < 1e6:
        suggestions = ["3F4", "N49", "PC200"]
    else:
        suggestions = ["N49", "4F1"]

    return suggestions

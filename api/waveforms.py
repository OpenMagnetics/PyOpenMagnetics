"""
MAS (Magnetic Agnostic Structure) generator and waveform utilities.

Generates MAS-compliant input structures and waveforms for PyOpenMagnetics.
"""

import math
from typing import Optional, Any


# =============================================================================
# Waveform Generators
# =============================================================================

def triangular_current(i_dc: float, i_ripple_pp: float, duty: float, freq: float) -> dict:
    """Generate triangular current waveform (typical inductor current)."""
    period = 1.0 / freq
    t_on = duty * period
    i_min = i_dc - i_ripple_pp / 2
    i_max = i_dc + i_ripple_pp / 2
    return {"waveform": {"data": [i_min, i_max, i_min], "time": [0, t_on, period]}}


def rectangular_voltage(v_on: float, v_off: float, duty: float, freq: float) -> dict:
    """Generate rectangular voltage waveform."""
    period = 1.0 / freq
    t_on = duty * period
    return {"waveform": {"data": [v_on, v_on, v_off, v_off], "time": [0, t_on, t_on, period]}}


def sinusoidal_current(i_rms: float, freq: float, dc_offset: float = 0.0, num_points: int = 64) -> dict:
    """Generate sinusoidal current waveform."""
    period = 1.0 / freq
    i_peak = i_rms * math.sqrt(2)
    times = [i * period / num_points for i in range(num_points + 1)]
    data = [dc_offset + i_peak * math.sin(2 * math.pi * freq * t) for t in times]
    return {"waveform": {"data": data, "time": times}}


def flyback_primary_current(vin: float, vout: float, pout: float, n: float, lm: float,
                            freq: float, efficiency: float = 0.85, mode: str = "ccm") -> dict:
    """Generate flyback primary winding current waveform."""
    period = 1.0 / freq
    pin = pout / efficiency
    vout_reflected = n * vout
    duty = vout_reflected / (vin + vout_reflected)
    t_on = duty * period

    if mode == "dcm":
        i_pk = math.sqrt(2 * pin / (freq * lm * duty))
        t_reset = 2 * lm * i_pk / vout_reflected
        t_reset = min(t_reset, period - t_on)
        return {"waveform": {"data": [0, i_pk, 0, 0], "time": [0, t_on, t_on + t_reset, period]}}
    else:
        i_avg = pin / vin
        delta_i = (vin * t_on) / lm
        i_min = max(0, i_avg - delta_i / 2)
        i_max = i_avg + delta_i / 2
        return {"waveform": {"data": [i_min, i_max, 0, 0], "time": [0, t_on, t_on, period]}}


def flyback_secondary_current(vin: float, vout: float, iout: float, n: float, lm: float,
                              freq: float, mode: str = "ccm") -> dict:
    """Generate flyback secondary winding current waveform."""
    period = 1.0 / freq
    vout_reflected = n * vout
    duty = vout_reflected / (vin + vout_reflected)
    t_on = duty * period
    t_off = period - t_on
    lm_sec = lm / (n * n)

    if mode == "dcm":
        pout = vout * iout
        pin = pout / 0.85
        i_pri_pk = math.sqrt(2 * pin / (freq * lm * duty))
        i_sec_pk = i_pri_pk * n
        t_reset = min(lm_sec * i_sec_pk / vout, t_off)
        return {"waveform": {"data": [0, 0, i_sec_pk, 0, 0], "time": [0, t_on, t_on, t_on + t_reset, period]}}
    else:
        i_sec_avg = iout / (1 - duty)
        delta_i_sec = (vout * t_off) / lm_sec
        i_sec_max = i_sec_avg + delta_i_sec / 2
        i_sec_min = max(0, i_sec_avg - delta_i_sec / 2)
        return {"waveform": {"data": [0, 0, i_sec_max, i_sec_min], "time": [0, t_on, t_on, period]}}


def buck_inductor_current(vin: float, vout: float, iout: float, inductance: float, freq: float) -> dict:
    """Generate buck converter inductor current waveform."""
    period = 1.0 / freq
    duty = vout / vin
    t_on = duty * period
    delta_i = (vin - vout) * t_on / inductance
    i_min = max(0, iout - delta_i / 2)
    i_max = iout + delta_i / 2
    return {"waveform": {"data": [i_min, i_max, i_min], "time": [0, t_on, period]}}


def buck_inductor_voltage(vin: float, vout: float, freq: float) -> dict:
    """Generate buck converter inductor voltage waveform."""
    period = 1.0 / freq
    duty = vout / vin
    t_on = duty * period
    return {"waveform": {"data": [vin - vout, vin - vout, -vout, -vout], "time": [0, t_on, t_on, period]}}


def boost_inductor_current(vin: float, vout: float, pout: float, inductance: float,
                           freq: float, efficiency: float = 0.9) -> dict:
    """Generate boost converter inductor current waveform."""
    period = 1.0 / freq
    duty = 1 - (vin / vout)
    t_on = duty * period
    pin = pout / efficiency
    i_avg = pin / vin
    delta_i = vin * t_on / inductance
    i_min = max(0, i_avg - delta_i / 2)
    i_max = i_avg + delta_i / 2
    return {"waveform": {"data": [i_min, i_max, i_min], "time": [0, t_on, period]}}


def boost_inductor_voltage(vin: float, vout: float, freq: float) -> dict:
    """Generate boost converter inductor voltage waveform."""
    period = 1.0 / freq
    duty = 1 - (vin / vout)
    t_on = duty * period
    return {"waveform": {"data": [vin, vin, vin - vout, vin - vout], "time": [0, t_on, t_on, period]}}


def boost_inductor_waveforms(
    vin: float,
    vout: float,
    power: float,
    inductance: float,
    frequency: float,
    efficiency: float = 0.9,
) -> dict:
    """
    Calculate complete inductor waveforms for boost converter.

    This function provides detailed waveform analysis including RMS values,
    peak values, and other metrics needed for loss calculation.

    Args:
        vin: Input voltage (V)
        vout: Output voltage (V)
        power: Output power (W)
        inductance: Inductor value (H)
        frequency: Switching frequency (Hz)
        efficiency: Converter efficiency (default 0.9)

    Returns:
        dict with waveform data and calculated metrics:
            - current/voltage waveforms in MAS format
            - i_dc, i_ripple_pp, i_rms, i_peak
            - v_rms, duty_cycle
            - l_critical (boundary conduction inductance)
    """
    period = 1.0 / frequency
    duty = 1 - (vin / vout)
    t_on = duty * period

    # Input power and average current
    pin = power / efficiency
    i_dc = pin / vin

    # Current ripple
    delta_i = vin * t_on / inductance
    i_min = max(0, i_dc - delta_i / 2)
    i_max = i_dc + delta_i / 2

    # RMS current (triangular waveform on DC)
    # I_rms = sqrt(I_dc^2 + (delta_I)^2 / 12)
    i_rms = math.sqrt(i_dc ** 2 + (delta_i ** 2) / 12)

    # Voltage waveform
    v_on = vin           # During switch ON
    v_off = vin - vout   # During switch OFF (negative)

    # RMS voltage
    v_rms = math.sqrt(duty * v_on ** 2 + (1 - duty) * v_off ** 2)

    # Critical inductance for boundary conduction mode (BCM)
    # L_crit = Vin * D * (1-D) / (2 * f * I_out)
    i_out = power / vout
    l_critical = (vin * duty * (1 - duty)) / (2 * frequency * i_out) if i_out > 0 else 0

    # Build MAS-format waveforms
    current_waveform = {"waveform": {"data": [i_min, i_max, i_min], "time": [0, t_on, period]}}
    voltage_waveform = {"waveform": {"data": [v_on, v_on, v_off, v_off], "time": [0, t_on, t_on, period]}}

    return {
        # MAS format waveforms
        "current": current_waveform,
        "voltage": voltage_waveform,

        # Current metrics
        "i_dc": i_dc,
        "i_ripple_pp": delta_i,
        "i_min": i_min,
        "i_max": i_max,
        "i_rms": i_rms,
        "i_peak": i_max,

        # Voltage metrics
        "v_on": v_on,
        "v_off": v_off,
        "v_rms": v_rms,

        # Operating parameters
        "duty_cycle": duty,
        "frequency": frequency,
        "period": period,
        "t_on": t_on,

        # Design parameters
        "l_critical": l_critical,
        "power_in": pin,
        "power_out": power,
        "efficiency": efficiency,
    }


def calculate_critical_inductance_dcm(vin: float, vout: float, i_out: float, frequency: float) -> float:
    """
    Calculate critical inductance for DCM/CCM boundary.

    Below this inductance, the converter operates in DCM.
    Above this inductance, the converter operates in CCM.

    Args:
        vin: Input voltage (V)
        vout: Output voltage (V)
        i_out: Output current (A)
        frequency: Switching frequency (Hz)

    Returns:
        Critical inductance in Henries
    """
    duty = 1 - (vin / vout)
    return (vin * duty * (1 - duty)) / (2 * frequency * i_out)


# =============================================================================
# MAS Structure Generators
# =============================================================================

def generate_design_requirements(
    magnetizing_inductance: float,
    turns_ratios: Optional[list[float]] = None,
    leakage_inductance: Optional[float] = None,
    insulation: Optional[dict] = None,
    max_dimensions: Optional[dict] = None,
    max_temperature: Optional[float] = None,
    name: Optional[str] = None,
    tolerance: float = 0.1
) -> dict:
    """Generate MAS design requirements structure."""
    req: dict[str, Any] = {
        "magnetizingInductance": {
            "nominal": magnetizing_inductance,
            "minimum": magnetizing_inductance * (1 - tolerance),
            "maximum": magnetizing_inductance * (1 + tolerance)
        },
        "turnsRatios": [{"nominal": r} for r in (turns_ratios or [])]
    }
    if leakage_inductance:
        req["leakageInductance"] = {"nominal": leakage_inductance}
    if insulation:
        req["insulation"] = insulation
    if max_dimensions:
        req["maximumDimensions"] = max_dimensions
    if max_temperature:
        req["maximumTemperature"] = {"nominal": max_temperature}
    if name:
        req["name"] = name
    return req


def generate_operating_point(
    frequency: float,
    excitations: list[dict],
    name: str = "Operating Point",
    ambient_temperature: float = 25.0
) -> dict:
    """Generate MAS operating point structure."""
    op: dict[str, Any] = {
        "name": name,
        "conditions": {"ambientTemperature": ambient_temperature},
        "excitationsPerWinding": []
    }
    for exc in excitations:
        exc_entry: dict[str, Any] = {"frequency": frequency}
        if "current" in exc:
            exc_entry["current"] = exc["current"]
        if "voltage" in exc:
            exc_entry["voltage"] = exc["voltage"]
        if "name" in exc:
            exc_entry["name"] = exc["name"]
        op["excitationsPerWinding"].append(exc_entry)
    return op


def generate_insulation_requirements(
    insulation_type: str = "Functional",
    pollution_degree: str = "P2",
    overvoltage_category: str = "OVC-II",
    standards: Optional[list[str]] = None
) -> dict:
    """Generate MAS insulation requirements structure."""
    ins = {"insulationType": insulation_type, "pollutionDegree": pollution_degree,
           "overvoltageCategory": overvoltage_category}
    if standards:
        ins["standards"] = standards
    return ins

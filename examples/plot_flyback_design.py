#!/usr/bin/env python3
"""
Flyback Transformer Design Visualization
=========================================
Generates plots for the 220V AC → 12V @ 1A flyback transformer design.

Note: PyOpenMagnetics plot_* functions are currently placeholders.
This script uses matplotlib to create equivalent visualizations.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon, Circle, Arc
from matplotlib.collections import PatchCollection
import numpy as np
import json

# Try to import PyOpenMagnetics for data
try:
    import PyOpenMagnetics
    HAS_PYOM = True
except ImportError:
    HAS_PYOM = False

# Design parameters from the flyback design
DESIGN = {
    'output_power': 12,  # W
    'input_voltage_min': 222,  # V DC (rectified from 185V AC)
    'input_voltage_max': 375,  # V DC (rectified from 265V AC)
    'output_voltage': 12,  # V
    'output_current': 1.0,  # A
    'switching_freq': 100e3,  # Hz
    'turns_ratio': 12.37,
    'magnetizing_inductance': 800e-6,  # H
    'primary_peak_current': 0.59,  # A
    'duty_cycle_max': 0.45,
    'efficiency': 0.85,
    
    # Core parameters
    'core_shape': 'E 25/13/7',
    'core_material': '3C95',
    'Ae': 51.8e-6,  # m² (effective area)
    'le': 57.8e-3,  # m (effective length)
    'gap': 0.13e-3,  # m
    
    # Winding parameters
    'primary_turns': 45,
    'secondary_turns': 4,
    'secondary_parallels': 2,
    'B_peak': 204e-3,  # T
}


def plot_core_cross_section():
    """Plot E-core cross-section with windings."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    
    # E 25/13/7 approximate dimensions (mm)
    A = 25.0   # Total width
    B = 12.8   # Height
    C = 7.2    # Center leg width
    D = 8.9    # Side leg width / 2
    E = 17.9   # Window width extent
    F = 7.2    # Window height
    
    # Scale for drawing
    scale = 1.0
    
    # Draw E-core (two halves)
    core_color = '#4a4a4a'
    
    # Bottom E-core
    # Base
    ax.add_patch(Rectangle((-A/2, -B/2), A, (B-F)/2, 
                           facecolor=core_color, edgecolor='black', linewidth=1.5))
    # Left leg
    ax.add_patch(Rectangle((-A/2, -B/2 + (B-F)/2), D/2, F, 
                           facecolor=core_color, edgecolor='black', linewidth=1.5))
    # Center leg (with gap)
    gap_mm = DESIGN['gap'] * 1000
    ax.add_patch(Rectangle((-C/2, -B/2 + (B-F)/2), C, F/2 - gap_mm/2, 
                           facecolor=core_color, edgecolor='black', linewidth=1.5))
    # Right leg
    ax.add_patch(Rectangle((A/2 - D/2, -B/2 + (B-F)/2), D/2, F, 
                           facecolor=core_color, edgecolor='black', linewidth=1.5))
    
    # Top E-core (mirror)
    # Top base
    ax.add_patch(Rectangle((-A/2, B/2 - (B-F)/2), A, (B-F)/2, 
                           facecolor=core_color, edgecolor='black', linewidth=1.5))
    # Left leg
    ax.add_patch(Rectangle((-A/2, -B/2 + (B-F)/2 + F), D/2, -(F), 
                           facecolor=core_color, edgecolor='black', linewidth=1.5))
    # Center leg (with gap)
    ax.add_patch(Rectangle((-C/2, B/2 - (B-F)/2), C, -(F/2 - gap_mm/2), 
                           facecolor=core_color, edgecolor='black', linewidth=1.5))
    # Right leg
    ax.add_patch(Rectangle((A/2 - D/2, -B/2 + (B-F)/2 + F), D/2, -(F), 
                           facecolor=core_color, edgecolor='black', linewidth=1.5))
    
    # Draw gap indication
    ax.annotate('', xy=(C/2 + 1, gap_mm/2), xytext=(C/2 + 1, -gap_mm/2),
                arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax.text(C/2 + 2, 0, f'Gap: {DESIGN["gap"]*1000:.2f}mm', fontsize=10, color='red', va='center')
    
    # Draw windings in the window
    window_left = -A/2 + D/2 + 0.5
    window_right = -C/2 - 0.5
    window_bottom = -B/2 + (B-F)/2 + 0.5
    window_top = B/2 - (B-F)/2 - 0.5
    
    # Primary winding (closer to center leg)
    primary_color = '#e74c3c'
    primary_width = (window_right - window_left) * 0.6
    ax.add_patch(Rectangle((window_right - primary_width, window_bottom), 
                           primary_width, window_top - window_bottom,
                           facecolor=primary_color, edgecolor='darkred', 
                           linewidth=1, alpha=0.7))
    ax.text(window_right - primary_width/2, 0, f'Pri\n{DESIGN["primary_turns"]}T', 
            fontsize=9, ha='center', va='center', color='white', fontweight='bold')
    
    # Secondary winding (outer)
    secondary_color = '#3498db'
    secondary_width = (window_right - window_left) * 0.35
    ax.add_patch(Rectangle((window_left, window_bottom), 
                           secondary_width, window_top - window_bottom,
                           facecolor=secondary_color, edgecolor='darkblue', 
                           linewidth=1, alpha=0.7))
    ax.text(window_left + secondary_width/2, 0, f'Sec\n{DESIGN["secondary_turns"]}T×{DESIGN["secondary_parallels"]}', 
            fontsize=9, ha='center', va='center', color='white', fontweight='bold')
    
    # Mirror windings on right side
    window_left_r = C/2 + 0.5
    window_right_r = A/2 - D/2 - 0.5
    
    ax.add_patch(Rectangle((window_left_r, window_bottom), 
                           primary_width, window_top - window_bottom,
                           facecolor=primary_color, edgecolor='darkred', 
                           linewidth=1, alpha=0.7))
    ax.add_patch(Rectangle((window_right_r - secondary_width, window_bottom), 
                           secondary_width, window_top - window_bottom,
                           facecolor=secondary_color, edgecolor='darkblue', 
                           linewidth=1, alpha=0.7))
    
    ax.set_xlim(-A/2 - 5, A/2 + 10)
    ax.set_ylim(-B/2 - 3, B/2 + 3)
    ax.set_aspect('equal')
    ax.set_xlabel('Width (mm)', fontsize=11)
    ax.set_ylabel('Height (mm)', fontsize=11)
    ax.set_title(f'E 25/13/7 Core Cross-Section with Windings\nMaterial: {DESIGN["core_material"]}', 
                 fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # Legend
    legend_elements = [
        patches.Patch(facecolor=core_color, edgecolor='black', label='Ferrite Core'),
        patches.Patch(facecolor=primary_color, alpha=0.7, label=f'Primary: {DESIGN["primary_turns"]} turns'),
        patches.Patch(facecolor=secondary_color, alpha=0.7, label=f'Secondary: {DESIGN["secondary_turns"]}T × {DESIGN["secondary_parallels"]}'),
    ]
    ax.legend(handles=legend_elements, loc='upper right')
    
    return fig


def plot_waveforms():
    """Plot primary current and voltage waveforms."""
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    
    # Time parameters
    T = 1 / DESIGN['switching_freq']  # Period
    t = np.linspace(0, 3*T, 1000)  # 3 periods
    
    # Duty cycle and timing
    D = DESIGN['duty_cycle_max']
    ton = D * T
    
    # Primary voltage (Vin during on, -Vout*n during off)
    Vin = DESIGN['input_voltage_min']
    Vout = DESIGN['output_voltage']
    n = DESIGN['turns_ratio']
    
    V_primary = np.zeros_like(t)
    I_primary = np.zeros_like(t)
    I_secondary = np.zeros_like(t)
    
    Ipk = DESIGN['primary_peak_current']
    
    for i, ti in enumerate(t):
        t_in_period = ti % T
        if t_in_period < ton:
            # Switch ON - energy storage phase
            V_primary[i] = Vin
            I_primary[i] = Ipk * (t_in_period / ton)
            I_secondary[i] = 0
        else:
            # Switch OFF - energy transfer phase
            t_off = t_in_period - ton
            toff_duration = T - ton
            V_primary[i] = -Vout * n
            I_primary[i] = 0
            # Secondary current ramps down
            I_secondary[i] = Ipk * n * (1 - t_off / toff_duration)
            if I_secondary[i] < 0:
                I_secondary[i] = 0
    
    # Plot primary voltage
    axes[0].plot(t * 1e6, V_primary, 'b-', linewidth=2)
    axes[0].axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    axes[0].fill_between(t * 1e6, V_primary, alpha=0.3)
    axes[0].set_ylabel('Primary Voltage (V)', fontsize=11)
    axes[0].set_title('Flyback Converter Waveforms @ Low Line (222V DC)', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    axes[0].set_ylim(-200, 300)
    axes[0].annotate(f'Vin = {Vin}V', xy=(ton*1e6/2, Vin), fontsize=10,
                     ha='center', va='bottom')
    axes[0].annotate(f'-Vout×n = {-Vout*n:.0f}V', xy=((ton + (T-ton)/2)*1e6, -Vout*n), 
                     fontsize=10, ha='center', va='top')
    
    # Plot primary current
    axes[1].plot(t * 1e6, I_primary, 'r-', linewidth=2)
    axes[1].fill_between(t * 1e6, I_primary, alpha=0.3, color='red')
    axes[1].set_ylabel('Primary Current (A)', fontsize=11)
    axes[1].grid(True, alpha=0.3)
    axes[1].set_ylim(-0.1, Ipk * 1.2)
    axes[1].annotate(f'Ipk = {Ipk:.2f}A', xy=(ton*1e6, Ipk), fontsize=10,
                     ha='right', va='bottom')
    
    # Plot secondary current
    axes[2].plot(t * 1e6, I_secondary, 'g-', linewidth=2)
    axes[2].fill_between(t * 1e6, I_secondary, alpha=0.3, color='green')
    axes[2].set_ylabel('Secondary Current (A)', fontsize=11)
    axes[2].set_xlabel('Time (µs)', fontsize=11)
    axes[2].grid(True, alpha=0.3)
    axes[2].set_ylim(-0.5, Ipk * n * 1.2)
    axes[2].annotate(f'Is,pk = {Ipk*n:.1f}A', xy=(ton*1e6, Ipk*n), fontsize=10,
                     ha='left', va='bottom')
    
    # Add switch state annotations
    for ax in axes:
        for period in range(3):
            ax.axvline(x=period*T*1e6, color='purple', linestyle=':', alpha=0.5)
            ax.axvline(x=(period*T + ton)*1e6, color='orange', linestyle=':', alpha=0.5)
    
    plt.tight_layout()
    return fig


def plot_bh_curve():
    """Plot B-H operating trajectory."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    
    # 3C95 material approximate B-H curve (simplified)
    # Saturation around 530mT at 25°C, 410mT at 100°C
    H_max = 1500  # A/m
    H = np.linspace(-H_max, H_max, 500)
    
    # Simplified tanh model for B-H curve
    Bsat = 0.53  # T at 25°C
    a = 200  # Shape parameter
    B_material = Bsat * np.tanh(H / a)
    
    # Plot material B-H curve
    ax.plot(H, B_material * 1000, 'b-', linewidth=2, label='3C95 Material (25°C)', alpha=0.5)
    
    # Operating point trajectory
    # With gap, the effective permeability is much lower
    # B = µ0 * µeff * H, where µeff ≈ le / (lg * µr + le/µr) for gapped core
    µ0 = 4 * np.pi * 1e-7
    µr = 3000  # Approximate initial permeability of 3C95
    le = DESIGN['le']
    lg = DESIGN['gap']
    
    # Reluctance model: B = µ0 * N * I / (le/µr + lg)
    # H_eff = N * I / le (for the core material)
    
    B_peak = DESIGN['B_peak']
    Np = DESIGN['primary_turns']
    Ipk = DESIGN['primary_peak_current']
    
    # Operating trajectory (simplified - linear due to gap dominance)
    H_op = np.linspace(0, Np * Ipk / le, 100)
    B_op = np.linspace(0, B_peak, 100)
    
    ax.plot(H_op, B_op * 1000, 'r-', linewidth=3, label='Operating Trajectory')
    ax.scatter([H_op[-1]], [B_op[-1] * 1000], color='red', s=100, zorder=5)
    ax.annotate(f'B_peak = {B_peak*1000:.0f} mT', 
                xy=(H_op[-1], B_op[-1]*1000), 
                xytext=(H_op[-1]+100, B_op[-1]*1000+50),
                fontsize=11, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color='red'))
    
    # Saturation limit lines
    ax.axhline(y=530, color='orange', linestyle='--', linewidth=2, label='Bsat @ 25°C (530mT)')
    ax.axhline(y=410, color='red', linestyle='--', linewidth=2, label='Bsat @ 100°C (410mT)')
    
    # Safe operating region
    ax.fill_between([0, H_max], [0, 0], [300, 300], alpha=0.1, color='green', label='Safe Region (<300mT)')
    
    ax.set_xlim(0, H_max)
    ax.set_ylim(0, 600)
    ax.set_xlabel('Magnetic Field Intensity H (A/m)', fontsize=12)
    ax.set_ylabel('Magnetic Flux Density B (mT)', fontsize=12)
    ax.set_title('B-H Operating Point\n3C95 Ferrite with 0.13mm Gap', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='lower right')
    
    return fig


def plot_design_summary():
    """Create a visual summary of the design parameters."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 1. Power flow diagram (top-left)
    ax = axes[0, 0]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    
    # Input block
    ax.add_patch(FancyBboxPatch((0.5, 2), 2, 2, boxstyle="round,pad=0.1",
                                facecolor='#3498db', edgecolor='black', linewidth=2))
    ax.text(1.5, 3, f'AC Input\n185-265V\n50/60Hz', ha='center', va='center', 
            fontsize=10, color='white', fontweight='bold')
    
    # Rectifier block
    ax.add_patch(FancyBboxPatch((3, 2), 1.5, 2, boxstyle="round,pad=0.1",
                                facecolor='#9b59b6', edgecolor='black', linewidth=2))
    ax.text(3.75, 3, f'Rectifier\n+Filter', ha='center', va='center', 
            fontsize=9, color='white', fontweight='bold')
    
    # Transformer block
    ax.add_patch(FancyBboxPatch((5, 1.5), 2, 3, boxstyle="round,pad=0.1",
                                facecolor='#e74c3c', edgecolor='black', linewidth=2))
    ax.text(6, 3, f'Flyback\nTransformer\nE25/13/7\n3C95', ha='center', va='center', 
            fontsize=9, color='white', fontweight='bold')
    
    # Output block
    ax.add_patch(FancyBboxPatch((7.5, 2), 2, 2, boxstyle="round,pad=0.1",
                                facecolor='#27ae60', edgecolor='black', linewidth=2))
    ax.text(8.5, 3, f'Output\n12V @ 1A\n12W', ha='center', va='center', 
            fontsize=10, color='white', fontweight='bold')
    
    # Arrows
    ax.annotate('', xy=(3, 3), xytext=(2.5, 3),
                arrowprops=dict(arrowstyle='->', lw=2))
    ax.annotate('', xy=(5, 3), xytext=(4.5, 3),
                arrowprops=dict(arrowstyle='->', lw=2))
    ax.annotate('', xy=(7.5, 3), xytext=(7, 3),
                arrowprops=dict(arrowstyle='->', lw=2))
    
    ax.text(5, 0.8, f'f_sw = 100 kHz | η = 85%', ha='center', fontsize=11)
    ax.set_title('Power Flow Diagram', fontsize=14, fontweight='bold')
    ax.axis('off')
    
    # 2. Electrical parameters table (top-right)
    ax = axes[0, 1]
    ax.axis('off')
    
    table_data = [
        ['Parameter', 'Value', 'Unit'],
        ['Output Power', '12', 'W'],
        ['Switching Freq', '100', 'kHz'],
        ['Turns Ratio', '12.37:1', '-'],
        ['Magnetizing L', '800', 'µH'],
        ['Primary Ipk', '0.59', 'A'],
        ['Max Duty Cycle', '45', '%'],
        ['B_peak', '204', 'mT'],
    ]
    
    table = ax.table(cellText=table_data, loc='center', cellLoc='center',
                     colWidths=[0.4, 0.3, 0.2])
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.2, 1.8)
    
    # Style header row
    for j in range(3):
        table[(0, j)].set_facecolor('#34495e')
        table[(0, j)].set_text_props(color='white', fontweight='bold')
    
    ax.set_title('Electrical Parameters', fontsize=14, fontweight='bold', pad=20)
    
    # 3. Core parameters (bottom-left)
    ax = axes[1, 0]
    ax.axis('off')
    
    core_data = [
        ['Core Parameter', 'Value'],
        ['Shape', 'E 25/13/7'],
        ['Material', '3C95 (Ferroxcube)'],
        ['Effective Area (Ae)', '51.8 mm²'],
        ['Effective Length (le)', '57.8 mm'],
        ['Air Gap', '0.13 mm'],
        ['AL Value', '395 nH/turn²'],
    ]
    
    table2 = ax.table(cellText=core_data, loc='center', cellLoc='center',
                      colWidths=[0.5, 0.4])
    table2.auto_set_font_size(False)
    table2.set_fontsize(11)
    table2.scale(1.2, 1.8)
    
    for j in range(2):
        table2[(0, j)].set_facecolor('#8e44ad')
        table2[(0, j)].set_text_props(color='white', fontweight='bold')
    
    ax.set_title('Core Specifications', fontsize=14, fontweight='bold', pad=20)
    
    # 4. Winding parameters (bottom-right)
    ax = axes[1, 1]
    ax.axis('off')
    
    winding_data = [
        ['Winding', 'Turns', 'Wire', 'Current'],
        ['Primary', '45', 'Ø0.35mm', '0.59A pk'],
        ['Secondary', '4 × 2', 'Ø0.6mm', '7.3A pk'],
    ]
    
    table3 = ax.table(cellText=winding_data, loc='center', cellLoc='center',
                      colWidths=[0.25, 0.2, 0.25, 0.25])
    table3.auto_set_font_size(False)
    table3.set_fontsize(11)
    table3.scale(1.2, 2.0)
    
    for j in range(4):
        table3[(0, j)].set_facecolor('#16a085')
        table3[(0, j)].set_text_props(color='white', fontweight='bold')
    
    ax.set_title('Winding Specifications', fontsize=14, fontweight='bold', pad=20)
    
    plt.suptitle('Flyback Transformer Design Summary\n220V AC → 12V @ 1A', 
                 fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    return fig


def main():
    """Generate all design plots."""
    print("=" * 60)
    print(" FLYBACK TRANSFORMER DESIGN VISUALIZATION")
    print(" 220V AC → 12V @ 1A (12W)")
    print("=" * 60)
    print()
    
    # Generate plots
    print("Generating plots...")
    
    # 1. Design Summary
    print("  [1/4] Design summary...")
    fig1 = plot_design_summary()
    fig1.savefig('/home/alf/OpenMagnetics/PyMKF/examples/flyback_summary.png', 
                 dpi=150, bbox_inches='tight', facecolor='white')
    
    # 2. Core cross-section
    print("  [2/4] Core cross-section...")
    fig2 = plot_core_cross_section()
    fig2.savefig('/home/alf/OpenMagnetics/PyMKF/examples/flyback_core.png', 
                 dpi=150, bbox_inches='tight', facecolor='white')
    
    # 3. Waveforms
    print("  [3/4] Operating waveforms...")
    fig3 = plot_waveforms()
    fig3.savefig('/home/alf/OpenMagnetics/PyMKF/examples/flyback_waveforms.png', 
                 dpi=150, bbox_inches='tight', facecolor='white')
    
    # 4. B-H curve
    print("  [4/4] B-H operating point...")
    fig4 = plot_bh_curve()
    fig4.savefig('/home/alf/OpenMagnetics/PyMKF/examples/flyback_bh_curve.png', 
                 dpi=150, bbox_inches='tight', facecolor='white')
    
    print()
    print("=" * 60)
    print("PLOTS SAVED:")
    print("  • flyback_summary.png   - Design overview")
    print("  • flyback_core.png      - Core cross-section")
    print("  • flyback_waveforms.png - Current/voltage waveforms")
    print("  • flyback_bh_curve.png  - B-H operating trajectory")
    print("=" * 60)
    
    # Display plots
    plt.show()


if __name__ == '__main__':
    main()

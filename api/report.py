"""
PyOpenMagnetics Design Report Generator

Generates comprehensive visual reports for magnetic component designs
using matplotlib. Includes:
- Pareto front analysis
- Parallel coordinate plots
- Radar charts for multi-objective comparison
- Loss breakdown visualizations
- Design ranking tables
"""

import os
import json
from typing import List, Optional, Dict, Any
from dataclasses import dataclass


def _ensure_matplotlib():
    """Lazily import matplotlib with Agg backend."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    return plt, np


def generate_design_report(
    results: List[Any],
    output_dir: str,
    title: str = "Magnetic Design Report",
    specs: Optional[Dict[str, Any]] = None,
    verbose: bool = False
) -> str:
    """
    Generate a comprehensive design report with multiple visualizations.

    Args:
        results: List of DesignResult objects from Design.solve()
        output_dir: Directory to save report files
        title: Report title
        specs: Optional design specifications dict
        verbose: Print progress messages

    Returns:
        Path to the generated report image
    """
    plt, np = _ensure_matplotlib()
    os.makedirs(output_dir, exist_ok=True)

    if not results:
        if verbose:
            print("[No results to generate report]")
        return ""

    # Convert to report data
    report_data = _extract_report_data(results)

    # Generate main report (2x3 grid)
    fig = plt.figure(figsize=(18, 12))
    fig.suptitle(title, fontsize=16, fontweight='bold', y=0.98)

    gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.25,
                          left=0.05, right=0.95, top=0.92, bottom=0.08)

    # Row 1
    ax1 = fig.add_subplot(gs[0, 0])
    _plot_pareto_front(ax1, report_data, plt, np)

    ax2 = fig.add_subplot(gs[0, 1])
    _plot_loss_breakdown_stacked(ax2, report_data, plt)

    ax3 = fig.add_subplot(gs[0, 2])
    _plot_loss_pie(ax3, report_data[0], plt)

    # Row 2
    ax4 = fig.add_subplot(gs[1, 0], projection='polar')
    _plot_radar_chart(ax4, report_data[:min(5, len(report_data))], plt, np)

    ax5 = fig.add_subplot(gs[1, 1])
    _plot_ranking_bars(ax5, report_data, plt)

    ax6 = fig.add_subplot(gs[1, 2])
    _plot_summary_card(ax6, report_data[0], specs, plt)

    report_path = os.path.join(output_dir, "design_report.png")
    plt.savefig(report_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()

    if verbose:
        print(f"[Design report saved to {report_path}]")

    # Generate additional plots
    _generate_pareto_detailed(report_data, output_dir, plt, np, verbose)
    _generate_volume_loss_pareto(report_data, output_dir, plt, np, verbose)
    _generate_parallel_coordinates(report_data, output_dir, plt, np, verbose)
    _generate_heatmap(report_data, output_dir, plt, np, verbose)
    _save_json_summary(report_data, output_dir, specs, verbose)

    return report_path


def _extract_report_data(results: List[Any]) -> List[dict]:
    """Extract report data from DesignResult objects."""
    report_data = []
    for i, r in enumerate(results):
        height = getattr(r, 'height_mm', 0) or 0
        width = getattr(r, 'width_mm', 0) or 0
        depth = getattr(r, 'depth_mm', 0) or 0
        volume = (height * width * depth) / 1000.0 if height and width and depth else 0
        report_data.append({
            "rank": i + 1,
            "core": getattr(r, 'core', 'Unknown'),
            "material": getattr(r, 'material', 'Unknown'),
            "primary_turns": getattr(r, 'primary_turns', 0),
            "primary_wire": getattr(r, 'primary_wire', 'Unknown'),
            "air_gap_mm": getattr(r, 'air_gap_mm', 0),
            "core_loss_w": getattr(r, 'core_loss_w', 0),
            "copper_loss_w": getattr(r, 'copper_loss_w', 0),
            "total_loss_w": getattr(r, 'total_loss_w', 0),
            "temp_rise_c": getattr(r, 'temp_rise_c', 0),
            "height_mm": height,
            "width_mm": width,
            "depth_mm": depth,
            "volume_cm3": volume,
            "weight_g": getattr(r, 'weight_g', 0) or 0,
        })
    return report_data


def _plot_pareto_front(ax, data: list, plt, np):
    """Plot Pareto front: Core Loss vs Copper Loss."""
    core_losses = np.array([d['core_loss_w'] for d in data])
    copper_losses = np.array([d['copper_loss_w'] for d in data])
    total_losses = np.array([d['total_loss_w'] for d in data])

    # Size points by inverse of total loss (better = bigger)
    if total_losses.max() > 0:
        sizes = 200 * (1 - (total_losses - total_losses.min()) /
                       (total_losses.max() - total_losses.min() + 0.001)) + 50
    else:
        sizes = np.full_like(total_losses, 100)

    # Color by rank
    colors = plt.cm.RdYlGn_r(np.linspace(0, 1, len(data)))

    ax.scatter(core_losses, copper_losses, s=sizes, c=colors,
               edgecolors='black', linewidths=1, alpha=0.8)

    # Mark Pareto-optimal points
    pareto_mask = _find_pareto_front(core_losses, copper_losses)
    if pareto_mask.sum() > 1:
        pareto_core = core_losses[pareto_mask]
        pareto_copper = copper_losses[pareto_mask]
        # Sort for line drawing
        sort_idx = np.argsort(pareto_core)
        ax.plot(pareto_core[sort_idx], pareto_copper[sort_idx],
                'b--', alpha=0.5, linewidth=2, label='Pareto Front')

    # Annotate top 3
    for i in range(min(3, len(data))):
        ax.annotate(f"#{i+1}", (core_losses[i], copper_losses[i]),
                   textcoords="offset points", xytext=(5, 5),
                   fontsize=9, fontweight='bold')

    ax.set_xlabel('Core Loss (W)', fontsize=10)
    ax.set_ylabel('Copper Loss (W)', fontsize=10)
    ax.set_title('Pareto Front Analysis', fontsize=11, fontweight='bold')
    ax.grid(True, alpha=0.3)
    # Only show legend if there are labeled artists
    handles, labels = ax.get_legend_handles_labels()
    if labels:
        ax.legend(loc='upper right', fontsize=8)


def _find_pareto_front(x, y):
    """Find Pareto-optimal points (minimize both objectives)."""
    import numpy as np
    n = len(x)
    pareto = np.ones(n, dtype=bool)
    for i in range(n):
        for j in range(n):
            if i != j:
                if x[j] <= x[i] and y[j] <= y[i] and (x[j] < x[i] or y[j] < y[i]):
                    pareto[i] = False
                    break
    return pareto


def _plot_loss_breakdown_stacked(ax, data: list, plt):
    """Plot stacked bar chart of loss components."""
    cores = [f"#{d['rank']}" for d in data]
    core_losses = [d['core_loss_w'] for d in data]
    copper_losses = [d['copper_loss_w'] for d in data]

    x = range(len(cores))
    ax.bar(x, core_losses, label='Core Loss', color='#e74c3c', edgecolor='white')
    ax.bar(x, copper_losses, bottom=core_losses, label='Copper Loss',
           color='#3498db', edgecolor='white')

    ax.set_xticks(x)
    ax.set_xticklabels(cores, fontsize=9)
    ax.set_ylabel('Loss (W)', fontsize=10)
    ax.set_title('Loss Breakdown by Design', fontsize=11, fontweight='bold')
    ax.legend(loc='upper right', fontsize=8)
    ax.grid(axis='y', alpha=0.3)

    # Add total labels
    for i, (c, cu) in enumerate(zip(core_losses, copper_losses)):
        ax.text(i, c + cu + 0.02 * max([c + cu for c, cu in zip(core_losses, copper_losses)]),
                f'{c+cu:.2f}W', ha='center', fontsize=8, fontweight='bold')


def _plot_loss_pie(ax, best: dict, plt):
    """Plot pie chart for best design."""
    core_loss = best['core_loss_w']
    copper_loss = best['copper_loss_w']

    if core_loss + copper_loss < 0.001:
        ax.text(0.5, 0.5, 'No loss data', ha='center', va='center',
                transform=ax.transAxes, fontsize=12)
        ax.axis('off')
        return

    sizes = [core_loss, copper_loss]
    labels = [f'Core\n{core_loss:.2f}W', f'Copper\n{copper_loss:.2f}W']
    colors = ['#e74c3c', '#3498db']
    explode = (0.05, 0)

    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors, explode=explode,
        autopct='%1.1f%%', startangle=90, textprops={'fontsize': 9}
    )
    for autotext in autotexts:
        autotext.set_fontweight('bold')

    ax.set_title(f'Best Design Loss Split\n({best["core"]})',
                 fontsize=11, fontweight='bold')


def _plot_radar_chart(ax, data: list, plt, np):
    """Plot radar chart comparing top designs on multiple metrics."""
    if len(data) < 2:
        ax.text(0.5, 0.5, 'Need 2+ designs\nfor radar chart',
                ha='center', va='center', transform=ax.transAxes)
        ax.axis('off')
        return

    # Metrics to compare (normalized 0-1, lower is better for losses)
    categories = ['Core Loss', 'Copper Loss', 'Total Loss', 'Turns', 'Gap']
    N = len(categories)

    # Extract and normalize data
    metrics = {
        'Core Loss': [d['core_loss_w'] for d in data],
        'Copper Loss': [d['copper_loss_w'] for d in data],
        'Total Loss': [d['total_loss_w'] for d in data],
        'Turns': [d['primary_turns'] for d in data],
        'Gap': [d['air_gap_mm'] for d in data],
    }

    # Normalize each metric (invert so lower=better becomes higher on chart)
    normalized = {}
    for key, values in metrics.items():
        vmin, vmax = min(values), max(values)
        if vmax > vmin:
            # Invert: best (lowest) becomes 1, worst becomes 0
            normalized[key] = [1 - (v - vmin) / (vmax - vmin) for v in values]
        else:
            normalized[key] = [0.5] * len(values)

    # Setup radar chart
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]  # Complete the loop

    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=8)

    # Plot each design
    colors = plt.cm.Set2(np.linspace(0, 1, len(data)))
    for i, d in enumerate(data):
        values = [normalized[cat][i] for cat in categories]
        values += values[:1]
        ax.plot(angles, values, 'o-', linewidth=2, color=colors[i],
                label=f"#{d['rank']}: {d['core'][:10]}")
        ax.fill(angles, values, alpha=0.1, color=colors[i])

    ax.set_ylim(0, 1)
    ax.set_title('Multi-Objective Comparison', fontsize=11, fontweight='bold', y=1.08)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1), fontsize=7)


def _plot_ranking_bars(ax, data: list, plt):
    """Plot horizontal bar chart ranking all designs."""
    labels = [f"#{d['rank']}: {d['core'][:12]}" for d in data]
    losses = [d['total_loss_w'] for d in data]

    colors = ['#2ecc71' if i == 0 else '#3498db' if i < 3 else '#95a5a6'
              for i in range(len(data))]

    bars = ax.barh(range(len(labels)), losses, color=colors, edgecolor='white')
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel('Total Loss (W)', fontsize=10)
    ax.set_title('Design Ranking', fontsize=11, fontweight='bold')
    ax.invert_yaxis()
    ax.grid(axis='x', alpha=0.3)

    # Value labels
    max_loss = max(losses) if losses else 1
    for bar, loss in zip(bars, losses):
        ax.text(bar.get_width() + max_loss * 0.02, bar.get_y() + bar.get_height()/2,
                f'{loss:.2f}W', va='center', fontsize=9)


def _plot_summary_card(ax, best: dict, specs: Optional[dict], plt):
    """Plot summary card for best design."""
    ax.axis('off')

    lines = [
        ("RECOMMENDED DESIGN", 'bold', 14, '#2c3e50'),
        ("", 'normal', 6, 'black'),
        (f"Core: {best['core']}", 'bold', 11, '#27ae60'),
        (f"Material: {best['material']}", 'normal', 11, 'black'),
        (f"Primary: {best['primary_turns']}T", 'normal', 11, 'black'),
        (f"Air Gap: {best['air_gap_mm']:.2f} mm", 'normal', 11, 'black'),
        ("", 'normal', 6, 'black'),
        (f"Core Loss: {best['core_loss_w']:.3f} W", 'normal', 10, '#e74c3c'),
        (f"Copper Loss: {best['copper_loss_w']:.3f} W", 'normal', 10, '#3498db'),
        (f"Total Loss: {best['total_loss_w']:.3f} W", 'bold', 12, '#2c3e50'),
        ("", 'normal', 6, 'black'),
        (f"Temp Rise: ~{best['temp_rise_c']:.0f} C", 'normal', 10,
         '#e74c3c' if best['temp_rise_c'] > 40 else '#27ae60'),
    ]

    y_pos = 0.95
    for text, weight, size, color in lines:
        ax.text(0.08, y_pos, text, transform=ax.transAxes,
                fontsize=size, fontweight=weight, color=color,
                verticalalignment='top', fontfamily='sans-serif')
        y_pos -= 0.075 if size >= 10 else 0.05

    # Border
    rect = plt.Rectangle((0.02, 0.02), 0.96, 0.96, fill=False,
                          edgecolor='#27ae60', linewidth=3,
                          transform=ax.transAxes)
    ax.add_patch(rect)


def _generate_pareto_detailed(data: list, output_dir: str, plt, np, verbose: bool):
    """Generate detailed Pareto analysis plot."""
    if len(data) < 2:
        return

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle('Detailed Pareto Analysis', fontsize=14, fontweight='bold')

    core_losses = np.array([d['core_loss_w'] for d in data])
    copper_losses = np.array([d['copper_loss_w'] for d in data])
    total_losses = np.array([d['total_loss_w'] for d in data])
    turns = np.array([d['primary_turns'] for d in data])

    # Plot 1: Core vs Copper Loss
    ax1 = axes[0]
    scatter = ax1.scatter(core_losses, copper_losses, c=total_losses,
                         cmap='RdYlGn_r', s=100, edgecolors='black')
    plt.colorbar(scatter, ax=ax1, label='Total Loss (W)')
    ax1.set_xlabel('Core Loss (W)')
    ax1.set_ylabel('Copper Loss (W)')
    ax1.set_title('Core vs Copper Loss')
    ax1.grid(True, alpha=0.3)

    # Plot 2: Total Loss vs Turns
    ax2 = axes[1]
    scatter = ax2.scatter(turns, total_losses, c=range(len(data)),
                         cmap='viridis', s=100, edgecolors='black')
    plt.colorbar(scatter, ax=ax2, label='Rank')
    ax2.set_xlabel('Primary Turns')
    ax2.set_ylabel('Total Loss (W)')
    ax2.set_title('Loss vs Complexity')
    ax2.grid(True, alpha=0.3)

    # Plot 3: Loss composition ratio
    ax3 = axes[2]
    core_ratio = core_losses / (total_losses + 0.001)
    ax3.bar(range(len(data)), core_ratio, label='Core Loss %', color='#e74c3c')
    ax3.bar(range(len(data)), 1 - core_ratio, bottom=core_ratio,
            label='Copper Loss %', color='#3498db')
    ax3.set_xticks(range(len(data)))
    ax3.set_xticklabels([f"#{d['rank']}" for d in data])
    ax3.set_ylabel('Loss Fraction')
    ax3.set_title('Loss Composition')
    ax3.legend(loc='upper right')
    ax3.axhline(y=0.5, color='black', linestyle='--', alpha=0.5)

    plt.tight_layout()
    path = os.path.join(output_dir, "pareto_detailed.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()

    if verbose:
        print(f"[Pareto analysis saved to {path}]")


def _generate_volume_loss_pareto(data: list, output_dir: str, plt, np, verbose: bool):
    """Generate Volume vs Total Loss Pareto plot."""
    if len(data) < 2:
        return

    # Check if volume data is available
    volumes = np.array([d['volume_cm3'] for d in data])
    if volumes.max() == 0:
        if verbose:
            print("[Volume/loss Pareto skipped - no dimension data]")
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('Volume vs Loss Trade-off Analysis', fontsize=14, fontweight='bold')

    total_losses = np.array([d['total_loss_w'] for d in data])

    # Plot 1: Volume vs Total Loss scatter with Pareto frontier
    ax1 = axes[0]

    # Find Pareto-optimal points (minimize both volume and loss)
    pareto_mask = _find_pareto_front(volumes, total_losses)

    # Size points by efficiency (lower total loss = bigger)
    if total_losses.max() > total_losses.min():
        sizes = 200 * (1 - (total_losses - total_losses.min()) /
                       (total_losses.max() - total_losses.min() + 0.001)) + 50
    else:
        sizes = np.full_like(total_losses, 100)

    # Color by rank
    colors = plt.cm.RdYlGn_r(np.linspace(0, 1, len(data)))

    ax1.scatter(volumes, total_losses, s=sizes, c=colors,
                edgecolors='black', linewidths=1, alpha=0.8)

    # Draw Pareto frontier line
    if pareto_mask.sum() > 1:
        pareto_vol = volumes[pareto_mask]
        pareto_loss = total_losses[pareto_mask]
        sort_idx = np.argsort(pareto_vol)
        ax1.plot(pareto_vol[sort_idx], pareto_loss[sort_idx],
                'b--', alpha=0.6, linewidth=2, label='Pareto Front')
        ax1.fill_between(pareto_vol[sort_idx], pareto_loss[sort_idx],
                        total_losses.max() * 1.1, alpha=0.1, color='blue')

    # Annotate top designs and Pareto-optimal ones
    for i, d in enumerate(data):
        if i < 3 or pareto_mask[i]:
            label = f"#{d['rank']}" if i < 3 else "*"
            ax1.annotate(label, (volumes[i], total_losses[i]),
                        textcoords="offset points", xytext=(5, 5),
                        fontsize=8, fontweight='bold')

    ax1.set_xlabel('Volume (cm³)', fontsize=11)
    ax1.set_ylabel('Total Loss (W)', fontsize=11)
    ax1.set_title('Volume vs Total Loss', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    handles, labels = ax1.get_legend_handles_labels()
    if labels:
        ax1.legend(loc='upper right', fontsize=9)

    # Plot 2: Power density comparison (Loss/Volume)
    ax2 = axes[1]

    loss_density = total_losses / (volumes + 0.001)  # W/cm³
    bars_colors = ['#2ecc71' if i == 0 else '#3498db' if i < 3 else '#95a5a6'
                   for i in range(len(data))]

    # Highlight Pareto-optimal designs
    for i, is_pareto in enumerate(pareto_mask):
        if is_pareto and i >= 3:
            bars_colors[i] = '#9b59b6'  # Purple for Pareto-optimal

    core_labels = [f"#{d['rank']}: {d['core'][:12]}" for d in data]
    bars = ax2.barh(range(len(data)), loss_density, color=bars_colors, edgecolor='white')
    ax2.set_yticks(range(len(data)))
    ax2.set_yticklabels(core_labels, fontsize=9)
    ax2.set_xlabel('Loss Density (W/cm³)', fontsize=11)
    ax2.set_title('Loss Density Comparison', fontsize=12, fontweight='bold')
    ax2.invert_yaxis()
    ax2.grid(axis='x', alpha=0.3)

    # Add value labels
    max_density = max(loss_density) if len(loss_density) > 0 else 1
    for bar, density, vol in zip(bars, loss_density, volumes):
        ax2.text(bar.get_width() + max_density * 0.02, bar.get_y() + bar.get_height()/2,
                f'{density:.3f} W/cm³ ({vol:.1f}cm³)', va='center', fontsize=8)

    # Add legend for colors
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#2ecc71', label='Best'),
        Patch(facecolor='#3498db', label='Top 3'),
        Patch(facecolor='#9b59b6', label='Pareto-optimal'),
        Patch(facecolor='#95a5a6', label='Other'),
    ]
    ax2.legend(handles=legend_elements, loc='lower right', fontsize=8)

    plt.tight_layout()
    path = os.path.join(output_dir, "volume_loss_pareto.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()

    if verbose:
        print(f"[Volume/loss Pareto saved to {path}]")


def _generate_parallel_coordinates(data: list, output_dir: str, plt, np, verbose: bool):
    """Generate parallel coordinates plot for multi-dimensional comparison."""
    if len(data) < 2:
        return

    fig, ax = plt.subplots(figsize=(12, 6))

    # Define dimensions
    dims = ['Core Loss', 'Cu Loss', 'Total Loss', 'Turns', 'Gap']
    values = {
        'Core Loss': [d['core_loss_w'] for d in data],
        'Cu Loss': [d['copper_loss_w'] for d in data],
        'Total Loss': [d['total_loss_w'] for d in data],
        'Turns': [d['primary_turns'] for d in data],
        'Gap': [d['air_gap_mm'] for d in data],
    }

    # Normalize each dimension to 0-1
    norm_values = {}
    for dim in dims:
        vmin, vmax = min(values[dim]), max(values[dim])
        if vmax > vmin:
            norm_values[dim] = [(v - vmin) / (vmax - vmin) for v in values[dim]]
        else:
            norm_values[dim] = [0.5] * len(values[dim])

    # Plot each design as a polyline
    x = range(len(dims))
    colors = plt.cm.RdYlGn_r(np.linspace(0, 1, len(data)))

    for i, d in enumerate(data):
        y = [norm_values[dim][i] for dim in dims]
        linewidth = 3 if i == 0 else 1.5
        alpha = 1.0 if i < 3 else 0.5
        ax.plot(x, y, 'o-', color=colors[i], linewidth=linewidth, alpha=alpha,
                label=f"#{d['rank']}: {d['core'][:10]}", markersize=8)

    ax.set_xticks(x)
    ax.set_xticklabels(dims, fontsize=10)
    ax.set_ylabel('Normalized Value (0-1)', fontsize=10)
    ax.set_title('Parallel Coordinates: Multi-Objective Comparison',
                 fontsize=12, fontweight='bold')
    ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-0.05, 1.05)

    # Add axis labels with actual ranges
    for i, dim in enumerate(dims):
        vmin, vmax = min(values[dim]), max(values[dim])
        ax.text(i, -0.12, f'{vmin:.2f}', ha='center', fontsize=8, color='gray')
        ax.text(i, 1.08, f'{vmax:.2f}', ha='center', fontsize=8, color='gray')

    plt.tight_layout()
    path = os.path.join(output_dir, "parallel_coordinates.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()

    if verbose:
        print(f"[Parallel coordinates saved to {path}]")


def _generate_heatmap(data: list, output_dir: str, plt, np, verbose: bool):
    """Generate heatmap of design characteristics."""
    if len(data) < 2:
        return

    fig, ax = plt.subplots(figsize=(10, 6))

    # Build matrix
    metrics = ['Core Loss', 'Copper Loss', 'Total Loss', 'Turns', 'Gap']
    matrix = []
    for d in data:
        row = [
            d['core_loss_w'],
            d['copper_loss_w'],
            d['total_loss_w'],
            d['primary_turns'],
            d['air_gap_mm'],
        ]
        matrix.append(row)

    matrix = np.array(matrix)

    # Normalize columns
    matrix_norm = np.zeros_like(matrix)
    for j in range(matrix.shape[1]):
        col = matrix[:, j]
        vmin, vmax = col.min(), col.max()
        if vmax > vmin:
            matrix_norm[:, j] = (col - vmin) / (vmax - vmin)
        else:
            matrix_norm[:, j] = 0.5

    # Plot heatmap
    im = ax.imshow(matrix_norm, cmap='RdYlGn_r', aspect='auto')

    # Labels
    ax.set_xticks(range(len(metrics)))
    ax.set_xticklabels(metrics, fontsize=10)
    ax.set_yticks(range(len(data)))
    ax.set_yticklabels([f"#{d['rank']}: {d['core'][:10]}" for d in data], fontsize=9)

    # Add value annotations
    for i in range(len(data)):
        for j in range(len(metrics)):
            val = matrix[i, j]
            text = f'{val:.2f}' if val < 100 else f'{val:.0f}'
            color = 'white' if matrix_norm[i, j] > 0.5 else 'black'
            ax.text(j, i, text, ha='center', va='center', fontsize=8, color=color)

    ax.set_title('Design Characteristics Heatmap', fontsize=12, fontweight='bold')
    plt.colorbar(im, label='Normalized (0=Best, 1=Worst)')

    plt.tight_layout()
    path = os.path.join(output_dir, "heatmap.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()

    if verbose:
        print(f"[Heatmap saved to {path}]")


def _save_json_summary(data: list, output_dir: str, specs: Optional[dict], verbose: bool):
    """Save comprehensive JSON summary."""
    summary = {
        "report_version": "2.0",
        "num_designs": len(data),
        "best_design": data[0] if data else None,
        "specifications": specs,
        "all_designs": data,
        "statistics": {
            "min_total_loss": min(d['total_loss_w'] for d in data) if data else 0,
            "max_total_loss": max(d['total_loss_w'] for d in data) if data else 0,
            "avg_total_loss": sum(d['total_loss_w'] for d in data) / len(data) if data else 0,
            "loss_range": (max(d['total_loss_w'] for d in data) -
                          min(d['total_loss_w'] for d in data)) if data else 0,
        },
        "files_generated": [
            "design_report.png",
            "pareto_detailed.png",
            "volume_loss_pareto.png",
            "parallel_coordinates.png",
            "heatmap.png",
            "report_summary.json",
        ]
    }

    json_path = os.path.join(output_dir, "report_summary.json")
    with open(json_path, 'w') as f:
        json.dump(summary, f, indent=2)

    if verbose:
        print(f"[JSON summary saved to {json_path}]")

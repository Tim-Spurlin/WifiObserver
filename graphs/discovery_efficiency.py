#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Discovery Efficiency Graph Generator

This script generates a bar chart comparing the efficiency of network discovery
with and without WifiObserver. It visualizes the time savings and detection
improvements provided by the tool.
"""

import argparse
import json
import os
import sys
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# Add parent directory to path to enable imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def create_discovery_efficiency_chart(output_file=None):
    """Create a bar chart showing the efficiency comparison

    Args:
        output_file (str, optional): Output file path. If None, display the chart.
    """
    # Set up the data
    categories = ["Time to Discover\nAll Networks", "Hidden Network\nDetection", "Network Type\nClassification"]
    
    # Time measured in minutes for network discovery tasks
    manual_times = [15, 5, 20]  # Manual/Traditional approach (estimated)
    wifiobserver_times = [3, 3, 2]  # WifiObserver approach (estimated)
    
    # Set up the bar positions
    x = np.arange(len(categories))
    width = 0.35
    
    # Set up the chart
    fig, ax = plt.figure(figsize=(12, 8)), plt.axes()
    
    # Create the bars
    manual_bars = ax.bar(x - width/2, manual_times, width, label='Without WifiObserver', 
                        color='gray', edgecolor='black', linewidth=0.5)
    wifiobserver_bars = ax.bar(x + width/2, wifiobserver_times, width, label='With WifiObserver', 
                               color='royalblue', edgecolor='black', linewidth=0.5)
    
    # Add value labels above the bars
    def add_labels(bars):
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height} min',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom',
                        fontweight='bold')
    
    add_labels(manual_bars)
    add_labels(wifiobserver_bars)
    
    # Add efficiency improvement percentages
    for i, (m, w) in enumerate(zip(manual_times, wifiobserver_times)):
        improvement = ((m - w) / m) * 100
        ax.annotate(f'{improvement:.0f}% faster',
                   xy=(x[i], w + 0.5),
                   xytext=(0, 10),  # 10 points vertical offset
                   textcoords="offset points",
                   ha='center', va='bottom',
                   color='green',
                   fontweight='bold',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8, edgecolor='green'))
    
    # Customize the chart
    ax.set_title('Network Discovery Efficiency Comparison', fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel('Time (minutes)', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=11)
    ax.legend(fontsize=12)
    
    # Add grid lines
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Set y-axis limit with some padding
    ax.set_ylim(0, max(manual_times) * 1.2)
    
    # Add explanatory annotations
    explanations = [
        "Discovers all networks\nin range including hidden\nnetworks automatically",
        "Identifies hidden networks\nwithout manual probing\nor specialized tools",
        "Automatically classifies\nnetworks based on\ncharacteristics"
    ]
    
    for i, explanation in enumerate(explanations):
        ax.annotate(explanation,
                   xy=(x[i], 0.5),
                   xytext=(0, -30),  # 30 points vertical offset
                   textcoords="offset points",
                   ha='center', va='top',
                   fontsize=9,
                   fontStyle='italic',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.8))
    
    # Add additional benefits section
    benefits_text = "\n".join([
        "Additional Benefits of WifiObserver:",
        "• Passive scanning only - no packets sent to networks",
        "• Automatic reporting and visualization",
        "• Legal compliance built-in by design",
        "• Consistent, repeatable methodology",
        "• Easy-to-interpret network classification"
    ])
    
    plt.figtext(0.7, 0.2, benefits_text, fontsize=10, 
               bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.3))
    
    # Add timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    plt.figtext(0.5, 0.01, f"Generated: {timestamp}", ha="center", fontsize=9, style='italic')
    
    # Disclaimer
    disclaimer = "Note: Times are estimates based on typical usage patterns. Actual efficiency may vary based on hardware and environment."
    plt.figtext(0.5, 0.04, disclaimer, ha="center", fontsize=8, style='italic')
    
    # Tight layout
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.1)
    
    # Save or display
    if output_file:
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        plt.savefig(output_file, bbox_inches='tight', dpi=300)
        print(f"Chart saved to {output_file}")
    else:
        plt.show()


def main():
    """Main function for the discovery efficiency graph generator"""
    parser = argparse.ArgumentParser(description="WifiObserver - Discovery Efficiency Chart Generator")
    parser.add_argument("--output", "-o", default=None, help="Output image file (PNG/PDF/SVG)")
    args = parser.parse_args()
    
    # Default output filename if not specified
    if not args.output:
        args.output = "graphs/discovery_efficiency.png"
    
    # Ensure output directory exists
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create chart
    create_discovery_efficiency_chart(args.output)


if __name__ == "__main__":
    main()
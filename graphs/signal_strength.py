#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Signal Strength Graph Generator

This script generates a horizontal bar chart showing the signal strength
of detected networks, color-coded by network type for easy visualization.
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


def load_data(input_file):
    """Load network data from a JSON file

    Args:
        input_file (str): Path to the input JSON file

    Returns:
        list: List of networks
    """
    try:
        with open(input_file, "r") as f:
            data = json.load(f)
        
        # Handle different file structures
        if "networks" in data:
            return data["networks"]
        elif isinstance(data, list):
            return data
        elif isinstance(data, dict) and all(isinstance(v, dict) for v in data.values()):
            return list(data.values())
        else:
            print("Unrecognized data format in input file")
            sys.exit(1)
    
    except Exception as e:
        print(f"Error loading input file: {e}")
        sys.exit(1)


def prepare_signal_data(networks, max_networks=20):
    """Prepare data for the signal strength chart

    Args:
        networks (list): List of networks
        max_networks (int, optional): Maximum number of networks to display. Defaults to 20.

    Returns:
        tuple: (ssids, signal_strengths, types)
    """
    # Filter out networks without signal strength data
    valid_networks = [n for n in networks if "signal" in n and isinstance(n["signal"], (int, float))]
    
    # Sort by signal strength (strongest first)
    sorted_networks = sorted(valid_networks, key=lambda n: n.get("signal", -100), reverse=True)
    
    # Limit to max_networks
    if len(sorted_networks) > max_networks:
        sorted_networks = sorted_networks[:max_networks]
    
    # Prepare data
    ssids = []
    signal_strengths = []
    types = []
    
    for network in sorted_networks:
        # Use SSID if available, otherwise BSSID
        ssid = network.get("ssid", network.get("bssid", "Unknown"))
        if ssid == "[Hidden Network]" and "bssid" in network:
            ssid = f"Hidden ({network['bssid']})"
        
        # Truncate long SSIDs
        if len(ssid) > 20:
            ssid = ssid[:17] + "..."
        
        ssids.append(ssid)
        signal_strengths.append(network.get("signal", -100))
        types.append(network.get("type", "STANDARD"))
    
    return ssids, signal_strengths, types


def create_signal_strength_chart(networks, output_file=None, max_networks=20):
    """Create a bar chart of signal strengths

    Args:
        networks (list): List of networks
        output_file (str, optional): Output file path. If None, display the chart.
        max_networks (int, optional): Maximum number of networks to display. Defaults to 20.
    """
    # Prepare data
    ssids, signal_strengths, types = prepare_signal_data(networks, max_networks)
    
    if not ssids:
        print("No signal data available.")
        return
    
    # Set up colors based on network type
    color_map = {
        "POSSIBLE_OFFICIAL": "firebrick",
        "ENTERPRISE": "royalblue",
        "MOBILE_HOTSPOT": "forestgreen",
        "PUBLIC": "gold",
        "IOT": "purple",
        "ISP_PROVIDED": "turquoise",
        "STANDARD": "lightgray"
    }
    
    colors = [color_map.get(t, "lightgray") for t in types]
    
    # Set up chart
    plt.figure(figsize=(10, max(8, len(ssids) * 0.4)))
    
    # Create horizontal bar chart
    bars = plt.barh(ssids, signal_strengths, color=colors, alpha=0.8, edgecolor='black', linewidth=0.5)
    
    # Add a vertical line at -70 dBm (generally considered threshold for good signal)
    plt.axvline(-70, color='gray', linestyle='--', alpha=0.7)
    plt.text(-70, len(ssids) + 0.5, "Good Signal Threshold", va='center', ha='center', 
             rotation=90, color='gray', fontsize=8)
    
    # Set chart title and labels
    plt.title('Wi-Fi Network Signal Strengths (dBm)', fontsize=16, fontweight='bold', pad=20)
    plt.suptitle('Stronger signals are closer to 0', fontsize=10, y=0.92)
    plt.xlabel('Signal Strength (dBm)', fontsize=12)
    plt.ylabel('Network SSID', fontsize=12)
    
    # Set x-axis limits
    min_signal = min(signal_strengths) - 5
    max_signal = max(0, max(signal_strengths) + 5)
    plt.xlim(min_signal, max_signal)
    
    # Add grid lines on the x-axis only
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Annotate bars with values
    for bar, value in zip(bars, signal_strengths):
        plt.text(
            value - (0.03 * abs(min_signal)),  # Position text based on min_signal
            bar.get_y() + bar.get_height()/2,
            f"{value} dBm",
            va='center',
            color='white' if value > -60 else 'black',
            fontweight='bold',
            fontsize=9
        )
    
    # Add legend
    unique_types = list(set(types))
    legend_handles = [plt.Rectangle((0,0), 1, 1, color=color_map.get(t, "lightgray")) for t in unique_types]
    plt.legend(legend_handles, unique_types, loc='lower right', fontsize=10)
    
    # Add timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    plt.figtext(0.5, 0.01, f"Generated: {timestamp}", ha="center", fontsize=9, style='italic')
    
    # Add signal strength interpretation guide
    guide_text = "\n".join([
        "Signal Strength Interpretation:",
        "-30 to -50 dBm: Excellent signal (Very close to AP)",
        "-50 to -60 dBm: Good signal (Reliable connection)",
        "-60 to -70 dBm: Fair signal (Acceptable performance)",
        "-70 to -80 dBm: Weak signal (May experience issues)",
        "-80 to -90 dBm: Poor signal (Unreliable connection)",
        "Below -90 dBm: Very poor (Barely detectable)"
    ])
    
    plt.figtext(0.02, 0.02, guide_text, fontsize=9, 
               bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.8))
    
    # Tight layout
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.15)
    
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
    """Main function for the signal strength graph generator"""
    parser = argparse.ArgumentParser(description="WifiObserver - Signal Strength Chart Generator")
    parser.add_argument("--input", "-i", required=True, help="Input JSON file with network data")
    parser.add_argument("--output", "-o", default=None, help="Output image file (PNG/PDF/SVG)")
    parser.add_argument("--max", "-m", type=int, default=20, help="Maximum number of networks to display")
    args = parser.parse_args()
    
    # Default output filename if not specified
    if not args.output:
        input_base = os.path.splitext(os.path.basename(args.input))[0]
        args.output = f"graphs/signal_strength_{input_base}.png"
    
    # Ensure output directory exists
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Load data
    networks = load_data(args.input)
    
    # Create chart
    create_signal_strength_chart(networks, args.output, args.max)


if __name__ == "__main__":
    main()
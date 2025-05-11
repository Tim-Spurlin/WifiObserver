#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Network Types Distribution Graph Generator

This script generates a pie chart showing the distribution of network types
detected by WifiObserver. It visualizes the proportion of different network
classifications in a given scanning session.
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
        dict: Loaded data
    """
    try:
        with open(input_file, "r") as f:
            data = json.load(f)
        
        # Check if we have a proper data structure
        if "networks" in data:
            # File from wifi_scanner direct output
            networks = data["networks"]
        elif isinstance(data, dict) and "distribution" in data:
            # File from network_classifier output with pre-calculated distribution
            return data
        else:
            # Try to interpret as a direct network dictionary
            networks = data if isinstance(data, list) else list(data.values())
        
        return {"networks": networks}
    
    except Exception as e:
        print(f"Error loading input file: {e}")
        sys.exit(1)


def calculate_distribution(data):
    """Calculate the distribution of network types

    Args:
        data (dict): Network data

    Returns:
        dict: Distribution of network types
    """
    # Check if distribution is already calculated
    if "distribution" in data:
        return data["distribution"]
    
    # Calculate distribution from networks
    distribution = {
        "POSSIBLE_OFFICIAL": 0,
        "ENTERPRISE": 0,
        "MOBILE_HOTSPOT": 0,
        "PUBLIC": 0,
        "IOT": 0,
        "ISP_PROVIDED": 0,
        "STANDARD": 0
    }
    
    for network in data["networks"]:
        network_type = network.get("type", "STANDARD")
        if network_type in distribution:
            distribution[network_type] += 1
        else:
            distribution["STANDARD"] += 1
    
    return distribution


def create_network_types_chart(distribution, output_file=None):
    """Create a pie chart of network types distribution

    Args:
        distribution (dict): Network type distribution
        output_file (str, optional): Output file path. If None, display the chart.
    """
    # Filter out zero values
    filtered_distribution = {k: v for k, v in distribution.items() if v > 0}
    
    if not filtered_distribution:
        print("No data to display.")
        return
    
    # Set up colors for different network types
    colors = {
        "POSSIBLE_OFFICIAL": "firebrick",
        "ENTERPRISE": "royalblue",
        "MOBILE_HOTSPOT": "forestgreen",
        "PUBLIC": "gold",
        "IOT": "purple",
        "ISP_PROVIDED": "turquoise",
        "STANDARD": "lightgray"
    }
    
    # Set up chart
    plt.figure(figsize=(12, 7))
    
    # Extract data
    labels = filtered_distribution.keys()
    sizes = filtered_distribution.values()
    chart_colors = [colors.get(label, "lightgray") for label in labels]
    
    # Calculate percentages for labels
    total = sum(sizes)
    pct_sizes = [(size / total) * 100 for size in sizes]
    
    # Create pie chart
    patches, texts, autotexts = plt.pie(
        sizes, 
        labels=labels, 
        colors=chart_colors,
        autopct='%1.1f%%',
        startangle=90,
        shadow=True,
        wedgeprops={'edgecolor': 'black', 'linewidth': 0.5},
        textprops={'fontsize': 12, 'fontweight': 'bold'}
    )
    
    # Equal aspect ratio ensures the pie chart is circular
    plt.axis('equal')
    
    # Add title and subtitle
    plt.title('Wi-Fi Network Type Distribution', fontsize=16, fontweight='bold', pad=20)
    plt.suptitle('Based on WifiObserver Classification', fontsize=10, y=0.92)
    
    # Add timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    plt.figtext(0.5, 0.01, f"Generated: {timestamp}", ha="center", fontsize=9, style='italic')
    
    # Add legend
    legend_labels = [f"{label} ({int(pct)}%)" for label, pct in zip(labels, pct_sizes)]
    plt.legend(patches, legend_labels, loc="center left", bbox_to_anchor=(1, 0.5))
    
    # Add descriptive information
    info_text = "\n".join([
        "Network Type Classifications:",
        "POSSIBLE_OFFICIAL: Networks with characteristics of government/official entities",
        "ENTERPRISE: Corporate or organizational networks",
        "MOBILE_HOTSPOT: Personal mobile hotspots from phones or mobile devices",
        "PUBLIC: Open access points or public service networks",
        "IOT: Networks associated with Internet of Things devices",
        "ISP_PROVIDED: Default configurations from Internet Service Providers",
        "STANDARD: Networks that don't fit other classifications"
    ])
    
    plt.figtext(0.5, -0.1, info_text, ha="center", fontsize=9, 
               bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.8))
    
    # Adjust layout
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
    """Main function for the network types graph generator"""
    parser = argparse.ArgumentParser(description="WifiObserver - Network Types Distribution Chart Generator")
    parser.add_argument("--input", "-i", required=True, help="Input JSON file with network data")
    parser.add_argument("--output", "-o", default=None, help="Output image file (PNG/PDF/SVG)")
    args = parser.parse_args()
    
    # Default output filename if not specified
    if not args.output:
        input_base = os.path.splitext(os.path.basename(args.input))[0]
        args.output = f"graphs/network_types_{input_base}.png"
    
    # Ensure output directory exists
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Load data
    data = load_data(args.input)
    
    # Calculate distribution
    distribution = calculate_distribution(data)
    
    # Create chart
    create_network_types_chart(distribution, args.output)


if __name__ == "__main__":
    main()
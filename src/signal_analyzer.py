#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Signal Analyzer Module

This module provides functionality for analyzing Wi-Fi signal strength
over time, helping to identify signal patterns and stability.
"""

import argparse
import json
import os
import sys
import time
import signal
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

try:
    import scapy.all as scapy
except ImportError:
    print("Error: Scapy library not found. Please install it using 'pip install scapy'")
    sys.exit(1)

# Add parent directory to path to enable imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.interface_manager import set_monitor_mode, check_interface
from src.utils.logging_utils import setup_logger, log_header

# Initialize logger
logger = setup_logger("signal_analyzer")

# Global variables
networks = {}
signal_history = {}
interrupted = False


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    global interrupted
    print("\n\nAnalysis interrupted. Shutting down gracefully...")
    interrupted = True


def initialize_analysis(interface):
    """Initialize the signal analysis process

    Args:
        interface (str): Wireless interface to use

    Returns:
        str: Interface name
    """
    # Ensure interface exists
    if not check_interface(interface):
        logger.error(f"Interface {interface} not found. Please check available interfaces.")
        sys.exit(1)
    
    # Set monitor mode
    set_monitor_mode(interface)
    
    # Setup signal handler for graceful exit
    signal.signal(signal.SIGINT, signal_handler)
    
    log_header(f"Starting Wi-Fi signal analysis on interface {interface}")
    logger.info(f"Analysis initiated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("Press Ctrl+C to stop analysis and view results")
    
    return interface


def process_beacon(packet):
    """Process beacon frames to track signal strength

    Args:
        packet: Scapy packet
    """
    # Extract the network MAC
    bssid = packet[scapy.Dot11].addr2
    
    # Extract the network name (SSID)
    try:
        ssid = packet[scapy.Dot11Elt].info.decode("utf-8")
    except:
        ssid = "Unknown"
    
    # Handle hidden networks (empty SSID)
    if ssid == "" or not ssid:
        ssid = "[Hidden Network]"
    
    # Get signal strength
    signal = get_signal_strength(packet)
    
    # Get current timestamp
    timestamp = time.time()
    
    # Add/update network in the dictionary
    if bssid not in networks:
        networks[bssid] = {
            "ssid": ssid,
            "bssid": bssid,
            "first_seen": timestamp,
            "signals": []
        }
        # Initialize signal history
        signal_history[bssid] = []
    
    # Update signal information
    networks[bssid]["last_seen"] = timestamp
    networks[bssid]["signals"].append((timestamp, signal))
    
    # Keep a record of signal strength for this network
    signal_history[bssid].append((timestamp, signal))


def process_packet(packet):
    """Process captured packets for signal analysis

    Args:
        packet: Scapy packet
    """
    # Check if packet has a Beacon layer
    if packet.haslayer(scapy.Dot11Beacon):
        process_beacon(packet)


def get_signal_strength(packet):
    """Extract signal strength from packet

    Args:
        packet: Scapy packet

    Returns:
        int: Signal strength in dBm
    """
    # This is a vendor-specific extension for Linux, might not work on all setups
    if hasattr(packet, "dBm_AntSignal"):
        return packet.dBm_AntSignal
    return -100  # Default value if not available


def analyze_signal_stability(signals, network_info):
    """Analyze the stability of a network's signal

    Args:
        signals (list): List of (timestamp, signal_strength) tuples
        network_info (dict): Network information

    Returns:
        dict: Signal stability metrics
    """
    if not signals or len(signals) < 3:
        return {"stability": "Unknown", "std_dev": 0, "range": 0, "trend": "Unknown"}
    
    # Extract signal values (ignore timestamps for statistical analysis)
    signal_values = [s[1] for s in signals]
    
    # Calculate basic statistics
    mean = np.mean(signal_values)
    median = np.median(signal_values)
    std_dev = np.std(signal_values)
    min_signal = min(signal_values)
    max_signal = max(signal_values)
    signal_range = max_signal - min_signal
    
    # Determine stability category
    if std_dev < 2:
        stability = "Very Stable"
    elif std_dev < 5:
        stability = "Stable"
    elif std_dev < 10:
        stability = "Moderately Stable"
    else:
        stability = "Unstable"
    
    # Determine signal trend
    if len(signal_values) >= 10:
        # Use the first and second half of the data to determine trend
        first_half = signal_values[:len(signal_values)//2]
        second_half = signal_values[len(signal_values)//2:]
        first_mean = np.mean(first_half)
        second_mean = np.mean(second_half)
        
        if second_mean - first_mean > 3:
            trend = "Improving"
        elif first_mean - second_mean > 3:
            trend = "Deteriorating"
        else:
            trend = "Stable"
    else:
        trend = "Insufficient Data"
    
    return {
        "stability": stability,
        "std_dev": round(std_dev, 2),
        "mean": round(mean, 2),
        "median": round(median, 2),
        "min": min_signal,
        "max": max_signal,
        "range": signal_range,
        "trend": trend
    }


def generate_signal_report(output_file=None):
    """Generate a report of signal analysis

    Args:
        output_file (str, optional): Output file name. Defaults to None.

    Returns:
        str: Path to saved report (if output_file provided)
    """
    # Prepare output directory
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    
    # Default output filename if not provided
    if not output_file:
        timestamp = int(time.time())
        output_file = f"signal_analysis_{timestamp}.json"
    
    output_path = os.path.join(output_dir, output_file)
    
    # Process signal data for each network
    results = []
    for bssid, network in networks.items():
        if bssid in signal_history and len(signal_history[bssid]) > 0:
            signals = signal_history[bssid]
            stability_metrics = analyze_signal_stability(signals, network)
            
            # Add to results
            results.append({
                "ssid": network["ssid"],
                "bssid": bssid,
                "first_seen": datetime.fromtimestamp(network["first_seen"]).strftime("%Y-%m-%d %H:%M:%S"),
                "last_seen": datetime.fromtimestamp(network["last_seen"]).strftime("%Y-%m-%d %H:%M:%S"),
                "signal_metrics": stability_metrics,
                "raw_signal_data": [(datetime.fromtimestamp(ts).strftime("%H:%M:%S"), sig) for ts, sig in signals]
            })
    
    # Sort by signal strength (strongest first)
    results.sort(key=lambda x: x["signal_metrics"].get("mean", -100), reverse=True)
    
    # Create report
    report = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "duration": f"{(time.time() - min(n['first_seen'] for n in networks.values()))/60:.1f} minutes",
        "total_networks": len(networks),
        "networks": results
    }
    
    # Save to file
    with open(output_path, "w") as f:
        json.dump(report, f, indent=4)
    
    print(f"\nSignal analysis report saved to {output_path}")
    return output_path


def plot_signal_trends(network_data, output_dir="graphs"):
    """Generate signal trend plots for significant networks

    Args:
        network_data (list): List of network data dictionaries
        output_dir (str, optional): Output directory. Defaults to "graphs".
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Sort networks by mean signal strength (strongest first)
    sorted_networks = sorted(network_data, key=lambda x: x["signal_metrics"].get("mean", -100), reverse=True)
    
    # Limit to top 5 strongest networks
    top_networks = sorted_networks[:5]
    
    # Plot individual signal trends
    for network in top_networks:
        ssid = network["ssid"]
        bssid = network["bssid"]
        raw_data = network["raw_signal_data"]
        
        if len(raw_data) < 3:
            continue
        
        # Extract data
        timestamps = [d[0] for d in raw_data]
        signal_values = [d[1] for d in raw_data]
        
        # Create plot
        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, signal_values, marker='o', linestyle='-', markersize=4)
        
        # Set labels and title
        plt.title(f"Signal Strength Trend: {ssid} ({bssid})", fontsize=14, fontweight='bold')
        plt.xlabel("Time", fontsize=12)
        plt.ylabel("Signal Strength (dBm)", fontsize=12)
        
        # Set y-axis limits and grid
        plt.ylim(min(signal_values) - 5, max(signal_values) + 5)
        plt.grid(True, alpha=0.3)
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45, ha='right')
        
        # Show only some of the x-axis labels to avoid crowding
        if len(timestamps) > 10:
            step = len(timestamps) // 10
            plt.xticks(range(0, len(timestamps), step), [timestamps[i] for i in range(0, len(timestamps), step)])
        
        # Add average line
        avg = network["signal_metrics"]["mean"]
        plt.axhline(y=avg, color='r', linestyle='--', alpha=0.7, label=f"Average: {avg} dBm")
        
        # Add signal quality zones
        plt.axhspan(-50, 0, alpha=0.2, color='green', label='Excellent')
        plt.axhspan(-70, -50, alpha=0.2, color='yellow', label='Good')
        plt.axhspan(-90, -70, alpha=0.2, color='orange', label='Fair')
        plt.axhspan(-100, -90, alpha=0.2, color='red', label='Poor')
        
        # Add legend
        plt.legend(loc='lower right')
        
        # Add stability information
        stability_info = f"Stability: {network['signal_metrics']['stability']}\n"
        stability_info += f"Standard Deviation: {network['signal_metrics']['std_dev']} dBm\n"
        stability_info += f"Range: {network['signal_metrics']['range']} dBm\n"
        stability_info += f"Trend: {network['signal_metrics']['trend']}"
        
        plt.figtext(0.15, 0.15, stability_info, fontsize=10,
                   bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.8))
        
        # Adjust layout and save
        plt.tight_layout()
        filename = f"{output_dir}/signal_trend_{bssid.replace(':', '')}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Signal trend chart for {ssid} saved to {filename}")
    
    # Create comparative chart for all top networks
    plt.figure(figsize=(12, 8))
    
    for network in top_networks:
        ssid = network["ssid"]
        raw_data = network["raw_signal_data"]
        
        if len(raw_data) < 3:
            continue
        
        # Extract data
        timestamps = [d[0] for d in raw_data]
        signal_values = [d[1] for d in raw_data]
        
        # Plot this network's signal trend
        plt.plot(range(len(timestamps)), signal_values, marker='.', label=ssid)
    
    # Set labels and title
    plt.title("Comparative Signal Trends for Top Networks", fontsize=14, fontweight='bold')
    plt.xlabel("Time", fontsize=12)
    plt.ylabel("Signal Strength (dBm)", fontsize=12)
    
    # Set y-axis limits and grid
    plt.grid(True, alpha=0.3)
    
    # Show only some of the x-axis labels to avoid crowding
    if top_networks and len(top_networks[0]["raw_data"]) > 10:
        timestamps = [d[0] for d in top_networks[0]["raw_data"]]
        step = len(timestamps) // 10
        plt.xticks(range(0, len(timestamps), step), [timestamps[i] for i in range(0, len(timestamps), step)])
    
    # Add signal quality zones
    plt.axhspan(-50, 0, alpha=0.2, color='green', label='Excellent')
    plt.axhspan(-70, -50, alpha=0.2, color='yellow', label='Good')
    plt.axhspan(-90, -70, alpha=0.2, color='orange', label='Fair')
    plt.axhspan(-100, -90, alpha=0.2, color='red', label='Poor')
    
    # Add legend
    plt.legend(loc='lower right')
    
    # Adjust layout and save
    plt.tight_layout()
    filename = f"{output_dir}/comparative_signal_trends.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Comparative signal trends chart saved to {filename}")


def main():
    """Main function for the signal analyzer module"""
    parser = argparse.ArgumentParser(description="WifiObserver - Signal Analyzer")
    parser.add_argument("--interface", "-i", required=True, help="Wireless interface to use")
    parser.add_argument("--duration", "-d", type=int, default=60, help="Analysis duration in seconds")
    parser.add_argument("--output", "-o", default=None, help="Output file name")
    parser.add_argument("--interval", "-n", type=float, default=1.0, help="Sampling interval in seconds")
    parser.add_argument("--plot", "-p", action="store_true", help="Generate signal trend plots")
    args = parser.parse_args()
    
    # Initialize analysis
    interface = initialize_analysis(args.interface)
    
    # Set up variables for interval sampling
    last_sample_time = time.time()
    end_time = last_sample_time + args.duration
    current_time = last_sample_time
    
    try:
        print(f"Starting signal analysis for {args.duration} seconds with {args.interval}s intervals...")
        print("Press Ctrl+C to stop analysis early")
        
        # Main analysis loop
        while current_time < end_time and not interrupted:
            # Perform packet capture for a brief period
            scapy.sniff(
                iface=interface,
                prn=process_packet,
                store=False,
                timeout=args.interval
            )
            
            # Update time for next iteration
            current_time = time.time()
            
            # Calculate progress
            elapsed = current_time - last_sample_time
            progress = min(100, (elapsed / args.duration) * 100)
            
            # Print progress
            print(f"\rProgress: {progress:.1f}% - {len(networks)} networks analyzed", end="")
        
        print("\n\nAnalysis completed")
        
        # Generate report
        report_path = generate_signal_report(args.output)
        
        # Generate plots if requested
        if args.plot:
            # Load the report data
            with open(report_path, "r") as f:
                report_data = json.load(f)
            
            # Create signal trend plots
            plot_signal_trends(report_data["networks"])
        
        print("\nSignal Analysis Summary:")
        print(f"- {len(networks)} networks analyzed")
        print(f"- Analysis duration: {args.duration} seconds")
        print(f"- Report saved to: {report_path}")
        
        if args.plot:
            print("- Signal trend plots saved to graphs/ directory")
    
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user")
        generate_signal_report(args.output)
    
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    # Check if running as root
    if os.geteuid() != 0:
        print("Error: This script must be run as root (use sudo)")
        sys.exit(1)
    
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WifiObserver Scanner Module

This module provides the core functionality for passive Wi-Fi network detection,
including the ability to detect hidden networks. It operates within legal bounds
by only performing passive scanning without attempting to connect to networks.
"""

import argparse
import json
import os
import signal
import sys
import time
from datetime import datetime
from pathlib import Path

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
logger = setup_logger("wifi_scanner")

# Global variables
networks = {}
hidden_networks = set()
start_time = None
output_file = None


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\nScan interrupted. Shutting down gracefully...")
    if output_file:
        save_results(output_file)
    print(f"Discovered {len(networks)} networks ({len(hidden_networks)} hidden)")
    print("Exiting...")
    sys.exit(0)


def initialize_scan(interface):
    """Initialize the scanning process"""
    global start_time
    
    # Ensure interface exists
    if not check_interface(interface):
        logger.error(f"Interface {interface} not found. Please check available interfaces.")
        sys.exit(1)
    
    # Set monitor mode
    set_monitor_mode(interface)
    
    # Set start time
    start_time = datetime.now()
    
    # Setup signal handler for graceful exit
    signal.signal(signal.SIGINT, signal_handler)
    
    log_header(f"Starting Wi-Fi scan on interface {interface}")
    logger.info(f"Scan initiated at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("Press Ctrl+C to stop scanning and save results")
    
    return interface


def process_packet(packet):
    """Process captured packets to identify networks"""
    # Check if packet has a Beacon layer (standard networks)
    if packet.haslayer(scapy.Dot11Beacon):
        process_beacon(packet)
    # Check for Probe Responses (can reveal hidden networks)
    elif packet.haslayer(scapy.Dot11ProbeResp):
        process_probe_response(packet)
    

def process_beacon(packet):
    """Process beacon frames to identify networks"""
    # Extract the network MAC
    bssid = packet[scapy.Dot11].addr2
    if bssid in networks:
        # Update signal strength
        networks[bssid]["signal"] = get_signal_strength(packet)
        networks[bssid]["last_seen"] = time.time()
        return
        
    # Extract the network name (SSID)
    try:
        ssid = packet[scapy.Dot11Elt].info.decode("utf-8")
    except:
        ssid = "Unknown"
    
    # Handle hidden networks (empty SSID)
    if ssid == "" or not ssid:
        ssid = "[Hidden Network]"
        hidden_networks.add(bssid)
    
    # Get the channel
    channel = get_channel(packet)
    
    # Get encryption type
    encryption = get_encryption(packet)
    
    # Get signal strength
    signal = get_signal_strength(packet)
    
    # Get manufacturer (if available)
    manufacturer = get_manufacturer(bssid)
    
    # Store the network
    networks[bssid] = {
        "ssid": ssid,
        "bssid": bssid,
        "channel": channel,
        "encryption": encryption,
        "signal": signal,
        "manufacturer": manufacturer,
        "first_seen": time.time(),
        "last_seen": time.time(),
        "hidden": ssid == "[Hidden Network]",
        "type": classify_network(ssid, bssid, encryption, manufacturer)
    }
    
    # Log the discovery
    print_network(networks[bssid])


def process_probe_response(packet):
    """Process probe response frames to potentially uncover hidden networks"""
    bssid = packet[scapy.Dot11].addr2
    
    try:
        ssid = packet[scapy.Dot11Elt].info.decode("utf-8")
    except:
        return  # Invalid SSID
    
    # If this is a known hidden network and we now have its SSID
    if bssid in hidden_networks and ssid and ssid != "[Hidden Network]":
        if bssid in networks:
            # Update the network with actual SSID
            networks[bssid]["ssid"] = ssid
            networks[bssid]["hidden"] = False
            networks[bssid]["last_seen"] = time.time()
            hidden_networks.remove(bssid)
            
            # Log the discovery of a hidden network
            logger.info(f"Uncovered hidden network: {ssid} ({bssid})")
            print(f"✓ Uncovered hidden network: {ssid} ({bssid})")


def get_channel(packet):
    """Extract channel information from packet"""
    channel = 0
    
    # DS Parameter Set IE
    curr = packet[scapy.Dot11Elt]
    while curr and curr.ID != 3:
        curr = curr.payload
    
    if curr and curr.ID == 3 and curr.len == 1:
        channel = ord(curr.info)
    
    return channel


def get_encryption(packet):
    """Determine encryption type from packet"""
    encryption = "Open"
    
    # Check for encryption in the capability field
    capability = packet.sprintf("{Dot11Beacon:%Dot11Beacon.cap%}")
    
    if "privacy" in capability:
        # Check for RSN (WPA2) information
        rsn = get_rsn_info(packet)
        if rsn:
            if "CCMP" in rsn:
                encryption = "WPA2/WPA3"
            else:
                encryption = "WPA2"
        # Check for WPA information
        elif get_wpa_info(packet):
            encryption = "WPA"
        # If privacy bit is set but no WPA/WPA2, it's WEP
        else:
            encryption = "WEP"
    
    return encryption


def get_rsn_info(packet):
    """Extract RSN (WPA2) information"""
    curr = packet[scapy.Dot11Elt]
    while curr and curr.ID != 48:
        curr = curr.payload
    
    if curr and curr.ID == 48:
        return curr.info.hex()
    
    return None


def get_wpa_info(packet):
    """Extract WPA information"""
    curr = packet[scapy.Dot11Elt]
    while curr:
        if curr.ID == 221 and curr.info.startswith(b"\x00\x50\xf2\x01"):
            return True
        curr = curr.payload
    
    return False


def get_signal_strength(packet):
    """Extract signal strength from packet"""
    # This is a vendor-specific extension for Linux, might not work on all setups
    if hasattr(packet, "dBm_AntSignal"):
        return packet.dBm_AntSignal
    return -100  # Default value if not available


def get_manufacturer(mac):
    """Attempt to identify manufacturer from MAC address"""
    try:
        from manuf import manuf
        p = manuf.MacParser()
        manufacturer = p.get_manuf(mac)
        return manufacturer if manufacturer else "Unknown"
    except:
        return "Unknown"


def classify_network(ssid, bssid, encryption, manufacturer):
    """Attempt to classify the network type based on characteristics"""
    # This is a simple heuristic classification and is not definitive
    
    # Check for common government/official naming patterns
    if any(pattern in ssid.upper() for pattern in ["FBI", "GOV", "POLICE", "FED", "MIL", "DOD", "SECURE"]):
        return "POSSIBLE_OFFICIAL"
    
    # Check for common enterprise patterns
    if any(pattern in ssid.upper() for pattern in ["CORP", "ENTERPRISE", "STAFF", "EMPLOYEE"]):
        return "ENTERPRISE"
    
    # Check for mobile hotspots
    if any(pattern in ssid.upper() for pattern in ["IPHONE", "ANDROID", "GALAXY", "MOBILE", "HOTSPOT"]):
        return "MOBILE_HOTSPOT"
    
    # Check for common public networks
    if any(pattern in ssid.upper() for pattern in ["PUBLIC", "GUEST", "FREE", "WIFI"]):
        return "PUBLIC"
    
    # Default classification
    return "STANDARD"


def print_network(network):
    """Print information about a discovered network"""
    ssid = network["ssid"]
    bssid = network["bssid"]
    channel = network["channel"]
    encryption = network["encryption"]
    signal = network["signal"]
    network_type = network["type"]
    hidden = network["hidden"]
    
    # Color coding based on network type
    if network_type == "POSSIBLE_OFFICIAL":
        type_str = "\033[91mPOSSIBLE_OFFICIAL\033[0m"  # Red
    elif network_type == "ENTERPRISE":
        type_str = "\033[94mENTERPRISE\033[0m"  # Blue
    elif network_type == "MOBILE_HOTSPOT":
        type_str = "\033[92mMOBILE_HOTSPOT\033[0m"  # Green
    elif network_type == "PUBLIC":
        type_str = "\033[93mPUBLIC\033[0m"  # Yellow
    else:
        type_str = "STANDARD"
    
    # Signal strength indicator
    if signal > -50:
        signal_str = "▂▄▆█"
    elif signal > -65:
        signal_str = "▂▄▆_"
    elif signal > -75:
        signal_str = "▂▄__"
    elif signal > -85:
        signal_str = "▂___"
    else:
        signal_str = "____"
    
    # Hidden network indicator
    hidden_str = " [HIDDEN]" if hidden else ""
    
    print(f"Found: {ssid}{hidden_str} ({bssid}) | Ch: {channel} | Enc: {encryption} | Sig: {signal} dBm {signal_str} | Type: {type_str}")


def save_results(filename):
    """Save scan results to a JSON file"""
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, filename)
    
    # Convert network dict to a list for JSON serialization
    network_list = []
    for bssid, network in networks.items():
        # Convert time values to readable format
        network["first_seen"] = datetime.fromtimestamp(network["first_seen"]).strftime("%Y-%m-%d %H:%M:%S")
        network["last_seen"] = datetime.fromtimestamp(network["last_seen"]).strftime("%Y-%m-%d %H:%M:%S")
        network_list.append(network)
    
    # Add scan metadata
    scan_data = {
        "scan_start": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "scan_end": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_networks": len(networks),
        "hidden_networks": len(hidden_networks),
        "networks": network_list
    }
    
    # Write to file
    with open(output_path, "w") as f:
        json.dump(scan_data, f, indent=4)
    
    print(f"\nResults saved to {output_path}")
    return output_path


def main():
    """Main entry point for the scanner"""
    parser = argparse.ArgumentParser(description="WifiObserver - Passive Wi-Fi Network Scanner")
    parser.add_argument("--interface", "-i", required=True, help="Wireless interface to use")
    parser.add_argument("--output", "-o", default=f"scan_{int(time.time())}.json", help="Output file name")
    parser.add_argument("--time", "-t", type=int, default=0, help="Scan duration in seconds (0 for continuous)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--detect-hidden", "-d", action="store_true", help="Focus on detecting hidden networks")
    args = parser.parse_args()
    
    global output_file
    output_file = args.output
    
    # Initialize scan
    interface = initialize_scan(args.interface)
    
    try:
        # Start packet capture
        print(f"Starting capture on {interface}. Press Ctrl+C to stop.")
        
        end_time = time.time() + args.time if args.time > 0 else None
        
        # Start the packet capture
        scapy.sniff(
            iface=interface,
            prn=process_packet,
            store=False,
            stop_filter=lambda _: end_time and time.time() > end_time
        )
        
        # If we get here, the scan completed due to timeout
        print("\nScan completed.")
        save_results(output_file)
        print(f"Discovered {len(networks)} networks ({len(hidden_networks)} hidden)")
    
    except KeyboardInterrupt:
        print("\nScan interrupted by user.")
        save_results(output_file)
        print(f"Discovered {len(networks)} networks ({len(hidden_networks)} hidden)")
    
    except Exception as e:
        logger.error(f"Error during scan: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    # Check if running as root
    if os.geteuid() != 0:
        print("Error: This script must be run as root (use sudo)")
        sys.exit(1)
    
    main()
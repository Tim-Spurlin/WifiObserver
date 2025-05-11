#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Network Classifier Module

This module provides functionality for classifying Wi-Fi networks based on
their characteristics. It uses both heuristic rules and statistical analysis
to identify different types of networks.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime

# Add parent directory to path to enable imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.wifi_scanner import initialize_scan, process_packet
from src.utils.logging_utils import setup_logger, log_header, print_network_summary

# Initialize logger
logger = setup_logger("network_classifier")

# Global dictionaries for classification rules
NETWORK_TYPES = {
    "POSSIBLE_OFFICIAL": {
        "ssid_patterns": ["FBI", "GOV", "POLICE", "FED", "MIL", "DOD", "SECURE", 
                         "AGENCY", "OFFICIAL", "LEO", "DHS", "EMERGENCY", "EMERG"],
        "characteristics": ["Hidden SSID", "Strong encryption", "Enterprise auth"]
    },
    "ENTERPRISE": {
        "ssid_patterns": ["CORP", "ENTERPRISE", "STAFF", "EMPLOYEE", "CORPORATE", 
                        "OFFICE", "BUSINESS", "COMPANY", "INC", "LLC", "LTD"],
        "characteristics": ["Enterprise auth", "Strong encryption", "Consistent signal"]
    },
    "MOBILE_HOTSPOT": {
        "ssid_patterns": ["IPHONE", "ANDROID", "GALAXY", "MOBILE", "HOTSPOT", 
                         "MiFi", "PHONE", "POCKET", "SAMSUNG", "HUAWEI", "USB"],
        "characteristics": ["Varying signal", "Temporary presence", "Limited clients"]
    },
    "PUBLIC": {
        "ssid_patterns": ["PUBLIC", "GUEST", "FREE", "WIFI", "AIRPORT", "HOTEL", 
                         "CAFE", "RESTAURANT", "OPEN", "LIBRARY", "STORE"],
        "characteristics": ["Open or simple PSK", "High client count", "Consistent presence"]
    },
    "IOT": {
        "ssid_patterns": ["CAM", "CAMERA", "RING", "NEST", "SMART", "HOME", 
                        "DEVICE", "SENSOR", "THERMOSTAT", "BULB", "TV", "ROKU"],
        "characteristics": ["Simple PSK", "Low traffic", "Specific ports open"]
    },
    "ISP_PROVIDED": {
        "ssid_patterns": ["XFINITY", "COMCAST", "SPECTRUM", "ATT", "VERIZON", 
                         "FIOS", "OPTIMUM", "COX", "CENTURYLINK", "FRONTIER", "ROUTER"],
        "characteristics": ["Strong signal", "Consistent presence", "Default naming pattern"]
    }
}

# Manufacturer classifications
MANUFACTURER_TYPES = {
    "GOVERNMENT": ["HARRIS", "GENERAL DYNAMICS", "NORTHROP", "LOCKHEED", "RAYTHEON"],
    "ENTERPRISE": ["CISCO", "ARUBA", "JUNIPER", "EXTREME", "FORTINET", "RUCKUS"],
    "CONSUMER": ["NETGEAR", "LINKSYS", "TP-LINK", "D-LINK", "BELKIN", "ASUS"],
    "MOBILE": ["APPLE", "SAMSUNG", "GOOGLE", "HUAWEI", "XIAOMI", "MOTOROLA", "HTC"],
    "IOT": ["NEST", "RING", "ECOBEE", "WYZE", "SONOS", "ROKU", "AMAZON"]
}


def classify_network(network_data):
    """Classify a network based on its characteristics

    Args:
        network_data (dict): Dictionary containing network information

    Returns:
        tuple: (classification, confidence score)
    """
    scores = {
        "POSSIBLE_OFFICIAL": 0,
        "ENTERPRISE": 0,
        "MOBILE_HOTSPOT": 0,
        "PUBLIC": 0,
        "IOT": 0,
        "ISP_PROVIDED": 0,
        "STANDARD": 0
    }
    
    # Extract network properties
    ssid = network_data.get("ssid", "").upper()
    encryption = network_data.get("encryption", "Unknown")
    hidden = network_data.get("hidden", False)
    manufacturer = network_data.get("manufacturer", "Unknown").upper()
    signal = network_data.get("signal", -100)
    
    # Check for hidden network
    if hidden:
        scores["POSSIBLE_OFFICIAL"] += 3
        scores["ENTERPRISE"] += 2
    
    # Check for strong encryption
    if encryption == "WPA2/WPA3":
        scores["POSSIBLE_OFFICIAL"] += 2
        scores["ENTERPRISE"] += 2
        scores["ISP_PROVIDED"] += 1
    elif encryption == "Open":
        scores["PUBLIC"] += 3
    
    # Check SSID patterns
    for network_type, type_data in NETWORK_TYPES.items():
        for pattern in type_data["ssid_patterns"]:
            if pattern in ssid:
                scores[network_type] += 4
    
    # Check manufacturer
    for mfg_type, mfg_list in MANUFACTURER_TYPES.items():
        for mfg in mfg_list:
            if mfg in manufacturer:
                if mfg_type == "GOVERNMENT":
                    scores["POSSIBLE_OFFICIAL"] += 4
                elif mfg_type == "ENTERPRISE":
                    scores["ENTERPRISE"] += 3
                elif mfg_type == "CONSUMER":
                    scores["STANDARD"] += 2
                    scores["ISP_PROVIDED"] += 1
                elif mfg_type == "MOBILE":
                    scores["MOBILE_HOTSPOT"] += 4
                elif mfg_type == "IOT":
                    scores["IOT"] += 4
    
    # Signal strength heuristics
    if signal > -40:  # Very strong signal
        scores["STANDARD"] += 1
        scores["ISP_PROVIDED"] += 1
    elif signal < -80:  # Weak signal
        scores["MOBILE_HOTSPOT"] += 1
    
    # Find the highest scoring classification
    max_score = max(scores.values())
    if max_score == 0:
        return "STANDARD", 0.0
    
    # Find all types with max score (in case of tie)
    candidates = [t for t, s in scores.items() if s == max_score]
    if len(candidates) == 1:
        # Clear winner
        confidence = min(1.0, max_score / 10.0)  # Scale to 0.0-1.0
        return candidates[0], confidence
    else:
        # In case of tie, choose based on priority
        priorities = ["POSSIBLE_OFFICIAL", "ENTERPRISE", "MOBILE_HOTSPOT", 
                       "PUBLIC", "IOT", "ISP_PROVIDED", "STANDARD"]
        for p in priorities:
            if p in candidates:
                confidence = min(0.7, max_score / 10.0)  # Lower confidence due to tie
                return p, confidence
    
    # Fallback
    return "STANDARD", 0.0


def enhanced_network_classification(networks):
    """Perform enhanced classification on a set of networks

    Args:
        networks (dict): Dictionary of networks to classify

    Returns:
        dict: Updated networks with enhanced classification
    """
    logger.info(f"Performing enhanced classification on {len(networks)} networks")
    
    for bssid, network in networks.items():
        classification, confidence = classify_network(network)
        network["type"] = classification
        network["classification_confidence"] = f"{confidence:.2f}"
        
        # Add additional classification information
        if classification == "POSSIBLE_OFFICIAL":
            network["classification_note"] = "This network has characteristics consistent with official/government networks. This is a heuristic classification only and should be verified."
            logger.info(f"Classified {network['ssid']} ({bssid}) as POSSIBLE_OFFICIAL with {confidence:.2f} confidence")
        
        elif classification == "ENTERPRISE":
            network["classification_note"] = "This network appears to be an enterprise/corporate network based on its characteristics."
            
        elif classification == "MOBILE_HOTSPOT":
            network["classification_note"] = "This network appears to be a mobile hotspot or temporary network."
            
        elif classification == "PUBLIC":
            network["classification_note"] = "This network appears to be a public access point."
            
        elif classification == "IOT":
            network["classification_note"] = "This network appears to be associated with IoT devices."
            
        elif classification == "ISP_PROVIDED":
            network["classification_note"] = "This network appears to be an ISP-provided default configuration."
    
    return networks


def analyze_network_distribution(networks):
    """Analyze the distribution of network types

    Args:
        networks (dict): Dictionary of networks

    Returns:
        dict: Dictionary with network type distribution
    """
    distribution = {
        "POSSIBLE_OFFICIAL": 0,
        "ENTERPRISE": 0,
        "MOBILE_HOTSPOT": 0,
        "PUBLIC": 0,
        "IOT": 0,
        "ISP_PROVIDED": 0,
        "STANDARD": 0
    }
    
    for network in networks.values():
        network_type = network.get("type", "STANDARD")
        if network_type in distribution:
            distribution[network_type] += 1
        else:
            distribution["STANDARD"] += 1
    
    return distribution


def print_classified_network(network):
    """Print information about a classified network

    Args:
        network (dict): Network information
    """
    ssid = network["ssid"]
    bssid = network["bssid"]
    network_type = network["type"]
    confidence = float(network.get("classification_confidence", 0))
    
    # Format confidence as stars
    confidence_stars = int(confidence * 5)
    stars = "★" * confidence_stars + "☆" * (5 - confidence_stars)
    
    # Color coding based on network type
    if network_type == "POSSIBLE_OFFICIAL":
        type_str = "\033[91m{}\033[0m".format(network_type)  # Red
    elif network_type == "ENTERPRISE":
        type_str = "\033[94m{}\033[0m".format(network_type)  # Blue
    elif network_type == "MOBILE_HOTSPOT":
        type_str = "\033[92m{}\033[0m".format(network_type)  # Green
    elif network_type == "PUBLIC":
        type_str = "\033[93m{}\033[0m".format(network_type)  # Yellow
    elif network_type == "IOT":
        type_str = "\033[95m{}\033[0m".format(network_type)  # Purple
    elif network_type == "ISP_PROVIDED":
        type_str = "\033[96m{}\033[0m".format(network_type)  # Cyan
    else:
        type_str = network_type
    
    print(f"{ssid} ({bssid}) | Type: {type_str} | Confidence: {stars} ({confidence:.2f})")
    
    if "classification_note" in network:
        print(f"  Note: {network['classification_note']}")


def save_classification_results(networks, filename):
    """Save classification results to a JSON file

    Args:
        networks (dict): Dictionary of classified networks
        filename (str): Output filename

    Returns:
        str: Path to the saved file
    """
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, filename)
    
    # Convert network dict to a list for JSON serialization
    network_list = list(networks.values())
    
    # Add metadata
    classification_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_networks": len(networks),
        "distribution": analyze_network_distribution(networks),
        "networks": network_list
    }
    
    # Write to file
    with open(output_path, "w") as f:
        json.dump(classification_data, f, indent=4)
    
    print(f"\nClassification results saved to {output_path}")
    return output_path


def main():
    """Main function for the classifier module"""
    parser = argparse.ArgumentParser(description="WifiObserver - Network Classifier")
    parser.add_argument("--interface", "-i", required=True, help="Wireless interface to use")
    parser.add_argument("--input", help="Input JSON file from previous scan (optional)")
    parser.add_argument("--output", "-o", default=f"classification_{int(time.time())}.json", help="Output file name")
    parser.add_argument("--scan-time", "-t", type=int, default=60, help="Scan duration in seconds (if not using input file)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()
    
    log_header("WifiObserver Network Classifier")
    
    networks = {}
    hidden_networks = set()
    
    # Use existing data or perform a new scan
    if args.input and os.path.exists(args.input):
        logger.info(f"Loading network data from {args.input}")
        print(f"Loading network data from {args.input}")
        
        try:
            with open(args.input, "r") as f:
                data = json.load(f)
                
            if "networks" in data:
                # Handle the format from wifi_scanner output
                for network in data["networks"]:
                    bssid = network["bssid"]
                    networks[bssid] = network
                    if network.get("hidden", False):
                        hidden_networks.add(bssid)
            else:
                # Try to handle other possible formats
                for bssid, network in data.items():
                    if isinstance(network, dict) and "bssid" in network:
                        networks[bssid] = network
                        if network.get("hidden", False):
                            hidden_networks.add(bssid)
                
            logger.info(f"Loaded {len(networks)} networks from file")
            print(f"Loaded {len(networks)} networks from file")
            
        except Exception as e:
            logger.error(f"Error loading input file: {str(e)}")
            print(f"Error loading input file: {str(e)}")
            sys.exit(1)
    else:
        # Perform a new scan
        if args.input:  # Input file specified but doesn't exist
            logger.warning(f"Input file {args.input} not found, performing new scan")
            print(f"Input file {args.input} not found, performing new scan")
        
        logger.info(f"Starting new network scan on {args.interface} for {args.scan_time} seconds")
        print(f"Starting new network scan on {args.interface} for {args.scan_time} seconds")
        
        # Initialize scan
        interface = initialize_scan(args.interface)
        
        # Set up globals that the wifi_scanner module uses
        import src.wifi_scanner as scanner
        scanner.networks = networks
        scanner.hidden_networks = hidden_networks
        
        try:
            # Perform the scan
            import scapy.all as scapy
            print(f"Scanning for {args.scan_time} seconds...")
            scapy.sniff(
                iface=interface,
                prn=process_packet,
                store=False,
                timeout=args.scan_time
            )
            
            print(f"Scan completed. Discovered {len(networks)} networks ({len(hidden_networks)} hidden)")
            
        except Exception as e:
            logger.error(f"Error during scan: {str(e)}")
            print(f"Error during scan: {str(e)}")
            sys.exit(1)
    
    # Perform enhanced classification
    print("\nClassifying networks...")
    classified_networks = enhanced_network_classification(networks)
    
    # Print classification results
    print("\nClassification Results:")
    print("-" * 60)
    
    # Sort networks by type for organized display
    sorted_networks = sorted(
        classified_networks.values(),
        key=lambda n: (n.get("type", "STANDARD"), -float(n.get("classification_confidence", 0)))
    )
    
    for network in sorted_networks:
        print_classified_network(network)
    
    # Print distribution summary
    distribution = analyze_network_distribution(classified_networks)
    print("\nNetwork Type Distribution:")
    for network_type, count in distribution.items():
        if count > 0:
            percent = (count / len(classified_networks)) * 100
            print(f"  {network_type}: {count} ({percent:.1f}%)")
    
    # Save classification results
    save_classification_results(classified_networks, args.output)
    
    print("\nClassification complete!")


if __name__ == "__main__":
    # Check if running as root
    if os.geteuid() != 0:
        print("Error: This script must be run as root (use sudo)")
        sys.exit(1)
    
    main()
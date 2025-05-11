#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Logging Utilities

This module provides functions for setting up logging and printing formatted
output for the WifiObserver tool.
"""

import logging
import os
import sys
from datetime import datetime
import pyfiglet


def setup_logger(name, log_level=logging.INFO):
    """Set up a logger with file and console output

    Args:
        name (str): Logger name
        log_level (int, optional): Log level. Defaults to logging.INFO.

    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Generate log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/{name}_{timestamp}.log"
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Clear any existing handlers
    if logger.handlers:
        logger.handlers.clear()
    
    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_format = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_format)
    file_handler.setLevel(log_level)
    logger.addHandler(file_handler)
    
    # Create console handler (only for errors and critical messages)
    console_handler = logging.StreamHandler(sys.stderr)
    console_format = logging.Formatter(
        "\033[91m%(levelname)s\033[0m: %(message)s"  # Red text for errors
    )
    console_handler.setFormatter(console_format)
    console_handler.setLevel(logging.ERROR)
    logger.addHandler(console_handler)
    
    logger.info(f"Logging initialized to {log_file}")
    return logger


def print_banner():
    """Print the application banner"""
    banner = pyfiglet.figlet_format("WifiObserver", font="slant")
    print("\033[94m" + banner + "\033[0m")  # Blue text
    print("\033[92m" + "A Passive Wi-Fi Network Discovery Tool" + "\033[0m")  # Green text
    print("\033[93m" + "Legal Use Only: No Unauthorized Access Attempted" + "\033[0m")  # Yellow text
    print("-" * 60)


def log_header(message):
    """Print a formatted header with the message

    Args:
        message (str): Message to display in the header
    """
    print_banner()
    print("\033[1m" + message + "\033[0m")  # Bold text
    print("-" * 60)


def print_section_header(title):
    """Print a section header

    Args:
        title (str): Section title
    """
    print("\n" + "=" * 60)
    print(f"\033[1m{title}\033[0m".center(60))  # Bold and centered
    print("=" * 60)


def print_network_summary(networks, hidden_count):
    """Print a summary of discovered networks

    Args:
        networks (dict): Dictionary of discovered networks
        hidden_count (int): Number of hidden networks
    """
    print_section_header("NETWORK SUMMARY")
    
    total = len(networks)
    
    # Count network types
    types = {
        "POSSIBLE_OFFICIAL": 0,
        "ENTERPRISE": 0,
        "MOBILE_HOTSPOT": 0,
        "PUBLIC": 0,
        "STANDARD": 0
    }
    
    # Count encryption types
    encryption = {
        "Open": 0,
        "WEP": 0,
        "WPA": 0,
        "WPA2/WPA3": 0
    }
    
    for network in networks.values():
        types[network.get("type", "STANDARD")] += 1
        encryption[network.get("encryption", "Unknown")] = encryption.get(network.get("encryption", "Unknown"), 0) + 1
    
    # Print summary
    print(f"Total Networks: \033[1m{total}\033[0m")
    print(f"Hidden Networks: \033[1m{hidden_count}\033[0m")
    
    # Print network types
    print("\nNetwork Types:")
    print(f"  - \033[91mPossible Official/Gov: {types['POSSIBLE_OFFICIAL']}\033[0m")
    print(f"  - \033[94mEnterprise: {types['ENTERPRISE']}\033[0m")
    print(f"  - \033[92mMobile Hotspots: {types['MOBILE_HOTSPOT']}\033[0m")
    print(f"  - \033[93mPublic: {types['PUBLIC']}\033[0m")
    print(f"  - Standard/Other: {types['STANDARD']}")
    
    # Print encryption types
    print("\nEncryption Types:")
    print(f"  - Open (No Encryption): {encryption['Open']}")
    print(f"  - WEP (Insecure): {encryption['WEP']}")
    print(f"  - WPA: {encryption['WPA']}")
    print(f"  - WPA2/WPA3: {encryption['WPA2/WPA3']}")
    
    print("\n" + "-" * 60)


def print_error(message):
    """Print an error message

    Args:
        message (str): Error message to display
    """
    print(f"\033[91mERROR: {message}\033[0m")  # Red error text


def print_success(message):
    """Print a success message

    Args:
        message (str): Success message to display
    """
    print(f"\033[92m✓ {message}\033[0m")  # Green success text


def print_warning(message):
    """Print a warning message

    Args:
        message (str): Warning message to display
    """
    print(f"\033[93m! {message}\033[0m")  # Yellow warning text


def print_info(message):
    """Print an info message

    Args:
        message (str): Info message to display
    """
    print(f"\033[94mi {message}\033[0m")  # Blue info text


if __name__ == "__main__":
    # Test the logging functions
    logger = setup_logger("test")
    log_header("Testing Logging Utilities")
    
    print_section_header("TEST SECTION")
    print_error("This is an error message")
    print_warning("This is a warning message")
    print_info("This is an info message")
    print_success("This is a success message")
    
    # Test network summary
    test_networks = {
        "00:11:22:33:44:55": {"ssid": "Test1", "type": "STANDARD", "encryption": "WPA2/WPA3"},
        "11:22:33:44:55:66": {"ssid": "Test2", "type": "ENTERPRISE", "encryption": "WPA2/WPA3"},
        "22:33:44:55:66:77": {"ssid": "Test3", "type": "POSSIBLE_OFFICIAL", "encryption": "WPA2/WPA3"},
        "33:44:55:66:77:88": {"ssid": "Test4", "type": "MOBILE_HOTSPOT", "encryption": "Open"},
        "44:55:66:77:88:99": {"ssid": "Test5", "type": "PUBLIC", "encryption": "WPA"}
    }
    
    print_network_summary(test_networks, 2)
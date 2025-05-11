#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface Manager Utility

This module provides functions for managing wireless interfaces, 
including setting monitor mode and checking interface status.
"""

import os
import sys
import subprocess
import re
import time
import argparse
import logging

# Set up logging
logger = logging.getLogger("interface_manager")

def check_interface(interface):
    """Check if a network interface exists

    Args:
        interface (str): The interface name to check

    Returns:
        bool: True if interface exists, False otherwise
    """
    try:
        # Try to get interface info using ip command
        result = subprocess.run(
            ["ip", "link", "show", interface],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        return result.returncode == 0
    except Exception as e:
        logger.error(f"Error checking interface: {str(e)}")
        return False


def list_wireless_interfaces():
    """List all available wireless interfaces

    Returns:
        list: List of wireless interface names
    """
    try:
        # Use iw to list wireless interfaces
        result = subprocess.run(
            ["iw", "dev"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Error listing interfaces: {result.stderr}")
            return []
        
        # Parse the output to extract interface names
        interfaces = []
        for line in result.stdout.splitlines():
            match = re.search(r"Interface\s+(\w+)", line)
            if match:
                interfaces.append(match.group(1))
        
        return interfaces
    except Exception as e:
        logger.error(f"Error listing interfaces: {str(e)}")
        return []


def check_monitor_mode(interface):
    """Check if an interface is in monitor mode

    Args:
        interface (str): The interface name to check

    Returns:
        bool: True if interface is in monitor mode, False otherwise
    """
    try:
        # Use iw to check interface mode
        result = subprocess.run(
            ["iw", interface, "info"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Error checking interface mode: {result.stderr}")
            return False
        
        # Look for monitor mode in the output
        return "type monitor" in result.stdout
    except Exception as e:
        logger.error(f"Error checking monitor mode: {str(e)}")
        return False


def set_monitor_mode(interface):
    """Set an interface to monitor mode

    Args:
        interface (str): The interface to set to monitor mode

    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Setting {interface} to monitor mode...")
    
    # Check if interface exists
    if not check_interface(interface):
        logger.error(f"Interface {interface} does not exist")
        return False
    
    # Check if already in monitor mode
    if check_monitor_mode(interface):
        logger.info(f"Interface {interface} is already in monitor mode")
        return True
    
    try:
        # First, bring the interface down
        subprocess.run(
            ["ip", "link", "set", interface, "down"],
            check=True
        )
        
        # Try using airmon-ng to enable monitor mode
        try:
            subprocess.run(
                ["airmon-ng", "check", "kill"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            subprocess.run(
                ["airmon-ng", "start", interface],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Check if monitor mode was enabled with potential interface rename
            for new_interface in list_wireless_interfaces():
                if new_interface == interface or new_interface == f"{interface}mon":
                    if check_monitor_mode(new_interface):
                        if new_interface != interface:
                            logger.info(f"Interface renamed to {new_interface} and set to monitor mode")
                        return True
        
        except subprocess.CalledProcessError:
            # If airmon-ng fails, try the iw method
            logger.warning("airmon-ng method failed, trying iw method...")
        
        # Try setting monitor mode with iw
        subprocess.run(
            ["iw", interface, "set", "monitor", "none"],
            check=True
        )
        
        # Bring the interface back up
        subprocess.run(
            ["ip", "link", "set", interface, "up"],
            check=True
        )
        
        # Verify monitor mode was set
        if check_monitor_mode(interface):
            logger.info(f"Successfully set {interface} to monitor mode using iw")
            return True
        else:
            logger.error(f"Failed to set {interface} to monitor mode")
            return False
            
    except subprocess.CalledProcessError as e:
        logger.error(f"Error setting monitor mode: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error setting monitor mode: {str(e)}")
        return False


def set_managed_mode(interface):
    """Set an interface back to managed mode

    Args:
        interface (str): The interface to set to managed mode

    Returns:
        bool: True if successful, False otherwise
    """
    logger.info(f"Setting {interface} to managed mode...")
    
    # Check if interface exists
    if not check_interface(interface) and not check_interface(f"{interface}mon"):
        logger.error(f"Interface {interface} does not exist")
        return False
    
    # If we have mon interface, use that instead
    if check_interface(f"{interface}mon"):
        interface = f"{interface}mon"
    
    try:
        # First, bring the interface down
        subprocess.run(
            ["ip", "link", "set", interface, "down"],
            check=True
        )
        
        # Try using airmon-ng to disable monitor mode
        try:
            subprocess.run(
                ["airmon-ng", "stop", interface],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Check if the original interface is back
            orig_interface = interface.replace("mon", "")
            if check_interface(orig_interface):
                interface = orig_interface
        
        except subprocess.CalledProcessError:
            # If airmon-ng fails, try the iw method
            logger.warning("airmon-ng method failed, trying iw method...")
        
        # Try setting managed mode with iw
        subprocess.run(
            ["iw", interface, "set", "type", "managed"],
            check=True
        )
        
        # Bring the interface back up
        subprocess.run(
            ["ip", "link", "set", interface, "up"],
            check=True
        )
        
        # Verify managed mode was set
        if not check_monitor_mode(interface):
            logger.info(f"Successfully set {interface} to managed mode")
            return True
        else:
            logger.error(f"Failed to set {interface} to managed mode")
            return False
            
    except subprocess.CalledProcessError as e:
        logger.error(f"Error setting managed mode: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error setting managed mode: {str(e)}")
        return False


def get_interface_mac(interface):
    """Get the MAC address of an interface

    Args:
        interface (str): The interface name

    Returns:
        str: The MAC address or None if not found
    """
    try:
        # Use ip command to get interface info
        result = subprocess.run(
            ["ip", "link", "show", interface],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Error getting interface info: {result.stderr}")
            return None
        
        # Parse MAC address from output
        for line in result.stdout.splitlines():
            match = re.search(r"link/ether\s+([0-9a-f:]{17})", line)
            if match:
                return match.group(1)
        
        return None
    except Exception as e:
        logger.error(f"Error getting interface MAC: {str(e)}")
        return None


def main():
    """Main function when script is run directly"""
    parser = argparse.ArgumentParser(description="Wireless Interface Manager")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true", help="List available wireless interfaces")
    group.add_argument("--check", metavar="INTERFACE", help="Check if interface exists")
    group.add_argument("--set-monitor", metavar="INTERFACE", help="Set interface to monitor mode")
    group.add_argument("--set-managed", metavar="INTERFACE", help="Set interface to managed mode")
    group.add_argument("--get-mac", metavar="INTERFACE", help="Get interface MAC address")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Check if running as root for operations that require it
    if (args.set_monitor or args.set_managed) and os.geteuid() != 0:
        logger.error("Error: This operation requires root privileges (use sudo)")
        sys.exit(1)
    
    # Execute the requested operation
    if args.list:
        interfaces = list_wireless_interfaces()
        if interfaces:
            print("Available wireless interfaces:")
            for iface in interfaces:
                mode = "monitor" if check_monitor_mode(iface) else "managed"
                mac = get_interface_mac(iface) or "Unknown"
                print(f"  - {iface} (Mode: {mode}, MAC: {mac})")
        else:
            print("No wireless interfaces found")
    
    elif args.check:
        if check_interface(args.check):
            mode = "monitor" if check_monitor_mode(args.check) else "managed"
            print(f"Interface {args.check} exists (Mode: {mode})")
        else:
            print(f"Interface {args.check} does not exist")
    
    elif args.set_monitor:
        if set_monitor_mode(args.set_monitor):
            print(f"Successfully set {args.set_monitor} to monitor mode")
        else:
            print(f"Failed to set {args.set_monitor} to monitor mode")
            sys.exit(1)
    
    elif args.set_managed:
        if set_managed_mode(args.set_managed):
            print(f"Successfully set {args.set_managed} to managed mode")
        else:
            print(f"Failed to set {args.set_managed} to managed mode")
            sys.exit(1)
    
    elif args.get_mac:
        mac = get_interface_mac(args.get_mac)
        if mac:
            print(f"MAC address of {args.get_mac}: {mac}")
        else:
            print(f"Failed to get MAC address of {args.get_mac}")
            sys.exit(1)


if __name__ == "__main__":
    main()
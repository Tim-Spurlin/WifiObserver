#!/bin/bash

# WifiObserver Setup Script
# This script installs all necessary dependencies for the WifiObserver tool

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}Please run as root (sudo ./setup.sh)${NC}"
  exit 1
fi

# Check if running on Kali Linux
if ! grep -q 'Kali' /etc/os-release; then
  echo -e "${YELLOW}Warning: This script is optimized for Kali Linux.${NC}"
  echo -e "${YELLOW}It may work on other Debian-based distros but is not guaranteed.${NC}"
  read -p "Continue anyway? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi

echo -e "${GREEN}Starting WifiObserver installation...${NC}"

# Update package lists
echo -e "${YELLOW}Updating package lists...${NC}"
apt update

# Install required packages
echo -e "${YELLOW}Installing required system packages...${NC}"
apt install -y \
  aircrack-ng \
  wireless-tools \
  iw \
  net-tools \
  python3-pip \
  python3-dev \
  libpcap-dev \
  wireshark \
  tshark

# Check if installation was successful
if [ $? -ne 0 ]; then
  echo -e "${RED}Failed to install system packages.${NC}"
  exit 1
fi

# Install Python dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip3 install -r requirements.txt

# Check if installation was successful
if [ $? -ne 0 ]; then
  echo -e "${RED}Failed to install Python dependencies.${NC}"
  exit 1
fi

# Create necessary directories if they don't exist
echo -e "${YELLOW}Setting up directories...${NC}"
mkdir -p logs
mkdir -p data

# Set permissions
echo -e "${YELLOW}Setting permissions...${NC}"
chmod +x src/*.py
chmod +x src/utils/*.py
chmod +x graphs/*.py

# Create symlink to make the tool easily accessible
echo -e "${YELLOW}Creating executable symlink...${NC}"
ln -sf "$(pwd)/src/wifi_scanner.py" /usr/local/bin/wifiobserver
chmod +x /usr/local/bin/wifiobserver

echo -e "${GREEN}Installation complete!${NC}"
echo -e "${GREEN}You can now run WifiObserver using: sudo wifiobserver --interface <your_interface>${NC}"
echo -e "${YELLOW}To list available wireless interfaces, run: ip a | grep wlan${NC}"
echo -e "${YELLOW}For full documentation, see the README.md and docs/ directory.${NC}"

# Check if wireless interfaces are available
INTERFACES=$(ip a | grep -o "wlan[0-9]" | sort -u)
if [ -z "$INTERFACES" ]; then
  echo -e "${RED}No wireless interfaces detected. Please ensure your wireless adapter is connected.${NC}"
else
  echo -e "${GREEN}Detected wireless interfaces:${NC}"
  for interface in $INTERFACES; do
    echo -e "  - ${GREEN}$interface${NC}"
  done
  echo -e "${YELLOW}You can use any of these interfaces with WifiObserver.${NC}"
fi

echo -e "${GREEN}To start scanning, run:${NC}"
echo -e "${YELLOW}sudo python3 -m src.wifi_scanner --interface wlan0${NC}"
echo -e "${GREEN}(Replace wlan0 with your interface)${NC}"
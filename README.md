# WifiObserver

A comprehensive tool for legitimate Wi-Fi network discovery and monitoring, designed specifically for Kali Linux.

## Overview

WifiObserver is an open-source toolkit that allows for passive detection and identification of Wi-Fi networks in your vicinity, including hidden networks. It provides detailed technical information about discovered networks without attempting to connect to or interact with them in any way.

### Key Features

- **Complete Network Discovery**: Detect all Wi-Fi networks in range, including hidden SSIDs
- **Advanced Network Classification**: Identify potential network types based on characteristics
- **Signal Analysis**: Monitor and analyze signal strength and quality
- **Terminal-based UI**: Clean, efficient interface designed for Kali Linux users
- **Logging & Reporting**: Track discoveries and generate reports for your records
- **Legal Compliance**: Designed for legitimate use within legal boundaries

## Legal Disclaimer

This tool is designed for **PASSIVE DETECTION ONLY**. It does not:
- Break encryption or attempt to decode network traffic
- Connect to any networks without explicit authorization
- Enable any form of unauthorized access

WifiObserver is intended for:
- Network administrators monitoring their own infrastructure
- Security professionals performing authorized assessments
- Educational purposes and understanding wireless network principles
- Legitimate research and network awareness

Users are responsible for complying with all local laws regarding network monitoring. Always obtain proper authorization before monitoring networks in any setting.

## Installation

### Requirements

- Kali Linux (2023.1 or later recommended)
- Python 3.9+
- Wireless adapter capable of monitor mode
- Root privileges (for interface management)

### Quick Install

```bash
# Clone the repository
git clone https://github.com/yourusername/WifiObserver.git
cd WifiObserver

# Run the setup script
chmod +x setup.sh
sudo ./setup.sh

# Install Python dependencies
pip install -r requirements.txt
```

### Manual Dependencies

If you prefer manual installation, ensure you have these utilities:
```bash
sudo apt update
sudo apt install -y aircrack-ng wireless-tools python3-pip python3-dev libpcap-dev
```

## Usage

### Basic Network Scanning

```bash
# Start the scanner
sudo python3 -m src.wifi_scanner --interface wlan0

# For detailed output with signal analysis
sudo python3 -m src.wifi_scanner --interface wlan0 --verbose --detect-hidden
```

### Interface Management

```bash
# Check available wireless interfaces
python3 -m src.utils.interface_manager --list

# Set an interface to monitor mode
sudo python3 -m src.utils.interface_manager --set-monitor wlan0
```

### Signal Analysis

```bash
# Run signal strength analysis on discovered networks
sudo python3 -m src.signal_analyzer --interface wlan0 --duration 60
```

### Network Classification

```bash
# Attempt to classify networks by characteristics
sudo python3 -m src.network_classifier --interface wlan0 --scan-time 120
```

## Visualization

Generate visualizations of discovered networks:

```bash
# Generate network type distribution graph
python3 -m graphs.network_types --input scan_results.json --output network_distribution.png

# Generate signal strength map
python3 -m graphs.signal_strength --input scan_results.json --output signal_map.png
```

## Troubleshooting

### Common Issues

**Interface not found**
```bash
# List all available interfaces
ip a

# Ensure your wireless adapter is connected and recognized
sudo airmon-ng
```

**Permission errors**
```bash
# Ensure you're running with sudo
sudo python3 -m src.wifi_scanner --interface wlan0
```

**Dependencies errors**
```bash
# Reinstall dependencies
sudo apt update
sudo apt install -y aircrack-ng wireless-tools
pip install -r requirements.txt
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
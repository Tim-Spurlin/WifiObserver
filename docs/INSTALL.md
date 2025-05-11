# Installation Guide for WifiObserver

This guide provides detailed installation instructions for setting up WifiObserver on Kali Linux.

## System Requirements

- Kali Linux (2023.1 or later recommended)
- Python 3.9+
- Wireless adapter capable of monitor mode
- Root privileges (for interface management)

## Hardware Requirements

### Compatible Wireless Adapters

WifiObserver works with most wireless adapters that support monitor mode. Here are some commonly used and recommended adapters:

1. **Alfa AWUS036ACH** - Dual-band 2.4GHz/5GHz, USB 3.0
2. **Alfa AWUS036NHA** - 2.4GHz with high gain antenna, USB 2.0
3. **Panda PAU09** - Dual-band 2.4GHz/5GHz, USB 3.0
4. **TP-Link TL-WN722N** (V1 only) - 2.4GHz, USB 2.0
5. **Built-in wireless cards** - Many built-in wireless cards in laptops support monitor mode, especially those in laptops with Kali Linux pre-installed

To check if your wireless adapter supports monitor mode:
```bash
sudo iw list | grep -A 10 "Supported interface modes:" | grep -i monitor
```

## Installation Methods

### Method 1: Automatic Installation (Recommended)

The easiest way to install WifiObserver is to use the included setup script:

```bash
# Clone the repository
git clone https://github.com/yourusername/WifiObserver.git
cd WifiObserver

# Make the setup script executable
chmod +x setup.sh

# Run the setup script as root
sudo ./setup.sh

# Install Python dependencies
pip install -r requirements.txt
```

### Method 2: Manual Installation

If you prefer to install manually or the automatic script doesn't work for your environment:

1. **Install system dependencies**:
   ```bash
   sudo apt update
   sudo apt install -y aircrack-ng wireless-tools iw net-tools python3-pip python3-dev libpcap-dev wireshark tshark
   ```

2. **Install Python dependencies**:
   ```bash
   pip install scapy python-wifi netifaces matplotlib numpy pandas rich manuf pyopenssl pyfiglet tabulate termcolor netaddr python-dateutil python-dotenv PyYAML requests
   ```

3. **Set up directories**:
   ```bash
   mkdir -p logs
   mkdir -p data
   mkdir -p graphs
   ```

4. **Make Python scripts executable**:
   ```bash
   chmod +x src/*.py
   chmod +x src/utils/*.py
   chmod +x graphs/*.py
   ```

5. **Create a symlink for easy access** (optional):
   ```bash
   sudo ln -sf "$(pwd)/src/wifi_scanner.py" /usr/local/bin/wifiobserver
   chmod +x /usr/local/bin/wifiobserver
   ```

## Troubleshooting Installation Issues

### Python Dependency Issues

If you encounter issues with Python dependencies:

```bash
# Make sure pip is up to date
pip install --upgrade pip

# Try installing dependencies one by one
pip install scapy
pip install python-wifi
# etc.
```

### Wireless Interface Not Detected

If your wireless interface isn't detected:

```bash
# List all interfaces
ip a

# Check if any wireless interfaces are recognized
sudo iw dev

# If using a USB adapter, check if it's recognized
lsusb
```

### Monitor Mode Issues

If you have trouble setting monitor mode:

```bash
# Kill processes that might interfere with monitor mode
sudo airmon-ng check kill

# Try setting monitor mode manually
sudo ip link set <interface> down
sudo iw <interface> set monitor none
sudo ip link set <interface> up
```

### Permission Issues

If you encounter permission issues:

```bash
# Make sure you're running as root for operations that require it
sudo -i

# Check file permissions
ls -la ./src/
chmod +x ./src/*.py
```

## Verifying Installation

To verify that WifiObserver is correctly installed:

```bash
# List available wireless interfaces
python3 -m src.utils.interface_manager --list

# Run a simple test scan (replace wlan0 with your interface)
sudo python3 -m src.wifi_scanner --interface wlan0 --time 10
```

If the above commands run without errors and you see output about detected networks, the installation was successful.

## Next Steps

After installation, please refer to the [Usage Guide](USAGE.md) for instructions on how to use WifiObserver effectively and within legal boundaries.
# WifiObserver Usage Guide

This guide provides detailed instructions for using WifiObserver effectively and legally on Kali Linux.

## Legal Considerations

Before using WifiObserver, please review the [Legal Considerations](LEGAL.md) document. Remember that:

- Only use this tool for legitimate purposes
- Only scan networks you own or have explicit permission to scan
- Passive scanning is generally legal, but local laws may vary
- Do not attempt to connect to networks without authorization

## Basic Usage

### Preparing Your Wireless Interface

Before scanning, you need to set up your wireless interface:

```bash
# List available wireless interfaces
sudo python3 -m src.utils.interface_manager --list

# Set an interface to monitor mode
sudo python3 -m src.utils.interface_manager --set-monitor wlan0

# Check interface status
sudo python3 -m src.utils.interface_manager --check wlan0
```

Replace `wlan0` with your actual wireless interface name.

### Basic Network Scanning

To perform a basic passive scan for networks in your area:

```bash
# Scan continuously until Ctrl+C is pressed
sudo python3 -m src.wifi_scanner --interface wlan0

# Scan for a specific duration (in seconds)
sudo python3 -m src.wifi_scanner --interface wlan0 --time 60

# Save results to a specific file
sudo python3 -m src.wifi_scanner --interface wlan0 --output my_scan.json
```

### Finding Hidden Networks

To focus on detecting hidden networks:

```bash
sudo python3 -m src.wifi_scanner --interface wlan0 --detect-hidden
```

## Advanced Usage

### Network Classification

To classify the networks you've discovered:

```bash
# Classify networks from a previous scan
sudo python3 -m src.network_classifier --interface wlan0 --input data/scan_1234567890.json

# Perform a new scan and classify immediately (scan for 120 seconds)
sudo python3 -m src.network_classifier --interface wlan0 --scan-time 120
```

### Signal Analysis

To analyze signal strength in detail:

```bash
sudo python3 -m src.signal_analyzer --interface wlan0 --duration 60
```

### Generating Visualizations

WifiObserver can generate useful visualizations of your scan results:

```bash
# Generate network type distribution chart
python3 -m graphs.network_types --input data/scan_1234567890.json --output graphs/network_types.png

# Generate signal strength chart
python3 -m graphs.signal_strength --input data/scan_1234567890.json --output graphs/signal_strength.png

# Generate discovery efficiency comparison
python3 -m graphs.discovery_efficiency --output graphs/efficiency.png
```

## Command Line Options

### WiFi Scanner

```
--interface, -i    Wireless interface to use (required)
--output, -o       Output JSON file name (default: scan_timestamp.json)
--time, -t         Scan duration in seconds (0 for continuous until Ctrl+C)
--verbose, -v      Enable verbose output
--detect-hidden    Focus on detecting hidden networks
```

### Network Classifier

```
--interface, -i    Wireless interface to use (required)
--input            Input JSON file from previous scan (optional)
--output, -o       Output JSON file name (default: classification_timestamp.json)
--scan-time, -t    Scan duration in seconds (if not using input file)
--verbose, -v      Enable verbose output
```

### Signal Analyzer

```
--interface, -i    Wireless interface to use (required)
--duration, -d     Analysis duration in seconds
--output, -o       Output JSON file name (default: signal_timestamp.json)
--interval, -n     Sampling interval in seconds (default: 1)
```

### Interface Manager

```
--list             List available wireless interfaces
--check            Check if interface exists and its mode
--set-monitor      Set interface to monitor mode
--set-managed      Set interface to managed mode
--get-mac          Get interface MAC address
```

## Interpreting Results

### Network Types

WifiObserver classifies networks into these categories:

- **POSSIBLE_OFFICIAL**: Networks with characteristics consistent with government/official entities
- **ENTERPRISE**: Corporate or organizational networks
- **MOBILE_HOTSPOT**: Personal mobile hotspots from phones or mobile devices
- **PUBLIC**: Open access points or public service networks
- **IOT**: Networks associated with Internet of Things devices
- **ISP_PROVIDED**: Default configurations from Internet Service Providers
- **STANDARD**: Networks that don't fit other classifications

> **Note**: The classification of "POSSIBLE_OFFICIAL" is based on heuristics and is not definitive. It simply indicates that a network has some characteristics commonly associated with official networks.

### Signal Strength Interpretation

Signal strength is measured in dBm (decibels relative to a milliwatt):

- **-30 to -50 dBm**: Excellent signal (Very close to AP)
- **-50 to -60 dBm**: Good signal (Reliable connection)
- **-60 to -70 dBm**: Fair signal (Acceptable performance)
- **-70 to -80 dBm**: Weak signal (May experience issues)
- **-80 to -90 dBm**: Poor signal (Unreliable connection)
- **Below -90 dBm**: Very poor (Barely detectable)

## Example Workflow

Here's a typical workflow for using WifiObserver:

1. **Preparation**:
   ```bash
   sudo python3 -m src.utils.interface_manager --set-monitor wlan0
   ```

2. **Initial Scan**:
   ```bash
   sudo python3 -m src.wifi_scanner --interface wlan0 --time 120
   ```

3. **Analyze Results**:
   ```bash
   sudo python3 -m src.network_classifier --input data/scan_1234567890.json
   ```

4. **Generate Visualizations**:
   ```bash
   python3 -m graphs.network_types --input data/classification_1234567890.json
   python3 -m graphs.signal_strength --input data/classification_1234567890.json
   ```

5. **Return Interface to Normal**:
   ```bash
   sudo python3 -m src.utils.interface_manager --set-managed wlan0
   ```

## Troubleshooting

### Common Issues

**Network scanning not finding any networks**:
- Make sure your interface is in monitor mode
- Verify that your wireless adapter supports monitor mode
- Try moving to a different location

**Permission denied errors**:
- Make sure you're running with sudo for operations that require it

**Interface not found**:
- Check that your wireless adapter is properly connected
- Try unplugging and reconnecting (if using USB)

**Python errors**:
- Verify that all dependencies are installed: `pip install -r requirements.txt`

## Extended Use Cases

### Monitoring Your Own Networks

To assess the visibility of your own networks:

```bash
# Scan for networks
sudo python3 -m src.wifi_scanner --interface wlan0 --time 300

# Check if your network is detected as hidden
python3 -m src.network_classifier --input data/scan_1234567890.json | grep -i "your_network_name"
```

### Security Auditing

For legitimate security auditing of networks you own or have permission to test:

```bash
# Long-duration scan
sudo python3 -m src.wifi_scanner --interface wlan0 --time 3600 --output security_audit.json

# Detailed classification
python3 -m src.network_classifier --input data/security_audit.json --output security_classification.json

# Generate comprehensive reports
python3 -m graphs.network_types --input data/security_classification.json --output audit/network_types.png
python3 -m graphs.signal_strength --input data/security_classification.json --output audit/signal_strength.png
```

## Getting Help

If you encounter issues or have questions:

- Check the documentation in the `docs/` directory
- Review the source code comments for detailed information
- Submit issues via GitHub if you find bugs

Remember to always use this tool responsibly and within legal boundaries.
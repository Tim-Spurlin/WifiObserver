# Legal Considerations for Wi-Fi Network Discovery

This document outlines important legal considerations when using WifiObserver or any network discovery tool. **The authors of WifiObserver are not legal professionals, and this document does not constitute legal advice.** Always consult with a legal professional regarding the specific laws in your jurisdiction.

## Passive vs. Active Scanning

WifiObserver is designed for **passive scanning only**, which means:

- It only listens for network broadcasts (beacons, probe responses)
- It does not send any packets to networks
- It does not attempt to connect to any networks
- It does not attempt to decrypt any traffic

Passive scanning is generally considered legal in most jurisdictions as you are only receiving publicly broadcast information. However, laws vary by location, so please verify the legality in your jurisdiction.

## What is Generally Legal

These activities are generally considered legal in most jurisdictions when performed with legitimate purposes:

1. **Passive detection** of Wi-Fi networks in your vicinity
2. **Viewing basic network information** (SSID, signal strength, encryption type)
3. **Identifying hidden networks** that are broadcasting but not advertising their SSID
4. **Monitoring networks you own or have explicit permission to monitor**
5. **Security testing your own networks** or networks you have explicit written permission to test

## What is Generally Illegal

These activities are generally illegal in most jurisdictions:

1. **Attempting to break encryption** or access protected networks without authorization
2. **Capturing and decrypting network traffic** without authorization
3. **Unauthorized access** to any network, even if it's open or has weak security
4. **Disrupting or interfering** with network operations (jamming, deauthentication attacks)
5. **Continuous monitoring** of networks you don't own without authorization
6. **Using network discovery for malicious purposes** such as facilitating unauthorized access

## Understanding Monitor Mode

WifiObserver uses "monitor mode" for your wireless interface, which:

- Allows your wireless card to receive all Wi-Fi packets in the vicinity
- Is necessary for passive network discovery
- Is legal to use on your own equipment
- Does NOT by itself constitute any illegal activity

Using monitor mode is similar to using a radio scanner to listen to publicly broadcast radio - the technology itself is legal, but how you use it matters.

## Jurisdiction-Specific Considerations

Laws regarding network discovery vary widely:

- **United States**: Subject to the Computer Fraud and Abuse Act (CFAA) and various state laws
- **European Union**: Subject to various computer misuse laws and GDPR for any data collection
- **United Kingdom**: Subject to the Computer Misuse Act and other legislation
- **Canada**: Subject to the Criminal Code sections on unauthorized use of computers
- **Australia**: Subject to the Criminal Code Act and state-based cybercrime legislation

## Using WifiObserver Legally

To ensure legal usage:

1. **Only use on networks you own** or have explicit permission to scan
2. **Limit scanning duration** to what's necessary for your legitimate purpose
3. **Do not attempt to connect** to any networks discovered
4. **Do not distribute or publish** information about networks you discover
5. **Document permission** if testing networks you don't own
6. **Consider notifying nearby network owners** if conducting extended scanning
7. **Be transparent** about your activities if questioned

## Government and Official Networks

Special caution is warranted regarding government and official networks:

- Many jurisdictions have specific laws protecting government networks
- Even passive scanning of certain government networks may have legal implications
- Some locations have restrictions on monitoring emergency services networks
- WifiObserver's classification of networks as "POSSIBLE_OFFICIAL" is purely heuristic and not definitive

## Educational and Research Purposes

If using WifiObserver for educational or research purposes:

- Consider obtaining Institutional Review Board (IRB) approval if appropriate
- Document your methodology and purpose
- Anonymize any data you collect
- Consider consulting with legal counsel at your institution

## Reporting Security Issues

If you discover security issues through legitimate use:

- Consider responsible disclosure to affected parties
- Do not exploit vulnerabilities
- Document your findings and how they were discovered legally
- Consult with legal counsel before disclosure if uncertain

## Disclaimer

WifiObserver is provided "as is" without warranty of any kind. The authors are not responsible for any misuse of the tool or for any illegal activities conducted with it. Users assume all legal responsibility for how they use this tool.

Remember that network security laws are evolving rapidly, and what is legal in one jurisdiction may be illegal in another. Always consult with a legal professional regarding specific laws in your jurisdiction before conducting any network discovery activities.
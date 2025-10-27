---
title: "Troubleshooting Internet (FTTH/DSL/LTE/5G)"
version: "1.2"
last_updated: "2025-27-10"
source: "Internal KB"
owner: "Tech Support"
audience: "L1 Support"
summary: "Procedury diagnozy braku lub niskiej prędkości internetu, checklista ONT/router/APN/DNS."
---

# Troubleshooting Internet (FTTH/DSL/LTE/5G)

## Overview

This document guides consultants step-by-step through diagnosing internet access problems. Always start by identifying the access technology (FTTH/DSL/LTE/5G) and devices (ONT/modem, Wi‑Fi router, LTE/5G CPE).

## Common Symptoms

- **No internet**: web pages not loading or "no connection" message
- **Slow internet**: low speed, high ping, video buffering
- **Connection drops**: every few minutes or intermittently
- **Wi‑Fi available but no internet access**
- **5 GHz disappears** or Wi‑Fi range is weak

## Root Causes — Common Reasons

### Physical Layer Issues
- Damaged fiber/Ethernet cable
- Loose connectors
- Power loss or adapter failure

### CPE/ONT/Modem Issues
- Device freeze or unresponsive state
- Incorrect WAN configuration
- Outdated or corrupted firmware

### Mobile Network Issues (LTE/5G)
- Missing or inactive APN settings
- Overloaded base station
- Weak RSRP/RSRQ/SINR signal values

### Addressing & DNS Issues
- IP address conflict
- No DNS servers configured
- CGNAT (limited ports and inbound services)

### Wi‑Fi Issues
- Radio interference from neighboring APs
- Too wide channel or inappropriate channel width
- Distance/walls causing signal degradation
- Mixed 802.11 mode settings

## Prerequisites — Before You Start

- [ ] Customer number / user_id (for verification and tools)
- [ ] Device model (ONT/router/LTE CPE)
- [ ] Connection mode (bridge/router mode)
- [ ] Credentials for CPE panel (admin password if applicable)
- [ ] Technology type: FTTH, DSL, LTE, or 5G

---

## Troubleshooting Procedures

### 1. FTTH (Fiber-to-the-Home) — No or Intermittent Internet

#### 1.1 Check ONT LEDs and Physical Connection

**PON LED Status:**
- **Solid light** → Signal OK, proceed to next steps
- **Flashing >30 seconds** → Possible optical link or authorization issue
- **Off** → No optical signal or power loss

**Power Verification:**
1. Verify the ONT power adapter is working
2. Perform power cycle: unplug for 30 seconds → replug
3. Wait for LEDs to stabilize (typically 2-3 minutes)

**Physical Inspection:**
- Check optical patchcord is not bent or pinched
- Verify SC/APC plug sits firmly in ONT socket
- Inspect for any visible cable damage

#### 1.2 Verify ONT to Router Connection

**Cable Verification:**
- Connection: ONT LAN1 port → Router WAN port
- Cable type: Cat.5e or higher
- Check connections are tight and indicators show link activity

**Router WAN Configuration:**
1. Enter router admin panel
2. Navigate to WAN Status section
3. Verify:
   - WAN IP address is assigned (DHCP or PPPoE)
   - DNS servers are configured (typically 2 addresses)
   - Connection status shows "Connected"

#### 1.3 Connection Mode Verification

**If PPPoE Mode:**
- Confirm login credentials are correct
- Disconnect and reconnect WAN interface
- Monitor logs for authentication errors

**If DHCP Mode:**
- Refresh DHCP lease from router panel
- Wait for new IP assignment (typically <30 seconds)

**Verification Checklist:**
- [ ] Web pages load in <3 seconds
- [ ] Ping to 1.1.1.1 shows <25 ms latency
- [ ] Zero packet loss on continuous ping
- [ ] No CPE log errors during last 15 minutes

#### 1.4 FTTH Edge Cases and Escalation

**Escalate to 2nd-line/Field when:**
- Optical level too low (e.g., < −28 dBm)
- Persistent PON LED flashing despite troubleshooting
- Physical fiber damage suspected

**Double NAT Issue:**
- **Symptom**: Both ONT and user's router in router mode
- **Solution A**: Set ONT to bridge mode
- **Solution B**: Configure user's router as AP/bridge mode

---

### 2. DSL — Low Speeds and Connection Drops

#### 2.1 LED and Line Parameter Diagnostics

**Modem LED Status:**
- Check DSL LED: solid green = synced, orange/blinking = retraining, red/off = no sync
- Check Internet LED: solid green = active, other states = connection issue

**Modem Admin Panel — Line Parameters:**
1. Access modem configuration panel
2. Check line parameters:
   - **SNR Margin**: If < 6 dB → line degradation likely
   - **Attenuation**: High values may indicate line quality issues
   - **Speed Profile**: Should match contracted service level

**Action if Degraded:**
- Disconnect all phone splitters and test "direct" with modem only
- Change RJ11 cable and port on wall jack
- Perform 30-second power cycle of modem

#### 2.2 DSL Configuration Optimization

**Modulation Mode:**
- Set modulation to "Auto" if manual setting exists
- Check profile selection: ADSL2+/VDSL with Auto-negotiation enabled

**Reset Procedure (if needed):**
1. Access modem management interface
2. Use "Reset DSL Port" option (without factory reset)
3. Allow 2-3 minutes for re-synchronization
4. Monitor for stable connection

#### 2.3 DSL Verification and Monitoring

**Verification Checklist:**
- [ ] Speeds within 80–120% of contracted agreement
- [ ] SNR Margin > 6 dB and stable
- [ ] Attenuation normal for line length
- [ ] Connection stable for ≥15 minutes without retrain events
- [ ] Modem log shows no repeated errors

#### 2.4 DSL Edge Cases

**Common Issues:**
- Bad filtering on micro-splitters → test without splitter
- Old internal wiring degradation → escalate to field
- Interference from phone line → ensure proper shielding
- Seasonal issues (humidity/temperature) in underground lines

---

### 3. LTE/5G CPE — No Internet or Slow Connection

#### 3.1 Signal Quality Assessment

**Access CPE Admin Panel:**
1. Open CPE web interface or mobile app
2. Navigate to Network Status section
3. Record signal metrics:
   - **RSRP** (Reference Signal Received Power): target > −120 dBm
   - **RSRQ** (Reference Signal Received Quality): target > −15 dB
   - **SINR** (Signal-to-Interference Noise Ratio): target > 0 dB

**Signal Optimization:**
- If signal is weak: move device closer to window or higher location
- Remove obstacles between CPE and external wall
- Try different room locations for 5-10 minutes to assess variation

#### 3.2 APN Configuration Verification

**Typical APN Settings for Common Operators:**
```
Name: "Internet" or "Operator Internet"
APN: internet (or operator-specific value)
Authentication Type: PAP/CHAP (auto-detect)
Username: (usually empty)
Password: (usually empty)
Other fields: Leave empty unless explicitly required
```

**APN Verification Steps:**
1. Compare current settings with operator documentation
2. If changed, save and restart CPE
3. Monitor connection stabilization (2-3 minutes)

**Verify Network Registration:**
- Force auto-selection mode (don't lock to specific band)
- Allow CPE to reselect best available cell/band
- After SIM replacement: allow 5-10 minutes for full re-registration

#### 3.3 Speed Testing and Validation

**Testing Procedure:**
- Run Speedtest.net or equivalent during off-peak hours
- Record download/upload speeds and latency
- Compare against typical values for local operators

**Verification Checklist:**
- [ ] Download speed matches typical local LTE/5G speeds
- [ ] Upload speed acceptable for use case
- [ ] Ping < 60 ms (lower is better)
- [ ] Consistent results across multiple tests

#### 3.4 LTE/5G CPE Edge Cases

**No Signal or Registration Issues:**
- SIM may be blocked or inactive
- Data service not activated on account
- IMEI may be locked by operator
- eSIM profile not activated

**Very Variable Speeds:**
- Test at different hours (suspect sector congestion)
- Check for signal variation with movement
- Monitor for periodic band/cell reselection in logs

---

### 4. Wi‑Fi Connected but "No Internet" Issue

#### 4.1 DHCP and IP Address Verification

**Client-Level Diagnostics:**
1. Check if device received IP address from router:
   - Access router admin panel → client/device list
   - Verify client has valid IP address (not 169.254.x.x or 0.0.0.0)

**If No IP Address:**
- Try "renew DHCP lease" on client device
- Access router → DHCP settings → verify DHCP pool size
- Restart router (30-second power cycle)

#### 4.2 Router WAN and DNS Validation

**WAN Status Check:**
1. Access router admin panel
2. Navigate to WAN Status:
   - Verify WAN IP is assigned and valid
   - Confirm DNS servers are configured (two addresses minimum)

**If Router Has No WAN Connection:**
- Return to appropriate technology troubleshooting (FTTH/DSL/LTE section)
- Verify cables and physical layer before continuing Wi-Fi troubleshooting

#### 4.3 DNS Resolution on Client

**Windows:**
```
ipconfig /flushdns
ipconfig /renew
```

**macOS/Linux:**
```
sudo dscacheutil -flushcache
```

**Configure Public DNS in Router:**
- Set primary DNS: 1.1.1.1 (Cloudflare) or 8.8.8.8 (Google)
- Set secondary DNS: 1.0.0.1 or 8.8.4.4

#### 4.4 Access Control Verification

**Check Router Settings:**
- [ ] MAC filtering not blocking client
- [ ] Parental controls not preventing access
- [ ] Guest network isolation not applied
- [ ] Firewall rules not blocking client

**Verification:**
- [ ] After DNS flush/refresh, web pages load in <3 seconds
- [ ] HTTPS sites load without certificate errors
- [ ] DNS resolution works (nslookup google.com)

#### 4.5 Wi‑Fi "No Internet" Edge Cases

- **Captive portal in guest network**: Check router guest network settings
- **Browser proxy settings**: Configure proxy only if corporate environment requires
- **Client-specific block**: Review router logs for blocked connections

---

### 5. Connection Drops Every Few Minutes

#### 5.1 Log Analysis and Pattern Identification

**Access Router Logs:**
1. Navigate to router system logs
2. Look for patterns:
   - WAN interface up/down transitions
   - PPPoE reconnect events (DSL)
   - LTE cell reselection logs
   - Repeated error messages at specific intervals

**Common Log Indicators:**
- PPPoE: "Authentication failed" → WAN configuration issue
- LTE: Frequent "Cell reselection" → weak/unstable signal
- Fiber: "Link down/up" → optical or power issue

#### 5.2 Feature Temporary Disabling

**For Stability Testing (24-48 hours):**
1. Disable QoS (Quality of Service) settings
2. Disable IDS/firewall advanced features
3. Disable USB tethering if enabled
4. Disable UPnP if not essential

**After Disabling:**
- Monitor continuous connection for 30-60 minutes
- If stability improves, re-enable features individually
- Identify which feature caused instability

#### 5.3 Firmware and Configuration Optimization

**Firmware Update Procedure:**
1. Check available stable firmware version (not beta/RC)
2. Update during off-peak hours (impact window: 5-10 minutes)
3. Verify router reboots and reconnects
4. Monitor logs for first 30 minutes post-update

**Wi‑Fi Channel Optimization:**
```
2.4 GHz Band (non-overlapping channels):
  - Channel 1, 6, or 11 (select one)
  - Scan for interference from neighboring APs
  - Set channel width: 20 MHz (for stability)

5 GHz Band (wider availability):
  - Scan available channels (UNII-1: 36-48, UNII-3: 149-165)
  - Avoid UNII-2 (120-144) due to weather radar restrictions
  - Set 40 or 80 MHz width (20 MHz for stability)
```

**Selection Strategy:**
1. Use Wi-Fi analyzer tool to identify least congested channel
2. Select channel with strongest signal and minimum neighbor interference
3. Test with narrow channel width (20 MHz) first for stability

#### 5.4 Connection Drops Verification

**Continuous Monitoring (30-60 minutes):**
- [ ] No WAN/PPPoE reconnects in logs
- [ ] No LTE cell reselection events
- [ ] Wi‑Fi clients maintain stable connection
- [ ] No error messages in system logs
- [ ] Ping response consistent (no timeouts)

#### 5.5 Connection Drops Edge Cases

- **Microwave interference**: 2.4 GHz band affected during microwave use
- **Bluetooth interference**: Check for conflict with 2.4 GHz devices
- **Thermal throttling**: Router overheating → check ventilation/temperature
- **Memory leak**: Monitor router RAM usage; restart weekly if necessary
- **Neighboring AP interference**: Switch channels or adjust TX power

---

### 6. CGNAT and Remote Access Issues

#### 6.1 CGNAT Explanation and Detection

**What is CGNAT?**
- Operator-level NAT that hides multiple customers behind single public IP
- Limits inbound connection initiation from internet
- Prevents port forwarding effectiveness
- May cause issues with: gaming, video conferencing, remote access

**Detection Method:**
1. Access router WAN IP settings
2. If IP starts with 100.64.x.x — 100.127.x.x: CGNAT active
3. Compare router WAN IP with external IP check (whatismyipaddress.com)
4. If different → CGNAT in use

#### 6.2 CGNAT Workaround Options

**Option 1: IPv6 (if available)**
- Check if IPv6 prefix delegated to router
- Configure services on IPv6 (generally not firewalled by operator)
- Verification: Test external IPv6 connectivity

**Option 2: Public IPv4 Upgrade**
- Contact operator for dedicated public IPv4
- Typically paid premium service
- Allows standard port forwarding and inbound services

**Option 3: VPN/Tunnel Solution**
- Install VPN server on router (e.g., WireGuard/OpenVPN)
- Route client traffic through encrypted tunnel
- Allows remote access without port forwarding
- Trade-off: Added latency and server overhead

**Option 4: Manufacturer P2P Services**
- Use camera/NAS vendor-specific cloud services
- Requires account setup with service provider
- Generally easier for non-technical users
- Limited control and privacy considerations

#### 6.3 Verification After CGNAT Workaround

**Testing Checklist:**
- [ ] Remote connection works after changes
- [ ] Port forwarding test passes (portchecker.co or similar)
- [ ] Inbound connections establish within reasonable time
- [ ] No unusual router restart or logs

#### 6.4 CGNAT Edge Cases

- **Double NAT scenario**: Customer's own router behind another router
- **Solution**: Enable bridge mode or AP mode on second router
- **IPv6 preference**: Some services may need explicit IPv4 or IPv6 selection

---

## General Verification and Post-Repair Checks

### Step-by-Step Verification Procedure

#### 1. Web Browsing Test
- [ ] Open 3 different websites (HTTP and HTTPS)
- [ ] Pages load fully within <3 seconds
- [ ] No timeout errors or connection refused messages

#### 2. Network Connectivity Test
```
Ping to 1.1.1.1:  <60 ms latency, ≤1% packet loss
Ping to github.com: <60 ms latency, ≤1% packet loss
```

#### 3. Speed Verification
- [ ] Run Speedtest during off-peak hours
- [ ] Download/upload speeds: 80–120% of typical link throughput
- [ ] Latency appropriate for technology (FTTH <10 ms, DSL <20 ms, LTE <50 ms)

#### 4. Stability Monitoring
- [ ] 15-minute continuous monitoring without disconnects
- [ ] No critical error messages in CPE logs
- [ ] Router/modem temperature normal
- [ ] CPU/RAM usage stable

#### 5. Customer Acceptance
- [ ] Customer confirms issue is resolved
- [ ] Service meets their requirements
- [ ] All troubleshooting steps documented
- [ ] Next escalation procedure explained if necessary

---

## Advanced Notes and Best Practices

### Bridge Mode Deployment

**When to Use Bridge Mode:**
- Customer has high-end router equipment
- Need to disable FTTH ONT routing features
- Prevent double NAT scenarios
- Simplify network architecture

**Important Considerations:**
- Document original configuration before change
- Verify customer understands bridge mode operation
- Ensure customer router has compatible WAN configuration
- Test connectivity immediately after change

### PPPoE vs DHCP Selection

**DHCP Mode:**
- Simpler configuration
- Operator assigns IP directly
- No credentials needed
- Typical for FTTH and LTE/5G

**PPPoE Mode:**
- Additional authentication layer
- Common for DSL in some regions
- Operator provides username/password
- Useful for traffic accounting/billing

**Troubleshooting:**
- Wrong PPPoE credentials → blocks entire session
- DHCP lease conflict → renew or change lease time
- PPPoE session timeout → check modem line quality

### Firmware Update Best Practices

**Before Updating:**
- [ ] Backup current configuration if possible
- [ ] Schedule during maintenance window
- [ ] Notify customer of brief downtime (5-15 minutes)
- [ ] Have device model and current firmware version ready

**During Update:**
- [ ] Do NOT power off during firmware flash
- [ ] Wait for full reboot completion (5-10 minutes)
- [ ] Monitor for any error messages or LED anomalies

**After Update:**
- [ ] Verify basic connectivity immediately
- [ ] Check that user settings preserved (if applicable)
- [ ] Monitor logs for first 30 minutes
- [ ] Document firmware version for future reference

### eSIM and SIM Management

**After SIM Replacement or APN Changes:**
- Allow 5-10 minutes for full network re-registration
- Monitor for "Registering..." state in CPE panel
- Verify correct MCC/MNC (Mobile Country/Network Code) appears
- Re-enter or verify APN settings post-registration

**SIM Issues Requiring Escalation:**
- SIM blocked or deactivated by operator
- Data service not activated on account
- IMEI restrictions preventing registration
- eSIM profile corruption or non-activation

---

## Glossary of Abbreviations and Terms

| Term | Definition |
|------|-----------|
| **ONT** | Optical Network Terminal — device converting optical signal to electrical for FTTH |
| **CPE** | Customer Premises Equipment — any device at customer location (router, modem, etc.) |
| **FTTH** | Fiber-to-the-Home — broadband delivered via optical fiber to customer premises |
| **CGNAT** | Carrier-Grade NAT — operator-level NAT limiting inbound connections |
| **PPPoE** | Point-to-Point Protocol over Ethernet — authentication protocol for DSL |
| **DHCP** | Dynamic Host Configuration Protocol — automatic IP address assignment |
| **RSRP** | Reference Signal Received Power — LTE/5G signal strength (-140 to -44 dBm) |
| **RSRQ** | Reference Signal Received Quality — LTE/5G signal quality (-19.5 to -3 dB) |
| **SINR** | Signal-to-Interference Noise Ratio — LTE/5G signal quality (typically 0 to 50 dB) |
| **APN** | Access Point Name — settings connecting mobile device to operator network |
| **SNR Margin** | Signal-to-Noise Ratio Margin in DSL — indicates line stability (6+ dB desired) |
| **Attenuation** | Signal loss over DSL line distance (dB) |
| **LED** | Light Emitting Diode — status indicator on CPE devices |
| **UNII** | Unlicensed National Information Infrastructure — 5 GHz Wi-Fi bands |

---

## References and Related Documentation

- **02_router_wifi.md** — Router Setup & Wi‑Fi Configuration
- **03_apn_bridge.md** — APN Configuration & Bridge Mode Procedures
- **04_known_issues.md** — Known Issues & Workarounds
---

## Notes for TechnicalAgent (RAG Implementation)

- **Response Constraint**: Respond only based on cited sections in this document
- **Retrieval Threshold**: When retriever returns fewer than 3 matching fragments, ask for clarification or indicate lack of documented information
- **Search Optimization**: This document is structured with semantic headers for vector DB optimal chunking and retrieval
- **Audience Context**: Always consider that L1 Support staff may have limited technical knowledge; provide step-by-step guidance
- **Escalation Guidance**: Clearly indicate when issues require 2nd-line or field technician intervention
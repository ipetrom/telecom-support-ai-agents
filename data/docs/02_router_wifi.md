---
title: "Router Setup & Wi‑Fi Optimization"
version: "1.2"
last_updated: "2025-27-10"
source: "Internal KB"
owner: "Tech Support"
audience: "L1 Support"
summary: "Konfiguraciya SSID/WPA2-WPA3, kanały, band steering, sieć gościa, Mesh, QoS. Kroki-krok procedury i weryfikacja jakości Wi‑Fi."
---

# Router Setup & Wi‑Fi Optimization

## Overview

**Goal**: Fast, stable, and secure Wi‑Fi.

This guide covers:
1. Basic router configuration (SSID, password, encryption)
2. Radio optimization (channels, bands, width)
3. Advanced features (mesh, QoS, access control)
4. Diagnostics and verification tests

Start with basic configuration, then proceed to radio optimization and extra features. Conclude with verification testing.

## Prerequisites — Before You Start

- [ ] Router/CPE model and firmware version
- [ ] Login credentials for the panel (admin)
- [ ] Access technology information (FTTH/DSL/LTE/5G)
- [ ] Operation mode (router/bridge/AP)
- [ ] Customer requirements (coverage area, device types)

---

## Quick Fix — Rapid Checklist (60–120 seconds)

Use this checklist for immediate symptom resolution:

1. **Power Cycle**: Restart the router (unplug 30 seconds → replug)
2. **Wi‑Fi Status**: Verify Wi‑Fi is enabled and SSID is visible
3. **Password Check**: Ensure password has no trailing spaces or unsupported special characters
4. **Channel Selection**:
   - 2.4 GHz: Set to channel 1, 6, or 11 (least interference)
   - 5 GHz: Set to UNII-1/3 channel (36–48 or 149–165)
5. **Channel Width Adjustment**:
   - 2.4 GHz → 20 MHz (for stability)
   - 5 GHz → 40/80 MHz (or reduce to 40 MHz in noisy environments)

---

## Accessing the Router Panel

### Step-by-Step Login Procedure

**Connection Options:**
- Via **LAN cable**: Most reliable, always works even if Wi-Fi is misconfigured
- Via **Wi‑Fi**: From existing network

**Panel Access:**
1. Open web browser
2. Enter router panel address:
   - Typical addresses: `192.168.0.1`, `192.168.1.1`, or `192.168.100.1`
   - Check router sticker or manual if unsure
3. Log in with admin credentials
4. Navigate to Wi‑Fi or Network settings section

### Factory Reset (Last Resort)

**When to Use:**
- Locked out of admin account
- Forgotten password
- Corrupted configuration

**Reset Procedure:**
1. Locate physical Reset button on router (usually recessed)
2. Hold for 10–15 seconds while powered on
3. Wait for reboot (LED blink sequence completes)
4. **⚠️ Warning**: All custom settings will be lost; default credentials restore

---

## Basic Wi‑Fi Configuration

### 1. SSID (Network Name)

**Settings:**
- **SSID Name**: Clear, descriptive name (e.g., "Home_Network", "Office_WiFi")
- **Avoid**: Personal data, phone numbers, or sensitive information
- **Visibility**: Keep SSID visible (broadcast enabled)

**Why Not Hide SSID?**
- Hiding SSID does NOT increase security
- Makes device connections more difficult
- Can confuse technical support
- Determined attackers can still discover it

### 2. Encryption and Password

**Security Standard Selection:**

| Standard | Security Level | Compatibility | Recommendation |
|----------|---|---|---|
| **WPA3-Personal** | Highest | Modern devices (2019+) | **Prefer this** |
| **WPA2/WPA3 Mixed** | High | Mixed old/new devices | Use if older devices present |
| **WPA2 only** | Adequate | Very old devices (2004+) | Only if required for legacy IoT |
| **WEP/WPA-TKIP** | Compromised | Very old (<2004) | **NEVER use** |

**Password Requirements:**
- **Minimum length**: 12 characters
- **Character types**: Mix of uppercase, lowercase, numbers, symbols
- **Avoid**: Dictionary words, sequential numbers, personal information
- **Example**: `Tr0pic@l-Wave#24` (good), `mypassword123` (poor)

**Special Characters to Avoid:**
```
⚠️ Emoji/Unicode characters
⚠️ Leading/trailing spaces
⚠️ Non-ASCII special characters
✓ Use ASCII only: a-z, A-Z, 0-9, @#$%^&*()_+-={}[]|:;<>,.?/
```

### 3. Bands Configuration

**Available Bands:**

- **2.4 GHz Band**:
  - Range: ~100 meters (good wall penetration)
  - Speed: Up to 600 Mbps (802.11n) or 1 Gbps (802.11ax)
  - Pros: Better range, more devices support
  - Cons: Crowded, interference from microwaves/Bluetooth

- **5 GHz Band**:
  - Range: ~50 meters (weaker penetration)
  - Speed: Up to 1.3 Gbps (802.11ac) or 9.6 Gbps (802.11ax)
  - Pros: Less crowded, higher speeds
  - Cons: More affected by obstacles

- **6 GHz Band** (Wi-Fi 6E only):
  - Range: Similar to 5 GHz
  - Speed: Up to 9.6 Gbps
  - Pros: Newest, widest channels, least congestion
  - Cons: Limited device support (requires 2024+ devices)

**Configuration Strategy:**

**Option A: Single SSID (Band Steering)**
```
SSID: "Home_Network"
- Both 2.4 GHz and 5 GHz enabled
- Router automatically steers devices to best band
- Seamless experience when moving between zones
- Simplest setup
```

**Option B: Separate SSIDs**
```
SSID 2.4 GHz: "Home_Network_24G"
SSID 5 GHz:   "Home_Network_5G"
- Manual control for users
- Better for troubleshooting (diagnose which band)
- Useful when 2.4 GHz IoT devices conflict with 5 GHz
```

### 4. Band Steering

**What It Does:**
- Automatically moves devices from 2.4 GHz to 5 GHz when signal is strong
- Prioritizes 5 GHz for high-speed capable devices
- Keeps older/distant devices on 2.4 GHz

**Recommendation:** **Enable** band steering for optimal performance

### 5. Channels and Channel Width

#### 2.4 GHz Channel Selection

**Available Channels:** 1–13 (varies by region)

**Non-Overlapping Channels:**
```
Channel 1:  2.412 GHz
Channel 6:  2.437 GHz
Channel 11: 2.462 GHz
(These three do not overlap)
```

**Channel Width:**
- **20 MHz**: Standard, most stable, recommended for most environments
- **40 MHz**: Double bandwidth, but higher interference risk

**Selection Procedure:**
1. Use Wi-Fi analyzer tool (e.g., WiFi Analyzer app) on smartphone
2. Scan for neighboring networks and their channels
3. **Select channel with fewest neighbors**:
   - If neighbors on 1 & 11 → choose 6
   - If neighbors on 1 & 6 → choose 11
   - If neighbors on 6 & 11 → choose 1
4. Keep width at 20 MHz for stability

#### 5 GHz Channel Selection

**Channel Groups (UNII Bands):**

| Band | Channels | Notes |
|------|----------|-------|
| **UNII-1** | 36–48 | No DFS, safest choice |
| **UNII-2 (DFS)** | 52–144 | Radar interference possible |
| **UNII-3** | 149–165 | No DFS, wide availability |
| **UNII-4** | 169–177 | Future/limited support |

**DFS (Dynamic Frequency Selection) Explained:**
- Channels 52–144 require DFS support
- Router must listen for weather radar signals
- If radar detected → channel automatically switches (5–30 second interruption)
- **Not recommended** for critical services or IoT devices
- **Recommended channels**: 36–48 (UNII-1) or 149–165 (UNII-3)

**Channel Width Options:**
```
20 MHz:  Narrow, very stable, lowest throughput
40 MHz:  Medium, balance of stability/throughput
80 MHz:  Wide, high throughput, potential interference
160 MHz: Very wide, unstable in most environments
```

**Selection Strategy:**
- **Dense urban environment**: 20–40 MHz width, select least congested channel
- **Suburban/home**: 80 MHz width, monitor for stability
- **Isolated location**: Can use 160 MHz safely

**Channel Selection Procedure:**
1. Use Wi-Fi analyzer to scan for neighboring 5 GHz networks
2. **Prefer UNII-1 (36–48) over DFS channels**
3. If UNII-1 occupied:
   - Select UNII-3 (149–165) if available
   - Only use DFS channels if critical for bandwidth
4. Set width to 80 MHz initially; reduce if drops occur

### 6. Country/Region and Transmit Power

**Country Setting:**
- **Impact**: Determines allowed channels and DFS regulations
- **Correct Setting**: Must match customer's actual location
- **Effect**: Missing channels if set incorrectly
- **Action**: Navigate to Wireless → Regional Settings → Select correct country

**Transmit Power:**
- **Options**: Auto, High, Medium, Low
- **Recommendation**: Auto or Medium
- **Why Not High?**
  - Increases interference to neighboring networks
  - Causes uplink asymmetry (clients can hear router but router hears them weakly)
  - May violate local radio regulations
  - Does NOT significantly improve coverage
- **Better for Coverage**: Move router higher or to central location

---

## Advanced Features and Configuration

### 1. Guest Network

**Purpose:**
- Separate network for visitors
- Isolate guest devices from main network resources
- Control bandwidth and access

**Configuration:**

**Basic Settings:**
- **SSID**: "Home_Guest" or "Network_Guest" (descriptive)
- **Encryption**: WPA3 (same security as main network)
- **Password**: Separate from main network

**Advanced Options:**
- **Client Isolation**: Prevent guests from seeing/accessing each other
- **VLAN**: Isolated network segment (if router supports)
- **IP Range**: Separate subnet (e.g., 192.168.50.x vs 192.168.1.x)
- **Speed Limit**: Optional bandwidth cap per device or total
- **Schedule**: Optional time-based enable/disable
- **Captive Portal**: Redirect to login/acceptance page (enterprise use)

**Typical Setup:**
1. Enable guest network
2. Set SSID and strong password
3. Enable client isolation
4. Leave other options at defaults (unless specific requirements)

### 2. Mesh, Repeater, and AP Mode

#### Mesh Networks

**What It Is:**
- Multiple units (main router + satellites) communicating wirelessly
- Seamless roaming (devices move between units automatically)
- Maintains connection speed better than repeater

**Setup Procedure:**
1. Place main router in central location
2. Connect satellites via:
   - **WPS**: Press WPS button on both units
   - **QR Code**: Scan code from router panel
   - **Manual Panel**: Enter SSID/password of main network
3. **Optimal**: Use wired backhaul between units (faster, more stable)
   - Connect satellite to main via Ethernet cable
   - Most routers auto-detect wired backhaul

**Verification:**
- All units show same SSID
- Clients roam seamlessly between units
- No manual reconnection needed

#### Repeater Mode

**What It Is:**
- Secondary unit wirelessly extends existing network
- Similar SSID, same network segment
- Reduced throughput (half duplex on wireless backhaul)

**When to Use:**
- Only when wired connection impossible
- Temporary solution (low priority)

**Limitations:**
- Bandwidth typically 50% of main router
- Adds latency to connection
- Not recommended for gaming/video conferencing

#### AP (Access Point) Mode

**What It Is:**
- Router configured as "dumb" access point
- Main router provides DHCP and routing
- AP only provides Wi-Fi

**When to Use:**
- Primary router is separate (e.g., operator's CPE as main)
- Need multiple Wi-Fi access points
- Avoid double NAT scenarios

**Configuration:**
1. Set device to AP mode in administration panel
2. Connect to main network via Ethernet
3. Main router's DHCP provides IP addresses
4. Disable router's DHCP server (set to AP mode)

**Verification:**
- Devices get IP from main router (e.g., 192.168.1.x)
- No double NAT in network trace (pingpath)

### 3. QoS (Quality of Service) and WMM

**What Is QoS?**
- Prioritizes traffic by application or device
- Ensures VoIP/video conferencing gets priority
- Prevents one device from saturating connection

**WMM (Wi‑Fi Multimedia):**
- Basic QoS feature, enables device-level prioritization
- **Always enable** — very low overhead

**QoS Profiles:**

| Profile | Priority | Use Case |
|---------|----------|----------|
| Auto | Automatic | Most users - recommended |
| VoIP | High | Video conferencing, phone calls |
| Streaming | Medium | Video/music streaming |
| Best Effort | Low | General browsing, downloads |
| Background | Lowest | Backups, large downloads |

**Configuration Recommendation:**
1. **Enable WMM**: Almost always beneficial
2. **QoS Profile**: Set to "Auto" for most users
3. **Manual Limits**: Only if specific issue (e.g., gaming lag from uploads)
   - Avoid excessive restrictions — can throttle normal traffic
   - Test before and after changes

**Do NOT:**
- Set extremely low bandwidth limits
- Prioritize multiple competing protocols
- Enable unless experiencing specific issues

### 4. Filters and Access Control

#### MAC Filtering

**What It Is:**
- Whitelist/blacklist devices by hardware address
- Prevent specific devices from connecting

**Security Note:**
- Easy to spoof MAC addresses
- Does NOT increase security meaningfully
- Difficult to maintain

**When to Use:**
- Corporate/institutional environment with specific requirements
- Temporary blocking of known problematic device
- NOT for general security

**Better Alternatives:**
- Parental controls (more flexible)
- Network segmentation with VLANs
- Client certificate authentication

#### Parental Controls

**Features:**
- **Time-based blocking**: Schedule when internet is available
- **Category filtering**: Block websites by category (adult, gambling, etc.)
- **DNS-based**: Filters at DNS level (works on all devices)

**Configuration:**
1. Enable parental controls
2. Create profiles for devices/users
3. Set filtering categories
4. Configure time schedules (if needed)

**Limitations:**
- DNS-based filtering can be bypassed by VPN
- Not effective for encrypted traffic inspection
- Requires regular updates to category database

#### UPnP (Universal Plug and Play)

**What It Does:**
- Allows applications to automatically configure port forwarding
- Enables devices to discover each other

**Security Considerations:**
- **Pros**: Automatic configuration, gaming/IoT ease
- **Cons**: Can expose services unintentionally
- **Enabled by default** on most routers

**Recommendation:**
- Leave enabled for most users
- Disable in high-security environments or if suspicious activity detected
- Not primary attack vector if firewall properly configured

### 5. IPv6 Configuration

**What Is IPv6?**
- Next-generation internet protocol (replaces IPv4)
- Larger address space, built-in security features
- Increasing adoption by ISPs

**Enable If:**
- ISP provides IPv6 (check with operator)
- Modern devices on network
- Want future-proof configuration

**Common Settings:**

| Setting | Option | Notes |
|---------|--------|-------|
| **IPv6 Enable** | On | Enable if ISP supports |
| **Address Mode** | SLAAC or DHCPv6 | SLAAC simpler, DHCPv6 more controlled |
| **Prefix** | From ISP | ISP provides /56 or /60 prefix |
| **Firewall** | Enabled | Block inbound by default |
| **Exceptions** | As needed | Whitelist specific inbound ports |

**Router NAT (IPv4):**
- Typically enabled on router (router performs NAT)
- Can disable if ISP provides public IPv4 for each client
- Most common: Enable NAT

### 6. Updates and Backups

**Before Any Update:**

1. **Backup Configuration**:
   - Navigate to Administration → Backup/Export
   - Save configuration file to computer
   - Store safely (email or cloud storage)

2. **Schedule Update**:
   - Choose off-peak hours (late night, early morning)
   - Notify customer of brief downtime (5–15 minutes)
   - Avoid critical business hours

**Update Procedure:**

1. Access Administration → Firmware Update
2. Check available stable firmware (not beta/RC)
3. Click "Update" or "Upgrade"
4. **Do NOT power off** during update (risk of brick)
5. Wait for automatic reboot (5–10 minutes)
6. Monitor LED sequence until stabilization

**After Update:**

- [ ] Verify Wi-Fi is enabled and SSID visible
- [ ] Test connectivity from Wi‑Fi device
- [ ] Check that custom settings preserved
- [ ] Review Wi‑Fi settings (sometimes reset to defaults)
- [ ] Monitor logs for 30 minutes post-update

---

## Diagnostics and Optimization

### 1. Signal Quality Metrics

**RSSI (Received Signal Strength Indicator):**
- Range: −100 dBm (very weak) to −30 dBm (very strong)
- Target for applications:

| dBm Value | Quality | Recommended For |
|-----------|---------|-----------------|
| > −50 | Excellent | All applications |
| −50 to −60 | Very Good | All applications |
| −60 to −70 | Good | General use, VoIP |
| −70 to −80 | Acceptable | Browsing, email |
| < −80 | Poor | Limited functionality |

**For VoIP/Video Conferencing**: Target RSSI > −67 dBm  
**For Streaming**: Target RSSI > −70 dBm

**SNR (Signal-to-Noise Ratio):**
- Measures signal quality against background noise
- Higher values indicate better quality

| SNR Value | Quality |
|-----------|---------|
| ≥ 25 dB | Excellent |
| 15–25 dB | Average |
| < 15 dB | Poor |
| < 5 dB | Connection unreliable |

### 2. Common Problems and Solutions

#### Problem: "Wi‑Fi Visible but No Internet"

**Root Cause Analysis:**
1. Wi-Fi connection works (MAC shows in router client list)
2. But device cannot access internet

**Troubleshooting Steps:**

**Step 1: Router WAN Status**
- Access router panel
- Check WAN section:
  - [ ] WAN IP address assigned (not 0.0.0.0)
  - [ ] DNS servers listed (typically 2)
  - [ ] Status shows "Connected"
- **If not connected**: Refer to FTTH/DSL/LTE troubleshooting

**Step 2: DHCP and DNS on Client**
- Refresh DHCP lease:
  - Windows: `ipconfig /renew`
  - macOS/Linux: `sudo dscacheutil -flushcache`
- Set public DNS:
  - Router panel: Set DNS to 1.1.1.1 and 1.0.0.1
  - Or: 8.8.8.8 and 8.8.4.4

**Step 3: Access Control Review**
- Check router for:
  - [ ] MAC filter not blocking device
  - [ ] Parental controls not blocking time/domain
  - [ ] Firewall not blocking client
  - [ ] Guest network isolation (if guest network in use)

**Verification:**
- After changes, refresh DHCP on client
- Open 3 websites (should load in <3 seconds)
- Ping 1.1.1.1 (should show <50 ms latency)

#### Problem: Frequent Connection Drops

**Root Cause Analysis:**
- Client loses connection and must reconnect
- May be Wi-Fi roaming issue, interference, or power save conflict

**Troubleshooting Steps:**

**Step 1: Channel and Width Adjustment**
```
ACTION: Reduce channel width
2.4 GHz: 20 MHz (mandatory for stability)
5 GHz:   40 MHz (if currently 80 MHz)

MONITOR: 30-60 minutes for stability improvement
```

**Step 2: Change Channel**
```
ACTION: Select least congested channel
2.4 GHz: Scan with Wi-Fi analyzer, choose 1/6/11
5 GHz:   Use UNII-1 (36-48) or UNII-3 (149-165)
         AVOID DFS channels (52-144) if possible

MONITOR: 24 hours for patterns
```

**Step 3: Disable Interference-Causing Features**
```
Disable (temporarily test 24-48 hours):
- QoS (if enabled with strict rules)
- IDS/Intrusion Detection System
- USB tethering
- UPnP (if not needed)
- DFS channels (if enabled)

Re-enable features one-by-one to identify culprit
```

**Step 4: Power Management Check**
- Disable Wi-Fi power save on clients:
  - Windows: Device Manager → Network → Advanced → Power Management
  - macOS: System Preferences → Network → Wi-Fi → Advanced → Power Saving
  - iOS/Android: Disable Wi-Fi sleep settings

**Step 5: Firmware Update**
- Check available firmware (excluding beta)
- Update during off-peak hours
- Monitor for improvement

**Verification:**
- Continuous stable connection for 2–4 hours without drops
- No reconnection events in router logs

#### Problem: Weak Wi‑Fi Coverage

**Symptoms:**
- Low signal in distant rooms
- Connection drops in certain locations

**Solutions (In Priority Order):**

1. **Router Placement (Simplest)**:
   - Move to higher location (above furniture)
   - Move to central location (center of home/office)
   - Avoid placing near walls, metals, or microwaves
   - Estimated improvement: 20–40% range increase

2. **Antenna Orientation**:
   - Position antennas perpendicular to each other (one vertical, one horizontal)
   - Improves signal in different directions
   - Estimated improvement: 10–15%

3. **Add Mesh/AP**:
   - Place satellite/access point in weak coverage area
   - Requires wired connection for best performance
   - Provides seamless roaming
   - Estimated improvement: 80–100% new coverage area

4. **Cable to Key Devices**:
   - Use Ethernet for stationary devices (TV, desktop)
   - Frees up Wi-Fi bandwidth for mobile devices
   - Improves overall network performance

5. **5 GHz vs 2.4 GHz**:
   - If weak 5 GHz signal: increase 2.4 GHz channel width to 40 MHz
   - Note: 2.4 GHz has better range but lower speeds

#### Problem: "5 GHz Disappearing"

**Symptoms:**
- 5 GHz network randomly disappears for minutes or hours

**Common Causes:**

1. **DFS Radar Detection** (Most Common)
   - Solution: Switch from DFS channels (52–144) to fixed channels (36–48 or 149–165)
   - When detected: Router switches channels (5–30 second downtime)

2. **Thermal Throttling**:
   - Router overheating due to poor ventilation
   - Check router temperature visually (should be warm, not hot)
   - Improve ventilation: remove from enclosed spaces

3. **Radio Power Save**:
   - 5 GHz disabled due to inactivity or power save settings
   - Solution: Disable power save feature for 5 GHz

4. **Firmware Bug**:
   - Known issue on specific models/versions
   - Solution: Check for firmware updates or known workarounds

**Troubleshooting Procedure:**

1. Access router logs → search for "5GHz" or "radio"
2. Note time when 5 GHz disappeared → check for DFS/radar entries
3. If DFS-related:
   - Change to UNII-1 (36–48) or UNII-3 (149–165)
   - Disable DFS channels if router allows
4. If thermal-related:
   - Improve ventilation
   - Reduce enclosure/cover
4. If power-save-related:
   - Disable 5 GHz power save in settings
5. Monitor for 24–48 hours

### 3. Complete Test Procedure After Changes

**Perform these tests after any Wi-Fi configuration change:**

#### Test 1: Client Connection Refresh
```
Windows:
  ipconfig /renew
  ipconfig /flushdns

macOS/Linux:
  sudo dscacheutil -flushcache
  sudo ifconfig en0 down && sudo ifconfig en0 up

Repeat: Disconnect from Wi‑Fi → Reconnect
```

#### Test 2: Local Network Performance
**Via SMB/Network Share:**
```
Copy large file (>100 MB) from device to networked storage
Expected: >50 Mbps for 802.11ac, >100 Mbps for 802.11ax
```

**Or via iperf (if available):**
```
iperf3 -c <router_ip> -t 30
Expected: close to WiFi standard max throughput
```

#### Test 3: Internet Connectivity
```
1. Open 3 different websites:
   ✓ http://example.com
   ✓ https://google.com
   ✓ https://github.com
   Expected: All load in <3 seconds

2. Run Speedtest (off-peak hours):
   Expected: Matches typical ISP speeds within 80–120%

3. Ping tests:
   ping 192.168.1.1 (gateway) → <5 ms, 0% loss
   ping 1.1.1.1        → <30 ms, <1% loss
```

#### Test 4: Stability Monitoring
```
Duration: 15–30 minutes continuous monitoring

Monitor:
  ✓ No Wi‑Fi reconnections
  ✓ No WAN interruptions
  ✓ Router logs show no errors
  ✓ Consistent ping times (no spikes)
  ✓ No temperature warnings
  ✓ CPU usage normal (<50%)
```

#### Test 5: Device-Specific Verification
```
Test on:
  • Smartphone (Wi-Fi 5/6 capable)
  • Older device (if applicable)
  • Both bands (2.4 GHz and 5 GHz if applicable)

Verify:
  ✓ Device connects automatically
  ✓ RSSI shows acceptable signal
  ✓ IP address assigned from router
  ✓ Internet connectivity works
  ✓ Speed matches expectation
```

---

## Advanced Edge Cases and Special Scenarios

### DFS Channels — Advantages and Risks

**Why DFS Exists:**
- Weather radar operates on 5 GHz bands
- Wi-Fi must yield to radar signals
- DFS allows dynamic frequency switching

**Impact on Users:**
- Automatic channel switch when radar detected (5–30 second downtime)
- Typical: Rare in residential areas, more common near airports
- Critical systems (VoIP, gaming) affected if DFS change occurs

**Recommendation:**
- **For critical services**: Avoid DFS channels (use UNII-1/3)
- **For general use**: Can use DFS if radar unlikely in area
- **For IoT**: Avoid DFS (many devices don't handle seamlessly)

### IoT Devices (Smart Lights, Locks, Cameras)

**Typical Requirements:**
- 2.4 GHz only (most older IoT devices)
- WPA2 encryption (WPA3 not yet widely supported)
- Some devices: 802.11b/g only (no 802.11n/ac)

**Configuration Strategy:**

**Option 1: Dedicated IoT SSID (Recommended)**
```
SSID: "Home_IoT"
Band: 2.4 GHz only
Encryption: WPA2 (or WPA2/WPA3 Mixed)
Channel Width: 20 MHz
Channel: 1, 6, or 11
Band Steering: Disable
```

**Option 2: Shared SSID**
- Create on 2.4 GHz with WPA2 encryption
- Set mixed mode: WPA2/WPA3
- Monitor for conflicts with modern devices

**Troubleshooting IoT Connection Issues:**
1. Verify 2.4 GHz is enabled
2. Check encryption type (try WPA2 if mixed fails)
3. Temporarily switch to 20 MHz channel width
4. Try channel 1, 6, or 11 sequentially
5. Ensure password has no special characters unsupported by IoT device

### Double NAT Scenarios

**What Is Double NAT?**
- Two routers both performing Network Address Translation
- Example: ISP CPE (router mode) + Customer's own router (router mode)

**Symptoms:**
- UPnP port mapping fails
- Inbound ports unreachable
- Gaming/P2P applications affected

**Solution A: Bridge Mode (Recommended)**
- Set ISP CPE to bridge mode (converts to pass-through)
- Customer's router handles all routing/NAT
- Benefits: Single NAT, full control, proper port forwarding

**Solution B: AP Mode**
- Set customer's router to AP mode
- Customer's router provides Wi-Fi only
- ISP CPE handles routing/NAT
- Benefits: Simpler, no configuration needed

**Verification:**
- Check DHCP pool: Should match ISP network (e.g., 192.168.1.x)
- No nested NATing in tracert/traceroute output
- Port forwarding test passes (portchecker.co)

### Password Security and Special Characters

**Supported Characters:**

| Type | Characters | Support |
|------|-----------|---------|
| **ASCII Letters** | a-z, A-Z | ✓ All devices |
| **Numbers** | 0-9 | ✓ All devices |
| **Basic Symbols** | @#$%^&*()_+-={}[] | ✓ Most devices |
| **Extended Symbols** | <>,.?/\|:; | ⚠️ Some devices may have issues |
| **Spaces** | ' ' | ⚠️ Leading/trailing problematic |
| **Emoji/Unicode** | 🔒🔑 | ✗ NOT supported on most devices |

**Recommendation:**
- Use ASCII only (a-z, A-Z, 0-9, @#$%^&*_+-)
- At least 12 characters
- Avoid spaces (leading/trailing)
- Test with all device types before deploying

---

## General Verification Checklist — Post-Configuration

### Before Handing to Customer

- [ ] All bands enabled and visible
- [ ] Correct encryption (WPA2 or WPA3)
- [ ] SSID clearly visible (not hidden)
- [ ] Password strong and tested on 2+ device types
- [ ] Channels set to least congested values
- [ ] Channel width appropriate for environment
- [ ] WMM enabled for better performance
- [ ] Guest network configured (if requested)
- [ ] IPv6 enabled (if ISP supports)
- [ ] Firmware updated to stable version
- [ ] 15–30 min stability test passed
- [ ] 3 websites accessible from Wi‑Fi client
- [ ] Internet speed meets expectations
- [ ] Customer understands basic Wi‑Fi features

---

## Glossary of Terms and Abbreviations

| Term | Definition |
|------|-----------|
| **SSID** | Service Set Identifier — Wi-Fi network name broadcast to devices |
| **WPA2/WPA3** | Wi-Fi Protected Access versions 2 and 3 — security standards |
| **WEP** | Wired Equivalent Privacy — obsolete, insecure encryption |
| **WPA-TKIP** | Temporal Key Integrity Protocol — obsolete, compromised |
| **DFS** | Dynamic Frequency Selection — automatic radar channel switching |
| **RSSI** | Received Signal Strength Indicator — measured in dBm (-100 to -30) |
| **SNR** | Signal-to-Noise Ratio — signal quality measurement in dB |
| **Band Steering** | Automatic steering of clients to stronger band (2.4 GHz or 5 GHz) |
| **Mesh** | Multi-node Wi-Fi network with seamless roaming |
| **Repeater** | Wireless extender repeating existing Wi-Fi network |
| **AP (Access Point)** | Wi-Fi device without routing capabilities |
| **UPnP** | Universal Plug and Play — automatic port/service configuration |
| **QoS** | Quality of Service — prioritization of traffic types |
| **WMM** | Wi-Fi Multimedia — device-level QoS feature |
| **MAC Address** | Media Access Control address — hardware identifier |
| **VLAN** | Virtual Local Area Network — isolated network segment |
| **IPv6** | Internet Protocol version 6 — next-generation IP standard |
| **SLAAC** | Stateless Address Autoconfiguration — automatic IPv6 addressing |
| **DHCPv6** | Dynamic Host Configuration Protocol for IPv6 |
| **Backhaul** | Connection between mesh units (wired or wireless) |

---

## References and Related Documentation

- **01_troubleshooting_internet.md** — Troubleshooting Internet (FTTH/DSL/LTE/5G)
- **03_apn_bridge.md** — APN Configuration & Bridge Mode Procedures
- **04_known_issues.md** — Known Issues & Workarounds

---

## Notes for TechnicalAgent (RAG Implementation)

- **Response Constraint**: Answer only based on cited sections in this document
- **Security Focus**: Do not recommend anything weaker than WPA2; WPA3 preferred
- **Retrieval Threshold**: If retriever returns fewer than 3 matching fragments, ask for clarification or indicate missing documentation
- **Audience Context**: L1 Support staff may have limited networking knowledge — provide step-by-step guidance with explanations
- **Configuration Variations**: Different router brands may have slightly different menu structures; use generic terminology where possible
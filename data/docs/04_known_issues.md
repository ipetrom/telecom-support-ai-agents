---
title: "Known Issues & Workarounds (FTTH/DSL/LTE/5G)"
version: "1.2"
last_updated: "2025-27-10"
source: "Internal KB"
owner: "Tech Support"
audience: "L1 Support"
summary: "Katalog znanych problemów, objawy, przyczyny, rozwiązania i workarounds dla FTTH, DSL, LTE, 5G, routerów, Wi-Fi i APN."
---

# Known Issues & Workarounds (FTTH/DSL/LTE/5G)

## Overview

This document catalogs known issues, bugs, and limitations encountered across various telecom technologies and devices. Each issue includes:

- **Symptoms**: What the customer reports
- **Affected Devices/Versions**: Which models/firmware versions
- **Root Cause**: Why it happens
- **Workaround**: How to fix it
- **Escalation Path**: When to escalate

---

## FTTH (Fiber-to-the-Home) Issues

### Issue 1: ONT Panel Access Lost After Bridge Mode

**Symptoms**:
- Cannot access ONT web panel (192.168.1.1) after enabling bridge
- "Connection refused" or timeout when trying to access panel

**Affected Devices**:
- Most ONT models: Huawei EchoLife HG6145F, TP-Link EC226, Zyxel PMG5627-T20

**Root Cause**:
- Bridge mode disables web server on LAN interface
- Panel access only available on management/service port (if available)

**Workarounds**:

1. **Temporary Re-enable Router Mode**:
   - Hold physical reset button 10–15 seconds
   - ONT returns to router mode (factory reset)
   - Access panel normally to reconfigure
   - Re-enable bridge if needed

2. **Service Port Access** (if available):
   - Some ONTs have dedicated Ethernet service port
   - Connect directly to service port
   - Access 192.168.0.1 (or specified address)
   - Reconfigure bridge or settings

3. **Operator Support Port**:
   - Contact operator → they may enable temporary access
   - Operator can reset remotely without losing bridge config

**Escalation**:
- If customer cannot access, escalate to 2nd-line with serial number
- Operator may need to enable temporary management access

**Prevention**:
- Document ONT factory reset procedure before enabling bridge
- Take screenshots of current configuration
- Provide customer with reset instructions

---

### Issue 2: Low Optical Signal (FTTH) — Intermittent Connection

**Symptoms**:
- PON LED flashing or flickering (>30 seconds)
- Frequent WAN disconnects (every 10-20 minutes)
- ONT reboots spontaneously
- Speeds vary wildly (working, then drops)

**Affected Devices**:
- All ONT models experiencing optical link issues
- Common in: newly installed fiber, aged cables, improper splitters

**Root Cause**:
- Optical signal strength too low (< −28 dBm threshold)
- Possible causes:
  - Dirty SC/APC connector (dust, debris)
  - Damaged fiber somewhere on line
  - Excessive splitters (if multipoint setup)
  - Aging optical cable
  - Poor connector seating

**Workarounds** (Temporary):

1. **Optical Cable Cleaning**:
   - Turn off ONT
   - Gently clean SC/APC plug with soft cloth (no liquids)
   - Verify plug seats firmly in socket (click sound expected)
   - Power on and monitor PON LED for 5-10 minutes

2. **Restart ONT**:
   - Unplug power for 30 seconds
   - Replug and wait for LED stabilization (2-3 minutes)
   - Verify PON LED solid (not flashing)
   - Check WAN connection stability for 1 hour

3. **Remove Inline Splitters**:
   - If optical splitter between OLT and ONT: temporarily remove
   - Test direct connection for 24 hours
   - If stable with direct connection: splitter issue confirmed

**Permanent Solutions** (Escalate):
- Field technician must:
  - Replace dirty connector with new SC/APC plug
  - Test optical levels (should be between −22 dBm and −28 dBm)
  - Inspect fiber for damage
  - Replace splitter if faulty
  - Install line filter if needed

**Escalation**:
- If optical level < −28 dBm: **ESCALATE IMMEDIATELY**
- Requires field technician with optical meter
- Do NOT keep customer on degraded service

---

### Issue 3: PPPoE Authentication Failure on FTTH

**Symptoms**:
- "PPPoE Authentication Failed" in ONT/Router logs
- WAN disconnects every 10-30 minutes
- Cannot manually reconnect (same error)
- Operator hotline says service is active

**Affected Devices**:
- FTTH setups using PPPoE authentication
- Typical: DSL-style PPPoE legacy deployments

**Root Cause**:
- Incorrect PPPoE credentials (username/password)
- Credentials not updated after service change
- Special characters in password not properly escaped
- ISP system database issue

**Workarounds**:

1. **Verify PPPoE Credentials**:
   - Ask customer for original ISP paperwork/email
   - Compare stored credentials against document
   - If mismatch: update with correct values
   - Test connection for 5 minutes

2. **Re-enter Credentials Carefully**:
   - Do NOT copy-paste (spaces may be invisible)
   - Type character-by-character on both WAN password fields
   - Watch for:
     - Leading/trailing spaces
     - Special characters (@, #, &, %, $)
     - Case sensitivity (usually lowercase)
   - Save and reconnect

3. **Remove Special Characters (Temporary)**:
   - If complex password failing: contact ISP for simpler password
   - ISP may generate new password without special characters
   - Update and test

4. **Check WAN MTU Size**:
   - Some PPPoE failures due to MTU mismatch
   - Router panel → Network → MTU
   - Try: 1492 (PPPoE standard) vs 1500 (default)
   - Save and reconnect
   - Monitor for 30 minutes

**If Still Failing**:
- Escalate to operator with:
  - Customer account number
  - PPPoE logs (username/start time/error message)
  - Operator verifies account status and credentials

**Escalation**:
- If credentials verified and still failing: **Escalate to ISP**
- May indicate ISP database corruption

---

## DSL Issues

### Issue 1: DSL Line Retrains Every Few Hours

**Symptoms**:
- Connection stable, then drops for 5-10 seconds
- DSL LED goes off briefly, then comes back online
- Logs show "DSL retrain" events at irregular intervals
- Speeds are significantly lower than maximum possible

**Affected Devices**:
- All DSL modems in poor line condition
- Common in: old lines, long distances from CO, bad filtering

**Root Cause**:
- Low SNR margin (< 6 dB) causing line instability
- Modem retrains to re-synchronize on each marginal signal fluctuation
- Temperature/humidity changes in line
- Interference from devices or old wiring

**Workarounds**:

1. **Reduce DSL Profile**:
   - Modem admin panel → Connection → DSL Profile
   - Change from: VDSL/ADSL2+ Auto → ADSL2+ or lower
   - This trades speed for stability
   - Monitor for 24 hours without retrains

2. **Disable DLC (Dynamic Line Control)**:
   - Modem admin panel → Advanced → Line Control
   - If enabled: Disable
   - This prevents modem from dynamically adjusting speed
   - May reduce retrains from speed adjustments

3. **Remove All Splitters**:
   - Disconnect phone splitter (temporary test)
   - Connect modem directly to wall jack
   - Monitor for 24 hours
   - If retrains stop: splitter issue confirmed
   - Use quality splitter or contact operator for dedicated line

4. **Replace RJ11 Cable**:
   - Try different RJ11 cable (cat.5e or higher)
   - Old/damaged cable may cause signal reflections
   - Test for 24 hours

5. **Power Cycle Modem**:
   - If retrains are infrequent: restart modem
   - Unplug for 30 seconds → replug
   - Wait for full synchronization (2-3 minutes)
   - Monitor logs for 7 days

**If Retrains Continue**:
- This indicates **line quality issue** → escalate to operator
- Operator may need to check line integrity or reduce profile server-side

**Escalation**:
- SNR < 6 dB: **Escalate immediately**
- Request line quality report from operator

---

### Issue 2: DSL Speeds Much Lower Than Advertised

**Symptoms**:
- Speedtest shows 10-20% of contract speed
- All traffic slow (not specific to one application)
- Speed consistent over time (not variable)

**Affected Devices**:
- All DSL modems experiencing line quality issues

**Root Cause**:
- High attenuation or SNR issues
- Operator DSL profile too conservative (intentional)
- Noise or interference on line
- Distance from central office

**Workarounds**:

1. **Check Modem Line Parameters**:
   ```
   Modem panel → Statistics or Line Info
   
   Look for:
   - SNR Margin: target > 6 dB
   - Attenuation: normal for line length
   - Speed: showing correctly in modem status
   ```

2. **If Speed Normal in Modem but Slow in Test**:
   - Issue may be router/Wi-Fi, not DSL line
   - Test via Ethernet directly from modem
   - If still slow: line issue confirmed
   - If faster: router or Wi-Fi issue (see Wi-Fi section)

3. **Request Operator Increase Profile**:
   - Contact operator with modem line parameters
   - Ask if operator can increase DSL profile server-side
   - Sometimes set too conservatively by default

4. **Check for Double/Triple Splitter Setup**:
   - If customer has phone + TV via splitters on line
   - Each splitter adds 3-4 dB attenuation
   - Remove unnecessary splitters if possible

**Permanent Solution**:
- If SNR < 6 dB and cannot improve: line quality issue
- Escalate to operator for line troubleshooting

---

## LTE/5G Issues

### Issue 1: No 5G Signal (LTE/5G CPE Stuck on LTE)

**Symptoms**:
- CPE only connects to LTE, never to 5G
- Status page shows "LTE" but never "5G" or "NR"
- Nearby customers have 5G but this one doesn't
- Speeds much lower than advertised 5G speeds

**Affected Devices**:
- LTE/5G CPEs with band locking or antenna issues
- Common models with 5G issues: Early 5G routers (2019-2020)

**Root Cause**:
- 5G band/frequency locked (intentional or accidental)
- 5G antenna disabled or failed
- 5G not available in area (check with operator)
- CPE not registered on 5G (requires specific APN)
- Firmware too old (5G support added in updates)

**Workarounds**:

1. **Check Band Lock Setting**:
   - CPE panel → Network → Mobile → Band/Frequency
   - If specific band locked (e.g., "LTE Band 20"): set to **Auto**
   - Save and restart CPE (2-3 minutes)
   - Monitor for 5G signal

2. **Force 5G Registration**:
   - CPE panel → Network → Mobile → Mode or Bearer
   - If option available: set to **5G (NR) Only** (temporary test)
   - Save and restart
   - If CPE connects: 5G is available
   - If no connection: 5G unavailable in area
   - Set back to **Auto** or **LTE/5G Auto**

3. **Firmware Update**:
   - CPE admin panel → Administration → Firmware Update
   - Check for available updates
   - Update to latest stable version
   - 5G support or improvements may be included
   - Restart after update

4. **Power Cycle and Wait**:
   - Unplug CPE for 30 seconds
   - Replug and wait 5-10 minutes for registration
   - 5G registration slower than LTE
   - Monitor signal for 30 minutes

5. **Check SIM Status**:
   - CPE panel → Mobile SIM info
   - Verify SIM is active and registered
   - Check for error messages
   - If locked: contact operator

**If Still No 5G**:
- 5G coverage may not exist in area
- Contact operator to confirm 5G availability
- Request **coverage map** for address
- If unavailable: no workaround (service limitation)

**Escalation**:
- If operator confirms 5G available and CPE can't find: **Escalate**
- May require CPE antenna inspection or replacement

---

### Issue 2: LTE/5G Speeds Vary Wildly (100 Mbps → 5 Mbps)

**Symptoms**:
- Speedtest shows huge variation (100-200 Mbps, then 10-30 Mbps)
- Not consistent day-to-day
- Other customers on same tower have stable speeds
- Usually worse during peak hours

**Affected Devices**:
- All LTE/5G CPEs in congested areas

**Root Cause**:
- **Sector congestion**: Too many users on same cell tower sector
- **Band congestion**: Particular LTE/5G band overloaded
- **Signal variation**: CPE moving between bands/cells for load balancing
- **Time-based load**: Peak hours (evening 7-11 PM) more congested

**Workarounds**:

1. **Test at Different Times**:
   - Run speedtest during off-peak (morning 2-6 AM)
   - Note speed for "best case" reference
   - If much better off-peak: **congestion confirmed**
   - Workaround: Schedule large downloads off-peak

2. **Lock to Specific Band** (Experimental):
   - CPE panel → Network → Mobile → Band Selection
   - Instead of Auto: try specific band lock (e.g., "5G N78")
   - Monitor speed for 24 hours
   - If more stable: that band has less congestion
   - If worse: revert to Auto

3. **Change LTE/5G Mode**:
   - CPE panel → Mode: try "4G (LTE) Only" for 24 hours
   - Note speed and stability
   - If better: 5G on this tower heavily congested
   - If worse or unstable: 5G preferred (stick with Auto)

4. **Position CPE for Best Signal**:
   - Move CPE closer to window
   - Try different room locations
   - Better signal may help router handle band switching better
   - Test for 24 hours

5. **Request Priority/QoS from Operator**:
   - Contact operator → explain speed variance
   - Ask if customer can request **priority/high-speed profile**
   - Some operators offer premium LTE/5G tier (paid service)

**If Variation Unacceptable**:
- Escalate to operator with speed logs/screenshots
- Request: sector capacity check, signal strength verification
- May require different tower or service type

---

### Issue 3: LTE/5G CPE — APN Shows "Connected" but No Data

**Symptoms**:
- CPE status shows "Connected" and IP assigned
- Wi-Fi clients see network but cannot load web pages
- Ping fails (no response)
- CPE panel shows LTE/5G signal

**Affected Devices**:
- All LTE/5G CPEs with APN configuration

**Root Cause**:
- APN configured but service not provisioned by operator
- Data service disabled on account
- Firewall on CPE blocking all traffic
- Routing table corrupted
- SIM profile mismatch

**Workarounds**:

1. **Verify APN Configuration**:
   - CPE panel → Network → Mobile → APN
   - Check against operator's documentation:
     - Correct APN string? (e.g., "internet" not "Internet")
     - Authentication type: PAP/CHAP Auto?
     - Username/Password empty (for standard plans)?
   - If incorrect: update and save
   - Restart CPE (2-3 minutes)
   - Test connectivity

2. **Check Firewall Status**:
   - CPE panel → Firewall or Security
   - Verify: **Firewall: Disabled** or **Enabled but Allow LAN Traffic**
   - If restrictive: temporarily disable for test
   - Restart CPE
   - Test connectivity
   - If works: re-enable firewall with proper rules

3. **Restart Mobile Service**:
   - CPE panel → Network → Mobile
   - Click **Disconnect** (if available)
   - Wait 10 seconds
   - Click **Connect**
   - Wait 2-3 minutes for re-registration
   - Check if data working

4. **Reset CPE (Factory Reset)**:
   - Hold CPE reset button 10-15 seconds
   - CPE reboots to factory settings
   - Reconfigure APN with correct values
   - Test connectivity

**If Still No Data**:
- Issue likely with operator account or SIM
- Contact operator:
  - Verify SIM is active
  - Confirm data service provisioned on account
  - Ask operator to restart account/service

**Escalation**:
- If workarounds fail: **Escalate to operator**
- Provide: SIM number, CPE IMEI, account details

---

## Wi-Fi Issues

### Issue 1: 5 GHz Band Disappears After Firmware Update

**Symptoms**:
- After firmware update: 5 GHz network no longer visible
- 2.4 GHz still works normally
- Restarting router doesn't help
- Router panel shows 5 GHz disabled (greyed out)

**Affected Devices**:
- TP-Link Archer C7/C6 (firmware v20210101 and later)
- Netgear AC1200 (firmware v2.1.x)
- Some ASUS routers (firmware version dependent)

**Root Cause**:
- Firmware update bug that disables 5 GHz radio
- 5 GHz hardware failure (rare, usually coincidental timing)
- Regional settings reset to region where 5 GHz not permitted

**Workarounds**:

1. **Manually Re-enable 5 GHz**:
   - Router panel → Wireless → 5 GHz Settings
   - If option present: check **Enable 5 GHz**
   - Save settings
   - Wait 30 seconds
   - Check if 5 GHz network appears

2. **Reset Radio Module**:
   - Router panel → System → Reboot or Reset
   - Click **Reboot** (full restart)
   - Wait 3-5 minutes for full boot
   - Check if 5 GHz appears

3. **Check Regional Settings**:
   - Router panel → Administration → Region/Country
   - If set to restricted region (e.g., some Middle East): 5 GHz disabled by regulation
   - Change to country where 5 GHz permitted
   - Save and restart

4. **Revert Firmware to Previous Version** (if available):
   - Download previous stable firmware version
   - Router panel → Administration → Firmware Update
   - Select **Restore Firmware** or **Load File**
   - Upload previous version
   - Wait for reflash and reboot (5-10 minutes)
   - **Note**: Some routers don't allow downgrading

5. **Factory Reset to Original Settings**:
   - Hold reset button 10-15 seconds
   - All settings lost, but 5 GHz may re-enable
   - Reconfigure from scratch
   - Typical: SSID, password, channels

**If 5 GHz Still Missing**:
- May indicate hardware failure (5 GHz radio failed)
- Escalate: requires replacement unit

---

### Issue 2: Frequent Wi-Fi Disconnections (Every 10-30 Minutes)

**Symptoms**:
- Devices randomly disconnect from Wi-Fi
- Must manually reconnect
- Happens on multiple devices simultaneously or one specific device
- Logs show no pattern initially

**Affected Devices**:
- All Wi-Fi routers, but specific patterns per brand

**Root Cause**:
- Channel interference or poor signal quality
- Router power save feature aggressive
- Client power save conflict with router
- Microwave/cordless phone on 2.4 GHz
- Neighboring APs on same channel
- WiFi feature like band steering causing disruption

**Workarounds**:

1. **Change Wi-Fi Channel**:
   - Router panel → Wireless → Channel
   - Use Wi-Fi analyzer app to find least congested channel
   - **2.4 GHz**: Try channels 1, 6, 11 (one at a time)
   - **5 GHz**: Try UNII-1 (36-48) instead of DFS channels
   - Save and monitor for 24 hours

2. **Reduce Channel Width**:
   - **2.4 GHz**: Set to **20 MHz** (narrower = more stable)
   - **5 GHz**: Try **40 MHz** instead of **80 MHz**
   - Save and monitor for 24 hours

3. **Disable Band Steering**:
   - Router panel → Wireless → Band Steering
   - Set to **Disabled** (temporary test)
   - Monitor for 24 hours
   - If disconnections stop: band steering causing issue
   - Note: Leaving disabled may cause performance issues; enable after identifying root cause

4. **Disable Power Save on Client Device**:
   - **Windows**: Device Manager → Network → Wi-Fi Adapter → Advanced → Power Saving Mode → Disabled
   - **macOS**: System Preferences → Network → Wi-Fi → Advanced → Power Save → Off
   - **iOS/Android**: Settings → Wi-Fi → Wi-Fi Sleep → Never
   - Reboot device and test

5. **Update Router Firmware**:
   - Check for available firmware updates
   - Update to latest stable version
   - Fixes may address Wi-Fi stability issues
   - Restart router after update

6. **Temporarily Disable QoS**:
   - Router panel → QoS or Traffic Management
   - Set to **Disabled** (temporary test)
   - Monitor for 24 hours
   - If disconnections stop: QoS rules causing issue
   - Re-enable after identifying issue

**If Still Disconnecting**:
- Issue may be specific device driver or app
- Try: updating device Wi-Fi driver, uninstalling problematic apps
- Escalate if pattern unclear

---

### Issue 3: Wi-Fi Speed Much Lower Than Router Specifications

**Symptoms**:
- Router specs show 802.11ac (up to 1300 Mbps) but only getting 30-50 Mbps
- 5 GHz especially slow
- Other devices on same Wi-Fi also slow
- Not a distance issue (tested close to router)

**Affected Devices**:
- All Wi-Fi routers

**Root Cause**:
- Client device uses older Wi-Fi standard (802.11n or older)
- Too many clients on same router (bandwidth shared)
- Heavy interference or poor signal quality
- Router has many background tasks (updating, scanning)
- WAN connection slower than Wi-Fi spec (WAN limited, not Wi-Fi)

**Workarounds**:

1. **Test with Single Client**:
   - Disconnect all other Wi-Fi devices
   - Test speed with one device only
   - If speed improves dramatically: too many clients, not Wi-Fi issue
   - Solution: upgrade router or spread devices across APs

2. **Check Client Device Standard**:
   - Router panel → Connected Clients
   - Note what standard each device is using
   - If mostly 802.11n or older: devices are bottleneck, not router
   - Some old devices capped at 150-300 Mbps max

3. **Test on 5 GHz with Modern Device**:
   - Use modern laptop or smartphone (Wi-Fi 5/6 capable)
   - Position within 5 meters of router
   - Run speedtest
   - If still slow: check for interference or router limitation

4. **Check for Wi-Fi Channel Interference**:
   - Use Wi-Fi analyzer app
   - If many neighboring networks on same channel: switch to empty channel
   - Monitor speed for 24 hours

5. **Disable Unnecessary Background Tasks**:
   - Router panel → various sections
   - Disable: USB scanning, IP camera streaming, file backups
   - Restart router
   - Test speed again

6. **Check WAN Speed as Baseline**:
   - Speedtest from router's LAN port (Ethernet)
   - Note download speed
   - That's your maximum Wi-Fi speed baseline (WAN limited)
   - Wi-Fi overhead + interference typically 10-20% slower than WAN

**Reality Check**:
- Most home Wi-Fi networks achieve 50-200 Mbps typical (not 1300 Mbps spec)
- Spec speed is theoretical maximum under ideal lab conditions
- Real-world: interference, walls, distance, client limitations reduce speed

---

## General Router Issues

### Issue 1: Router Constantly Rebooting (Every 5-10 Minutes)

**Symptoms**:
- Router loses power (LED sequence restarts)
- Wi-Fi drops, then reconnects automatically
- Happens repeatedly at intervals
- Sometimes triggered by specific action (accessing panel, downloading)

**Affected Devices**:
- All router models potentially affected

**Root Cause**:
- **Hardware failure** (most likely): power supply, capacitor, overheating
- **Firmware bug**: specific version causes watchdog resets
- **Overheating**: poor ventilation, blocked vents
- **Power surge/unstable input**: voltage fluctuations
- **Memory leak**: RAM exhaustion triggers crash/reboot cycle

**Workarounds**:

1. **Improve Ventilation**:
   - Remove router from enclosed cabinet or case
   - Ensure vents are clear of dust
   - Place on open shelf or use stand for air circulation
   - Monitor for 24 hours

2. **Disconnect Optional Devices**:
   - Disconnect USB drives, external storage, printers
   - Disable any optional services (USB tethering, NAS mode)
   - Restart router
   - Monitor for 24 hours
   - If stops rebooting: USB device causing issue

3. **Check Firmware Version**:
   - Router panel → Administration → About or System
   - Check firmware version against known issues
   - Visit manufacturer website: search for "known bugs" + version number
   - If known issue: **update to newer firmware**
   - If already on latest: try reverting to previous version (if available)

4. **Factory Reset**:
   - Hold reset button 10-15 seconds
   - Reconfigure router from scratch
   - Monitor for 24 hours
   - Resets may clear memory leaks or corrupted settings

5. **Power Adapter Inspection**:
   - Verify adapter specifications match router requirements
   - Check adapter output: should match router input (e.g., 12V 2A)
   - If wrong adapter: use correct one
   - Test for 24 hours

6. **Monitor Temperature**:
   - Router panel → Status or System info (if available)
   - Check CPU/system temperature
   - If >70°C: overheating issue
   - Improve ventilation, reduce ambient temperature

**If Reboots Continue**:
- Likely **hardware failure** (power supply, capacitor)
- **Escalate**: Requires replacement unit

---

### Issue 2: Router Panel Access — Forgot Password

**Symptoms**:
- Cannot log in to router admin panel
- "Incorrect password" error
- Cannot reset through Web UI (needs current password)

**Affected Devices**:
- All router models

**Root Cause**:
- Customer forgot password
- Password changed and not documented
- Factory reset performed, credentials reset to default but customer doesn't know

**Workarounds**:

1. **Try Default Credentials**:
   - Router sticker on bottom: often has default username/password
   - Common defaults:
     - admin/admin
     - admin/password
     - admin/12345
   - Check router model documentation

2. **Reset to Factory Defaults**:
   - Hold reset button 10-15 seconds while powered on
   - Router reboots with factory settings
   - Default credentials restored
   - **Warning**: All custom settings lost
   - **Required**: Reconfigure Wi-Fi SSID, password, channels, etc.

3. **Check for Backup Email/Account**:
   - Some cloud-managed routers (mesh systems)
   - Account-based reset via email
   - Go to router manufacturer's login portal
   - Use "Forgot Password" or account recovery

4. **WPS Reset**:
   - If router has WPS button:
   - Hold WPS button for 3-10 seconds
   - Router may reset or enter WPS mode
   - Check manual for specific behavior

**Escalation**:
- If customer cannot/will not factory reset
- Escalate to operator: may have remote reset capability
- Escalate to manufacturer: may offer proof-of-ownership password reset

---

## Known Device-Specific Issues

### TP-Link Archer C7 — 5 GHz Weak After Firmware v20210101

| Issue | Details |
|-------|---------|
| **Symptom** | 5 GHz signal shows as -70 dBm at 3 meters (weak) |
| **Affected Version** | Firmware v20210101 and later |
| **Root Cause** | TX power bug in firmware |
| **Workaround** | 1. Update to v20220201 or later (fix included) 2. Set 5 GHz TX power to High (if current version doesn't have fix) |
| **Escalation** | If older firmware: recommend update |

### Huawei HG659 — DSL Retrains Every 30 Minutes

| Issue | Details |
|-------|---------|
| **Symptom** | Connection drops for 5-10 seconds every 30 minutes |
| **Affected Hardware** | HG659 with DSL line SNR < 8 dB |
| **Root Cause** | Aggressive line retrain algorithm when SNR marginal |
| **Workaround** | 1. Set DSL profile to ADSL2+ (sacrifices speed for stability) 2. Disable DLC (Dynamic Line Control) 3. Contact operator for line quality check |
| **Escalation** | If SNR < 6 dB: operator intervention required |

### ZTE F609 — Bridge Mode Configuration Lost on Reboot

| Issue | Details |
|-------|---------|
| **Symptom** | Bridge mode enabled but reverts to router mode after power loss |
| **Affected Hardware** | ZTE F609 (early versions) |
| **Root Cause** | Bridge setting not persistent in flash memory |
| **Workaround** | 1. Enable bridge mode 2. Go to System → Save Configuration 3. Explicitly save before power off |
| **Escalation** | Firmware update available: escalate to operator for flash |

### Samsung 5G Router — Intermittent 5G Loss During Calls

| Issue | Details |
|-------|---------|
| **Symptom** | 5G drops to LTE during VoIP call, reconnects after call |
| **Affected Hardware** | Samsung 5G CPE (models 2020-2021) |
| **Root Cause** | Band selection algorithm prioritizes LTE during voice services |
| **Workaround** | 1. Manually lock 5G (disable LTE) if 5G available 2. Update firmware to latest version (improved band algorithm) |
| **Escalation** | If happens on latest firmware: request replacement unit |

---

## General Troubleshooting Flowchart

```
Issue Reported
    ↓
1. Is it FTTH, DSL, LTE, or Wi-Fi issue?
    ├─ FTTH → check optical signal, PPPoE auth, bridge panel access
    ├─ DSL → check retrains, line parameters, speed expectations
    ├─ LTE/5G → check 5G availability, APN, speeds
    └─ Wi-Fi → check channels, interference, disconnects
    ↓
2. Can issue be reproduced?
    ├─ Yes → proceed with specific troubleshooting
    └─ No → document and monitor
    ↓
3. Can issue be resolved with documented workaround?
    ├─ Yes → apply and verify
    └─ No → proceed to escalation
    ↓
4. Escalate to appropriate team:
    ├─ Operator required → provide device/line info
    ├─ Hardware failure suspected → replacement unit
    └─ 2nd-line support → detailed logs and troubleshooting steps
```

---

## Escalation Criteria

### Escalate to Operator Immediately When:

- [ ] Optical signal < −28 dBm (FTTH)
- [ ] DSL SNR margin < 6 dB
- [ ] LTE/5G showing no signal despite multiple restarts
- [ ] APN configured but no data despite all workarounds
- [ ] Customer reports service outage (multiple issues simultaneously)
- [ ] Port/line tests confirm physical line degradation

### Escalate to 2nd-Line Support When:

- [ ] All documented workarounds attempted without success
- [ ] Issue requires technical logs/analysis
- [ ] Device firmware suspected compromised
- [ ] Complex configuration (VLAN, bridge, failover) needed
- [ ] Multiple simultaneous issues

### Escalate to Replacement/Hardware Support When:

- [ ] Router constantly rebooting despite troubleshooting
- [ ] 5 GHz radio fails to initialize
- [ ] Physical damage visible (water, burn marks)
- [ ] Device manufactured >5 years ago (end of support)

---

## Glossary

| Term | Definition |
|------|-----------|
| **PON LED** | Passive Optical Network LED indicator on ONT (shows optical signal) |
| **SNR Margin** | Signal-to-Noise Ratio margin — DSL line stability measure |
| **Attenuation** | Signal loss in DSL line (dB) |
| **Retrain** | DSL line re-synchronization event (brief disconnect) |
| **Band Steering** | Wi-Fi router auto-moving clients between 2.4 GHz and 5 GHz |
| **DLC** | Dynamic Line Control — DSL adaptive speed adjustment |
| **Splitter** | Device splitting voice/data on phone line (DSL) |
| **WPS** | Wi-Fi Protected Setup — quick connection method |
| **MTU** | Maximum Transmission Unit — packet size (usually 1500) |
| **Sector Congestion** | Too many users on same LTE/5G tower sector |

---

## References and Related Documentation

- **01_troubleshooting_internet.md** — Troubleshooting Internet (FTTH/DSL/LTE/5G)
- **02_router_wifi.md** — Router Setup & Wi‑Fi Optimization
- **03_apn_bridge.md** — APN Configuration & Bridge Mode Procedures
---

## Notes for TechnicalAgent (RAG Implementation)

- **Issue Specificity**: When retrieving known issues, verify symptoms match exactly before applying workaround
- **Escalation Guidance**: Always check escalation criteria before recommending customer troubleshooting
- **Device Model Context**: Some workarounds are device-specific—always confirm model/firmware before implementation
- **Documentation Update**: New issues encountered should be documented in this file with: symptom, cause, workaround, escalation
- **Retrieval Threshold**: If fewer than 3 relevant issue fragments retrieved, ask customer for: device model, firmware version, exact symptoms
This document covers two areas: (1) APN configuration for cellular access (LTE/5G) on phones and CPE routers, and (2) enabling bridge/pass-through mode on ONT/CPE for FTTH or LTE/5G modems. At the end, you’ll find verification procedures and a list of edge cases.
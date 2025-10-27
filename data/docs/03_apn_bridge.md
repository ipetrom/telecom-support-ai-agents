---
title: "APN Configuration & Bridge Mode (LTE/5G & FTTH)"
version: "1.2"
last_updated: "2025-27-10"
source: "Internal KB"
owner: "Tech Support"
audience: "L1 Support"
summary: "Procedury konfiguracji APN na Androidzie/iOS/routerach LTE/5G i włączenie Bridge/Pass-Through na ONT/CPE. Zależności z CGNAT, IPv6, port forwarding."
---

# APN Configuration & Bridge Mode (LTE/5G & FTTH)

## Overview

This document covers two critical areas:

1. **APN Configuration**: How to configure Access Point Names (APN) for cellular access on Android, iOS, and LTE/5G routers
2. **Bridge/Pass-Through Mode**: How to enable bridge mode on ONT/CPE devices to avoid double NAT and enable port forwarding

You'll find step-by-step procedures, verification tests, and edge cases for each technology.

## When to Use This Document

- **No internet on LTE/5G device**: Despite network connection, device cannot access internet
- **Low speeds or service failures**: Wrong APN may block certain services
- **M2M/IoT not working**: Payment terminals, monitoring devices require specific APN
- **Port forwarding needed**: Customer wants to expose services (NAS, camera, game server)
- **Double NAT issues**: Customer's router behind ONT/CPE causing connectivity problems
- **Public IP required**: Customer needs direct internet access without CGNAT

## Prerequisites — Before You Start

- [ ] Device model and firmware version
- [ ] Credentials for CPE admin panel (if applicable)
- [ ] Technology type: LTE/5G or FTTH
- [ ] For bridge: confirm secondary router model and WAN capabilities
- [ ] Service contract details (operator, service type)

---

## APN (Access Point Name) — Fundamentals

### What Is APN?

APN (Access Point Name) is the gateway configuration that defines:
- Which operator network the device connects to
- Whether the device gets a public IP or private (CGNAT) address
- What services/features are enabled (data, SMS, MMS, VoIP)

**Analogy**: APN is like choosing different networks at a cellular operator—each APN can have different speeds, costs, and restrictions.

### APN Configuration Fields

| Field | Purpose | Typical Value | Notes |
|-------|---------|---------------|-------|
| **Name** | Profile name (user-visible) | "Internet", "PLAY Internet" | User-defined, for identification |
| **APN** | Operator's access point identifier | "internet", "play.internet" | Case-sensitive, varies by operator |
| **Username** | Authentication username | (empty) | Usually empty for consumer plans |
| **Password** | Authentication password | (empty) | Usually empty for consumer plans |
| **Authentication** | Authentication protocol | PAP/CHAP (Auto) | Auto-detect best method |
| **MCC/MNC** | Mobile Country/Network Code | Auto | Country and carrier codes |
| **APN Type** | Traffic type routed through APN | "default,supl" | default=internet, supl=SMS |
| **Bearer** | Forced mobile technology | LTE/NR/Auto | Auto recommended |
| **IP Type** | IP protocol version | IPv4/IPv6/IPv4v6 | IPv4v6 preferred if stable |

### APN Role in CGNAT vs Public IP

**Standard Consumer APN:**
- Uses **CGNAT** (Carrier-Grade NAT)
- Multiple customers share single public IP
- **Result**: No inbound port forwarding, no direct incoming connections
- **Suitable for**: General browsing, streaming, messaging

**Business/Public IPv4 APN:**
- Dedicated public IPv4 address
- **Result**: Full port forwarding capability, inbound connections work
- **Suitable for**: Remote access, game servers, NAS, port forwarding
- **Note**: Usually premium service, additional cost

**IPv6 APN:**
- Public IPv6 address (no CGNAT)
- **Result**: Inbound connections work natively
- **Suitable for**: Future-proof, direct connectivity
- **Caveat**: Requires IPv6-capable devices and firewall rules

---

## APN Configuration — Step-by-Step Procedures

### 1. Android Smartphones and Tablets

#### Stock Android (Most Devices)

**Path**: Settings → Mobile Network → Access Point Names (APN)

**Procedure:**

1. Open **Settings** app
2. Navigate to **Mobile Network** or **Cellular**
3. Select **Access Point Names** (or **APN**)
4. Tap **"+"** button to add new APN
5. Fill in the following fields:

   ```
   Name:              PLAY Internet (or "Internet")
   APN:               internet (check operator documentation)
   Proxy:             (leave empty)
   Port:              (leave empty)
   Username:          (leave empty)
   Password:          (leave empty)
   Server:            (leave empty)
   MMSC:              (leave empty if data-only)
   MMS Proxy:         (leave empty if data-only)
   MMS Port:          (leave empty if data-only)
   Authentication:    PAP/CHAP (Auto)
   APN type:          default,supl
   APN protocol:      IPv4/IPv6 (or IPv4v6)
   Bearer:            LTE/NR (or Auto)
   ```

6. Tap **Save** (menu button if needed)
7. Return to APN list, select new profile as **Active** (radio button)
8. Close Settings
9. **Restart device** or toggle **Airplane Mode** (off 5s → on 5s → off)

**Verification Checklist:**
- [ ] Signal bars show (not "X" or no signal)
- [ ] Status bar shows "LTE" or "5G"
- [ ] Web pages load in <3 seconds
- [ ] Speedtest runs successfully and shows reasonable speed
- [ ] Ping to 8.8.8.8: <60 ms, 0% loss

#### Custom/Manufacturer Skins (Samsung, OnePlus, etc.)

Menu path may differ slightly:
- **Samsung**: Settings → Connections → Mobile Networks → Access Point Names
- **OnePlus**: Settings → SIM & Network → Mobile Networks → Access Point Names

**Action**: Follow same field setup as stock Android

#### Dual SIM Considerations

- **Separate APNs per SIM**: Each SIM can have different APN profiles
- **Verify active SIM**: Check which SIM is marked as primary for data
- **eSIM special case**: eSIM may have APN locked by operator (cannot edit)

**Troubleshooting**:
- If SIM 1 not getting data: Switch to SIM 2, configure APN, test
- If unsure: Contact operator for confirmed APN values

### 2. iOS (iPhone and iPad)

**Note**: iOS does not allow manual APN editing for standard carrier profiles. APN is typically provisioned by operator or through carrier configuration.

#### Check Carrier Settings (First)

1. Open **Settings** → **General** → **About**
2. Look for "Carrier Settings" update notification
3. If available: tap **Update** (connects to carrier profile)
4. Restart device

#### Manual APN Configuration (eSIM/Premium Only)

**Path**: Settings → Cellular (or Mobile Data) → Cellular Plans → Data Options

**Procedure:**

1. Go to **Settings** → **Cellular**
2. Select **Cellular Plans** or **SIM** section
3. Tap **Data Options** or **Mobile Data**
4. Look for **Cellular Network** or **Data APN**
5. Fill in:

   ```
   APN:               internet
   Username:          (empty)
   Password:          (empty)
   ```

6. Return, changes auto-save
7. **Restart device** or toggle **Airplane Mode**

**Important Limitations**:
- Many iOS devices do NOT show APN fields (carrier profile locked)
- eSIM may be locked by operator
- If no APN field visible → APN is managed by carrier (cannot change)

**Verification Checklist:**
- [ ] Cellular bars show (not airplane mode icon)
- [ ] Status bar shows "LTE" or "5G"
- [ ] Web pages load in <3 seconds
- [ ] Speedtest app runs successfully
- [ ] Ping works (use Network Utility app or online tool)

#### Troubleshooting on iOS

**If no APN field visible**:
1. Restart device (power off → power on)
2. Check for carrier profile update in Settings → About
3. Contact operator (APN may be carrier-locked)

**If still no internet after APN change**:
1. Force restart: iPhone 12+ (press Vol Up → Vol Down → press power until slider appears)
2. Older iPhone: press Home + Top buttons for 10 seconds
3. Re-enter APN values
4. Wait 5-10 minutes for network registration

### 3. LTE/5G CPE (Router)

#### Panel Access

1. Open web browser (use Ethernet connection if possible)
2. Enter CPE panel address:
   - Most common: **192.168.8.1** or **192.168.0.1**
   - Check device sticker for correct address
3. Log in with admin credentials (default: admin/admin)
4. Navigate to section: **Network** → **Mobile** (or Cellular) → **APN Profiles**

#### APN Configuration Procedure

**Step 1: Create New Profile**

1. Click **"Add Profile"** or **"+"** button
2. Enter profile details:

   ```
   Profile Name:           Internet (or operator name)
   APN:                    internet (confirm with operator)
   Authentication Type:    PAP/CHAP (Auto-detect)
   IP Protocol Type:       IPv4v6 (preferred if stable)
   Bearer:                 LTE/NR (Auto recommended)
   
   Dial Number/Username:   (leave empty)
   Password:               (leave empty)
   PDN Type:               IPv4/IPv6/IPv4v6
   Roaming APN:            (usually same as normal)
   ```

3. Click **Save**

**Step 2: Set as Default**

1. Return to APN Profiles list
2. Select newly created profile
3. Click **"Set as Default"** or radio button
4. Click **Save** (if separate button)

**Step 3: Reconnect CPE**

1. Go to **Network** → **Mobile** → **Connection**
2. Click **Restart/Reconnect** (or wait for auto-reconnect)
3. Wait 3-5 minutes for registration and IP assignment
4. Monitor **Status** for:
   - Signal strength (RSRP/RSRQ/SINR values visible)
   - IP address assigned (not 0.0.0.0)
   - Connection state: **Connected**

**Verification Checklist:**
- [ ] CPE received IP address (check WAN/Status page)
- [ ] DNS servers present (usually 2 addresses)
- [ ] Wi-Fi or LAN clients can access internet
- [ ] Speedtest runs successfully
- [ ] Ping to 1.1.1.1: <60 ms, <1% loss

#### Edge Cases — CPE APN Configuration

**Band/Technology Lock Issues**:
- If CPE cannot register on network:
  - Check if 4G/5G band is locked in settings
  - Try "Force LTE" or "Force 5G" then back to Auto
  - Restart CPE completely

**Weak Signal After APN Change**:
- APN change should NOT affect signal
- If weak: likely coincidental, not APN-related
- Check signal before blaming APN

**Speed Degradation**:
- Verify new APN supports same speeds (check contract)
- Run multiple speedtests to ensure consistent result
- May indicate network congestion, not APN issue

---

## Bridge / Pass-Through Mode — Fundamentals

### What Is Bridge Mode?

**Bridge Mode** (also called "Pass-Through") is a network configuration where:

- **Router Functions Disabled**: Device does NOT perform NAT, routing, or DHCP
- **WAN IP Forwarded**: Public/WAN IP address passed directly to downstream router
- **Transparent Operation**: Device acts like a "dumb" network bridge (Layer 2)

**Visual Comparison**:

```
Standard (Router Mode):
Internet → ONT (Router) → Your Router → Devices
          (NAT happens here)

Bridge Mode:
Internet → ONT (Bridge) → Your Router → Devices
           (no NAT, passthrough only)
```

### When to Use Bridge Mode

**Use Bridge When:**
- [ ] Customer has advanced own router (mesh, gaming, commercial)
- [ ] Port forwarding/public IP needed
- [ ] Double NAT present (creating connectivity issues)
- [ ] Customer wants full network control (firewall, VPN, routing)
- [ ] TV/VoIP not needed (or handled separately)

**Do NOT Use Bridge When:**
- [ ] Only CPE Wi-Fi available (no own router)
- [ ] TV/VoIP services depend on ONT/CPE (requires VLAN)
- [ ] Customer cannot configure their own router
- [ ] Service contract includes managed CPE (operator requirement)

### Risks and Important Notes

**After Enabling Bridge:**
- **Wi-Fi disabled**: ONT/CPE Wi-Fi may stop functioning (check model)
- **DHCP disabled**: Devices won't auto-get IP (must be on own router)
- **Panel access complicated**: May require factory reset or service port
- **TV/VoIP affected**: May need additional VLAN configuration
- **Operator services**: Some carriers don't support bridge

**Always Document:**
1. Original configuration (take screenshot)
2. Factory reset procedure (in case needed)
3. Emergency access method (service port, reset button)

---

## Bridge Mode Configuration — Step-by-Step Procedures

### 1. FTTH — ONT to Own Router (PPPoE or DHCP)

#### Prerequisites Check

Before proceeding:
- [ ] Own router is available and working
- [ ] Know whether ISP uses PPPoE or DHCP (check contract)
- [ ] If PPPoE: have username/password from ISP
- [ ] Have Cat.5e+ Ethernet cable
- [ ] Documented current ONT settings (screenshot)

#### Procedure

**Step 1: Access ONT Panel**

1. Open browser → **192.168.1.1** (or **192.168.0.1**)
2. Log in with admin credentials
3. Navigate to **Network** → **WAN** or **Internet**

**Step 2: Change to Bridge Mode**

1. Find setting: **Operation Mode** or **Router Mode**
2. Change from **Router** to:
   - **Bridge** (most common)
   - **Pass-Through** (some models)
   - **Transparent Mode** (rare)
3. Click **Save**

**Step 3: VLAN Configuration (If Operator Requires)**

Some operators use Layer 2 VLAN tagging:

1. Check ISP documentation for VLAN ID (e.g., 35, 100, 10)
2. If VLAN required:
   - Find **VLAN Settings** section
   - Set WAN VLAN ID to operator's value
   - Save
3. If no VLAN: leave settings at defaults

**Step 4: Connection Setup**

1. Click **Save/Apply** to apply bridge mode
2. ONT will **reboot** (LED sequence shows restart)
3. Wait 2-3 minutes for stabilization

**Step 5: Physical Cable Connection**

1. Disconnect current cable from ONT LAN1
2. Connect **ONT LAN1 → Your Router WAN port** with Ethernet cable
3. Both devices should show link activity LED

**Step 6: Configure Your Router's WAN**

On your own router, set WAN connection type:

**If ISP uses PPPoE:**
```
WAN Type:          PPPoE
Username:          (ISP username)
Password:          (ISP password)
Auto-connect:      Enabled
Disconnect timeout: 0 or never
```

**If ISP uses DHCP:**
```
WAN Type:          DHCP
DHCP Hostname:     (leave empty or set to device name)
Renew IP:          (click if needed)
```

3. Save and wait for connection (30-60 seconds)
4. Your router should acquire public IP

**Verification Checklist:**
- [ ] Your router received public IP (not 192.168.x.x or 10.x.x.x)
- [ ] Router shows **"Connected"** in WAN status
- [ ] DNS servers assigned (typically 2)
- [ ] Devices on your Wi-Fi get internet
- [ ] Web pages load in <3 seconds
- [ ] Ping 1.1.1.1: <25 ms (typical for FTTH)

#### Edge Cases — FTTH Bridge

**ONT Panel Access Lost After Bridge**:
- Bridge disables web panel access from normal LAN
- Recovery:
  1. Connect directly to ONT via reserved Ethernet port (some models)
  2. Use factory reset (hold button 10-15s)
  3. Reconfigure and re-enable router mode

**TV/VoIP Not Working After Bridge**:
- Some operators require separate VLAN for TV/VoIP
- Solution:
  1. Document current TV/VoIP port (usually LAN2 or LAN3)
  2. Do NOT connect to your router WAN
  3. Connect TV box/VoIP gateway directly to that ONT port
  4. Enable VLAN if available in ONT settings

**Incorrect VLAN = No Connection**:
- If ISP uses VLAN and you didn't set it:
  - Your router won't get IP/connection
  - Solution: Re-enable router mode, check ISP documentation for VLAN
  - Set VLAN correctly, then re-enter bridge

### 2. LTE/5G CPE — IP Passthrough/Bridge to Own Router

#### Prerequisites Check

Before proceeding:
- [ ] Own router available and working
- [ ] LTE/5G CPE has bridge/passthrough feature (check manual)
- [ ] Understand CPE may still use CGNAT (port forwarding may not work)
- [ ] Have admin credentials for CPE panel

#### Procedure

**Step 1: Access CPE Panel**

1. Open browser → **192.168.8.1** or **192.168.0.1**
2. Log in with admin credentials
3. Navigate to **Network** → **Internet** or **WAN** Settings

**Step 2: Enable Bridge/IP Passthrough**

1. Find setting: **IP Passthrough** or **Bridge Mode**
2. Enable by clicking **checkbox** or **toggle**
3. If option available: select which LAN port receives WAN address
4. Some devices ask for **MAC Address** of your router (get from router label or Network Settings)

**Step 3: Disable NAT/DHCP**

- Some CPEs have separate option: **NAT** → set to **Disabled**
- Or: **DHCP Server** → set to **Disabled**
- Or: mode automatically disables when Bridge activated
- Check manual for your model

**Step 4: Save and Restart**

1. Click **Save/Apply**
2. CPE will **restart** (wait 1-2 minutes)
3. Observe LED sequence for completion

**Step 5: Connect Your Router**

1. Connect your router's WAN port to the **designated LAN port** on CPE
2. Your router's WAN port should light up (link LED)

**Step 6: Configure Your Router**

1. On your router: set WAN to **DHCP** (automatic)
2. Click **Renew IP** if needed
3. Wait 30-60 seconds for IP assignment

**Verification Checklist:**
- [ ] Your router received IP (check WAN status page)
- [ ] IP range matches CPE provider pool (might still be private due to CGNAT)
- [ ] Wi-Fi clients get internet access
- [ ] Web pages load in <3 seconds
- [ ] Ping 1.1.1.1: <60 ms acceptable for LTE/5G

#### Important: CGNAT Persistence on LTE/5G

**Critical Understanding**:
- Even in bridge/passthrough mode, **LTE/5G typically uses CGNAT**
- Your router will receive **private IP** (100.64.x.x to 100.127.x.x)
- **Port forwarding will NOT work** with CGNAT
- Bridge mode only removes double NAT, not CGNAT

**Solutions for Port Forwarding**:

1. **Purchase Public IPv4** from operator (premium service)
2. **Use IPv6** (if available, no CGNAT on IPv6)
3. **Use VPN tunnel** (WireGuard/OpenVPN to cloud server)
4. **Use P2P services** (if available for your service)

See [CGNAT Workarounds Section](#cgnat-workarounds) below.

#### Edge Cases — LTE/5G Bridge

**CPE Still Using NAT After Enabling Bridge**:
- Some vendors' "bridge" still uses NAT
- Check if CPE provides **public IP** (not 100.64.x.x)
- If private: contact operator for true IP passthrough

**No IP Received on Your Router**:
- Your router WAN remains 0.0.0.0
- Solutions:
  1. Restart your router
  2. Force DHCP renewal
  3. Check CPE logs for DHCP errors
  4. Verify CPE is in bridge mode (check status page)

**Speeds Dropped After Bridge**:
- Bridge itself should not cause speed drop
- Likely coincidental network issue
- Run speedtest from CPE directly to compare

### 3. AP Mode (Alternative to Bridge)

**When to Use AP Mode Instead of Bridge**:
- You want to avoid double NAT but don't need public IP on your router
- ISP CPE handles all routing
- Simpler configuration

**Procedure**:

1. Access CPE admin panel
2. Find: **Mode** or **Operation Mode**
3. Change to **Access Point (AP)** or **Wireless Bridge**
4. Disable: **NAT**, **DHCP** (depends on model)
5. Save and restart
6. Connect your router via Ethernet to CPE LAN
7. Your router obtains IP from CPE's DHCP (e.g., 192.168.1.x)
8. All routing/NAT done by ISP CPE

---

## IPv6 Configuration (Advanced)

### When to Enable IPv6

- [ ] ISP supports IPv6 (check service contract)
- [ ] Modern devices on network (most 2016+ devices support IPv6)
- [ ] Want future-proof configuration
- [ ] Considering IPv6 for incoming connections (no CGNAT)

### IPv6 Setup Steps

#### On CPE/ONT (Enable IPv6)

1. Access panel → **Network** → **WAN**
2. Find **IPv6** section
3. Set: **IPv6** → **Enabled** (or **Auto**)
4. Set: **IPv6 Mode** → **DHCPv6** or **SLAAC**
   - **SLAAC**: Simpler, auto-configuration
   - **DHCPv6**: More control, manual configuration option
5. Save and wait for IPv6 prefix assignment (typically /56 or /60)

#### On Your Router (Enable IPv6 Prefix Delegation)

1. Access your router panel → **Network** → **LAN**
2. Find **IPv6** section
3. Set: **IPv6** → **Enabled**
4. Set: **DHCPv6-PD** → **Enabled** (Prefix Delegation)
5. Wait for IPv6 prefix to be assigned (check WAN status)
6. LAN devices should receive IPv6 addresses (typically /64)

#### Firewall Rules (Important)

**By default**: IPv6 firewall is often permissive (allow inbound)

**If you want inbound restrictions**:
1. Router panel → **Firewall** → **IPv6**
2. Set: **Inbound Policy** → **Drop** (block by default)
3. Create **exceptions** for services you need
4. Example: Allow inbound port 22 (SSH) from specific IP

### IPv6 Verification

Run **IPv6 Connectivity Test** at:
- **ipv6-test.com** — comprehensive test
- **test-ipv6.com** — quick validation

Expected results:
- ✓ "IPv6 connectivity" → pass
- ✓ Devices show **IPv6 address** in range
- ✓ Ping to **2606:4700:4700::1111** (Cloudflare DNS) works

---

## CGNAT Workarounds (For LTE/5G Port Forwarding)

### Understanding CGNAT Limitation

If CPE provides **private IP** (100.64.x.x – 100.127.x.x) even in bridge mode:
- **Port forwarding impossible** through standard NAT rules
- Inbound connections cannot reach your service
- Solutions required for remote access

### Workaround Options

#### Option 1: Public IPv4 Subscription

**What**: Operator provides dedicated public IPv4

**Cost**: Typically €5–15/month

**Setup**:
1. Contact operator → request public IPv4
2. Receive activation confirmation
3. CPE automatically gets public IP (check WAN status)
4. Standard port forwarding now works

**Verification**:
- [ ] CPE WAN IP is **not** in 100.64.x.x range
- [ ] External port scan passes (portchecker.co)
- [ ] Inbound connection test succeeds

#### Option 2: IPv6 with Firewall Rules

**What**: Use native IPv6 (no CGNAT on IPv6)

**Requirements**:
- ISP must provide IPv6 (ask operator)
- Service/application must support IPv6
- Firewall rules properly configured

**Setup**:
1. Enable IPv6 on CPE and router (see section above)
2. Router firewall: create rules allowing inbound IPv6 traffic
3. Configure application to listen on IPv6 [::]:port
4. Test with IPv6-capable client

**Verification**:
- [ ] IPv6 address present on WAN (starts with 20XX or 26XX)
- [ ] External IPv6 connectivity test passes
- [ ] Inbound IPv6 connection works

**Pros**: No additional cost, future-proof

**Cons**: Not all devices/apps support IPv6 yet

#### Option 3: VPN Tunnel (Recommended for Reliability)

**What**: Create encrypted tunnel to cloud server with public IP

**Tools**: WireGuard (simple), OpenVPN (complex), ZeroTier (simple)

**High-Level Setup**:
1. Rent small VPS with public IP (e.g., €2–5/month)
2. Install VPN server (WireGuard/OpenVPN)
3. Install VPN client on CPE or your router
4. Route services through VPN tunnel
5. Clients access: **VPS_public_IP:port**

**Verification**:
- [ ] VPN tunnel established (check VPN status)
- [ ] External IP matches VPS (not CPE IP)
- [ ] Inbound connection reaches VPS (then tunnels to service)
- [ ] Performance acceptable for use case

**Pros**: Works with CGNAT, encrypted

**Cons**: Adds latency, requires VPS

#### Option 4: Manufacturer P2P Services

**What**: Use vendor's cloud platform (camera/NAS/game console)

**Examples**:
- Synology QuickConnect (NAS)
- Google Home app (Chromecast, devices)
- Sony/Nintendo cloud services

**Setup**:
1. Device/app registers with manufacturer's cloud
2. Access remotely through cloud platform
3. No port forwarding needed

**Verification**:
- [ ] Device/app shows "Connected" in cloud dashboard
- [ ] Remote access works from external network

**Pros**: Simplest for non-technical users, automatic

**Cons**: Limited privacy, cloud-dependent, restricted control

---

## Dual WAN / Failover Configuration (Optional)

### When to Use Dual WAN

- Customer has FTTH (primary) + LTE/5G (backup)
- Wants automatic failover if primary fails
- Important: Do NOT use load balancing for sensitive services (banking, VPN)

### Basic Dual WAN Setup

1. **Router Panel** → **Network** → **WAN** section
2. Add second WAN connection:
   - Primary: FTTH (static or DHCP)
   - Secondary: LTE/5G (USB tethering or separate CPE)
3. Set **Failover Mode**:
   - Monitor primary gateway with ping
   - If ping fails: switch to secondary
   - Typical switchover time: 30–60 seconds

4. Configure **Sticky Sessions** if sensitive services:
   - Ensure connections stick to primary
   - Prevent mid-session failover for banking apps

### Important Notes

- **Gaming**: May disconnect during failover (set long timeout)
- **Banking/VPN**: Use sticky session (prevent mid-transaction failover)
- **General Browsing**: Auto-failover acceptable

---

## Verification — Post-Configuration Tests

### For APN Configuration

**Test on Android/iOS:**

1. **Signal Verification**:
   - [ ] Cellular signal bars visible (not "X")
   - [ ] Status shows "LTE" or "5G"

2. **Internet Test**:
   - [ ] Open 3 websites (should load <3s)
   - [ ] Run Speedtest (verify reasonable speeds)

3. **Network Metrics**:
   - [ ] Ping 8.8.8.8: <60 ms, 0% loss
   - [ ] Ping 1.1.1.1: <60 ms, 0% loss

4. **Application Test**:
   - [ ] Messaging app sends/receives
   - [ ] Video streaming plays without buffering
   - [ ] M2M app connects (if applicable)

**Test on LTE/5G CPE:**

1. [ ] CPE panel shows **"Connected"** status
2. [ ] WAN IP assigned (not 0.0.0.0)
3. [ ] DNS servers present
4. [ ] Wi-Fi clients or LAN devices get internet
5. [ ] Speedtest from connected device passes

### For Bridge Mode Configuration

**FTTH Bridge Test:**

1. [ ] Your router received **public IP** (not 192.168.x.x)
2. [ ] WAN status shows **"Connected"**
3. [ ] DNS servers assigned
4. [ ] Wi-Fi clients access internet normally
5. [ ] Ping to gateway: <5 ms, 0% loss
6. [ ] No connectivity to ONT panel (expected in bridge)

**LTE/5G Bridge Test:**

1. [ ] Your router received IP (check WAN status)
2. [ ] Note IP range (may be private 100.64.x.x due to CGNAT)
3. [ ] Internet connectivity works from Wi-Fi/LAN
4. [ ] Speedtest runs successfully
5. [ ] If port forwarding needed: verify with external port scanner

### IPv6 Verification

- [ ] Run ipv6-test.com (should show "IPv6 connectivity")
- [ ] LAN devices have IPv6 addresses (check with `ipconfig` or network settings)
- [ ] Ping to **2606:4700:4700::1111**: should work

### Double NAT Verification

Check for double NAT:

**Command (Windows/macOS/Linux):**
```
tracert 1.1.1.1          (Windows)
traceroute 1.1.1.1       (macOS/Linux)
```

**Expected output**:
- First hop: Gateway (router)
- Second hop: ISP upstream
- **No routing loops** (same IP repeated)

**If double NAT present**:
- See multiple private IPs in path
- Solution: Re-enable bridge/AP mode

---

## Advanced Topics and Edge Cases

### Operator-Locked eSIM and APN

**Symptoms**:
- APN field not editable on device
- Cannot change from operator's default APN

**Reason**:
- Operator locks SIM/eSIM to prevent configuration
- Security measure or service control

**Solutions**:
1. Contact operator → request APN unlocking
2. Request operator provide correct APN profile
3. For business needs: explain use case to carrier

### VLAN Tagging (FTTH)

**When Required**:
- Operator uses Layer 2 VLAN for internet
- Common in Europe (VLAN 35, 100, 10)

**If VLAN Required but Not Set**:
- You'll have no internet in bridge mode
- Solution: Set correct VLAN ID in ONT bridge settings

**Verification**:
- [ ] ISP documentation lists VLAN ID
- [ ] ONT VLAN setting matches documentation
- [ ] WAN connection works after VLAN set

### TV and VoIP Services with Bridge

**Problem**:
- TV/VoIP stops working after enabling bridge

**Reason**:
- TV/VoIP typically use separate VLAN or port on ONT

**Solution**:
1. Keep TV/VoIP **directly connected** to ONT port (not through bridge)
2. Example:
   - ONT LAN1 → Your Router WAN (bridge internet)
   - ONT LAN2 → TV Box (for TV service)
   - ONT LAN3 → VoIP Gateway (for VoIP service)
3. No further configuration needed (operator handles it)

**Verification**:
- [ ] TV box connects to ONT directly
- [ ] TV channels load and play
- [ ] VoIP dialing works

### CPE Panel Access After Bridge

**Problem**:
- Cannot access CPE/ONT admin panel after bridge enabled

**Reason**:
- Bridge disables normal web interface access from LAN

**Recovery Options**:

1. **Service/Management Port** (if available):
   - Some routers have dedicated Ethernet port for management
   - Connect directly to this port, access 192.168.0.1

2. **Factory Reset** (last resort):
   - Hold reset button 10–15 seconds
   - All settings lost, must reconfigure
   - Router returns to router mode

3. **Backup Plan** (before enabling bridge):
   - Screenshot all current settings
   - Document factory reset procedure
   - Keep contact info for manufacturer support

---

## Glossary of Terms and Abbreviations

| Term | Definition |
|------|-----------|
| **APN** | Access Point Name — mobile network gateway configuration |
| **LTE** | Long-Term Evolution — 4G mobile technology |
| **5G/NR** | Fifth generation / New Radio — latest mobile technology |
| **CPE** | Customer Premises Equipment — device at customer location (modem, router) |
| **ONT** | Optical Network Terminal — FTTH device |
| **Bridge/Pass-Through** | Transparent mode passing WAN IP to downstream router |
| **CGNAT** | Carrier-Grade NAT — operator-level NAT limiting inbound connections |
| **PPPoE** | Point-to-Point Protocol over Ethernet — authentication method |
| **DHCP** | Dynamic Host Configuration Protocol — automatic IP assignment |
| **VLAN** | Virtual Local Area Network — isolated network segment (Layer 2) |
| **MCC/MNC** | Mobile Country/Network Code — carrier identifiers |
| **Passthrough** | See Bridge/Pass-Through |
| **IPv4v6** | Dual-stack — simultaneous IPv4 and IPv6 support |
| **IPv6-PD** | IPv6 Prefix Delegation — automatic prefix assignment |
| **DHCPv6-PD** | DHCPv6 with Prefix Delegation |
| **Failover** | Automatic switching between primary and backup connections |
| **Sticky Session** | Connection remains on primary link despite failover availability |

---

## References and Related Documentation

- **01_troubleshooting_internet.md** — Troubleshooting Internet (FTTH/DSL/LTE/5G)
- **02_router_wifi.md** — Router Setup & Wi‑Fi Optimization
- **04_known_issues.md** — Known Issues & Workarounds

---

## Notes for TechnicalAgent (RAG Implementation)

- **Information Accuracy**: If APN or bridge details are unclear in documentation, do NOT guess or infer—request specific information
- **Required Information**: Always request:
  1. Device model and firmware version
  2. Technology type (FTTH/LTE/5G)
  3. Specific need (port forwarding, public IP, bridge setup)
  4. ISP operator name and contract type
- **Retrieval Threshold**: Fewer than 3 matching fragments → ask for clarification
- **Security Note**: Bridge mode affects security posture—advise customer of firewall importance
- **CGNAT Reality**: Always explain that LTE/5G bridge often still has CGNAT (port forwarding won't work without workaround)
# ⚡ ROM Flasher & Android Device Manager made for everyone

*Runs on dreams and hopes, made with ❤️ by [auratech0](https://github.com/auratech0)*

---

A powerful, safe, and beginner-friendly GUI tool for flashing custom ROMs, debloating Android devices, reading device info, and controlling your device — all without touching a terminal.

Built with **Python + Tkinter**. No extra dependencies. Works on **Windows**, **Linux**, and **macOS**.
---

> [!NOTE]
> This project is **Open Source**, but if you want to **modify**, **enhance**, or release a **derivative version**, please contact me first for **approval** and ensure proper **credits** are maintained.

---

## 📸 Features at a Glance

| Tab | What it does |
|-----|-------------|
| ⚡ **Flash** | Flash recovery, boot, vendor, system, vbmeta images and ROM ZIPs via Fastboot or ADB Sideload. Includes wipe operations. |
| 🗑 **Debloat** | Remove bloatware with AUD-style presets (Simple) or a full live package list (Advanced). Safety-flagged like Canta. |
| 📱 **Device Info** | Read all `getprop` values and `fastboot getvar all` output in one click. |
| 🔄 **Reboot** | Reboot to System, Recovery, Bootloader, Fastboot (userspace), Sideload, or Power Off — both ADB and Fastboot. |

---

## 🚀 Getting Started

### Requirements

- **Python 3.8+** — [python.org](https://www.python.org/downloads/)
- **Android Platform Tools** (ADB + Fastboot) — [Download here](https://developer.android.com/tools/releases/platform-tools)
- Platform tools must be in your system `PATH`

### Install & Run

```bash
# Clone the repo
git clone https://github.com/auratech0/android-multitool-universal
cd android-multitool-universal

# No pip install needed — standard library only
python android-multitool-universal.py
```

### Adding Platform Tools to PATH

**Windows:**
1. Extract the platform-tools ZIP
2. Open System Properties → Environment Variables → PATH → New
3. Add the full path to the `platform-tools` folder

**Linux / macOS:**
```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$PATH:/path/to/platform-tools"
source ~/.bashrc
```

---

## ⚡ Flash Tab

### Supported Flash Modes

| Mode | Command | Partition | Data Erased? |
|------|---------|-----------|--------------|
| Flash Recovery | `fastboot flash recovery` | recovery | ❌ No |
| Flash Boot / Kernel | `fastboot flash boot` | boot | ❌ No |
| Flash Vendor Image | `fastboot flash vendor` | vendor | ❌ No |
| Flash System Image | `fastboot flash system` | system | ❌ No |
| Disable vbmeta & Flash | `fastboot --disable-verity --disable-verification flash vbmeta` | vbmeta | ❌ No (disables AVB) |
| Full ROM Package | `fastboot update` | multiple | ⚠️ ZIP-dependent |
| ADB Sideload | `adb sideload` | via Recovery | ⚠️ Manual in Recovery |

### How to Flash

1. Select a **Flash Mode** from the dropdown
2. Read the colour-coded **Warning** and **Info** banners — they are specific to each mode
3. Click **Browse…** and pick your `.img` or `.zip` file
4. Tick all **Pre-Flash Safety Checklist** items
5. Click **▶ START FLASH**
6. A **command preview dialog** shows the exact command before execution — confirm to proceed

### Safety Guarantees

- **No `-w` flag ever** — `fastboot update` runs without the data-wipe flag
- **No OEM `flash_all` scripts** — these always include `-w` and erase all data
- **Command preview** — exact shell command shown before anything runs
- **Slot detection** — current A/B slot is logged before flashing
- **Bootloader unlock check** — warns if unlock cannot be confirmed
- **Danger confirmation** — vbmeta and other destructive modes require double confirmation

### vbmeta / AVB Note

Flashing vbmeta with `--disable-verity --disable-verification` is required for root on most modern devices. After this:
- Your device shows an **orange/yellow warning** on every boot
- You **cannot re-lock the bootloader** without a full factory reset
- This is a permanent, intentional part of Android's security model

### Wipe Operations

Four wipe tools are available in the Flash tab (section 04):

| Operation | Command | Notes |
|-----------|---------|-------|
| Wipe App Data | `adb shell pm clear <pkg>` | Clears data for one specific app |
| Wipe Dalvik Cache | `adb shell rm -rf /data/dalvik-cache` | Requires root |
| Wipe Cache Partition | `fastboot erase cache` | Device must be in Fastboot |
| Wipe Userdata | `fastboot erase userdata` | ⚠️ Full data wipe — requires double confirmation |

---

## 🗑 Debloat Tab

### Safety Flags (Canta-style)

Every package in both Simple and Advanced mode is flagged:

| Flag | Meaning |
|------|---------|
| 🟢 Safe | Can be removed with no known side effects |
| ⭐ Recommended | Bloat, telemetry, or ads — recommended to remove |
| 🟡 Caution | May affect some functionality — test before removing |
| 🔴 Unsafe | Critical system component — **do not disable** |

### Simple Mode (AUD Presets)

Curated package lists by OEM, inspired by [Universal Android Debloater](https://github.com/0x192/universal-android-debloater):

- **Google Bloat** — Meet, YouTube, Play Movies, Books, News, Fit, Photos, Feedback…
- **Xiaomi / MIUI** — Analytics daemons, ad services (msa.global), MIUI apps
- **Samsung** — All Bixby components, Samsung Free, Galaxy Store, Kids Mode
- **OnePlus / OxygenOS** — Game Space, BBK Music, HeyTap apps
- **OPPO / Realme / ColorOS** — App markets, Safe Center, weather
- **Generic AOSP Bloat** — Browser, Email, Music, Gallery, Live Wallpaper Picker

Each row shows the package description, its safety flag, and the full package name.

All operations use `pm disable-user --user 0` — **fully reversible**. Nothing is deleted unless you explicitly use **Uninstall Selected**.

### Advanced Mode (All Packages)

Lists every installed package on the device. Features:

- **Live search** by package name
- **Filter tabs**: All / System / User / Disabled / Known (packages in the database)
- **5-column view**: Package, Type, State, Safety Flag, Description
- **Click a row** to see full description and safety notes in the info bar below
- **Multi-select** with Ctrl+Click and Shift+Click
- **Unsafe warning** — extra confirmation shown if you try to disable a 🔴 package

### PM Commands Used

| Action | Command |
|--------|---------|
| Disable | `adb shell pm disable-user --user 0 <package>` |
| Enable | `adb shell pm enable <package>` |
| Uninstall | `adb shell pm uninstall --user 0 <package>` |

---

## 📱 Device Info Tab

Reads key system properties via `adb shell getprop`:

| Property | `getprop` key |
|----------|--------------|
| Manufacturer | `ro.product.manufacturer` |
| Model | `ro.product.model` |
| Device Codename | `ro.product.device` |
| Android Version | `ro.build.version.release` |
| SDK Level | `ro.build.version.sdk` |
| Security Patch | `ro.build.version.security_patch` |
| Build ID | `ro.build.id` |
| Bootloader | `ro.bootloader` |
| CPU ABI | `ro.product.cpu.abi` |
| Serial | `ro.serialno` |

Also runs `fastboot getvar all` when the device is in Fastboot mode and displays the full output — useful for checking unlock status, anti-rollback level, slot info, and more.

---

## 🔄 Reboot Tab

### ADB Reboot  (device must be booted + USB Debugging active)

| Button | Command | Description |
|--------|---------|-------------|
| System / Android | `adb reboot` | Normal reboot |
| Recovery | `adb reboot recovery` | Boot into Recovery |
| Bootloader / Fastboot | `adb reboot bootloader` | Enter Fastboot mode |
| Fastboot (userspace) | `adb reboot fastboot` | Userspace Fastboot — Pixel / A/B devices |
| ADB Sideload | `adb reboot sideload` | Boot directly into sideload |
| Power Off | `adb shell reboot -p` | Graceful power off |

### Fastboot Reboot  (device must be in Fastboot mode)

| Button | Command | Description |
|--------|---------|-------------|
| System / Android | `fastboot reboot` | Exit Fastboot, boot Android |
| Bootloader | `fastboot reboot-bootloader` | Stay in Fastboot |
| Recovery | `fastboot reboot recovery` | Boot into Recovery |
| Temp Boot Image | `fastboot boot <img>` | Test a boot.img **without flashing** — no changes written |

---

## 🔧 OEM-Specific Notes

### Xiaomi / MIUI / HyperOS
> ⚠️ **Do NOT use** the `flash_all.bat` or `flash_all.sh` from Xiaomi's official packages — they pass `-w` and will wipe all your data.

Flash partitions individually using the Flash tab. For vbmeta-based root, use the dedicated vbmeta mode.

### Samsung
Samsung devices primarily use **Odin** or **Heimdall** for partition flashing — stock Fastboot is limited. ADB Sideload works for stock recovery ZIP installs.

### Google Pixel
Pixel devices support **userspace Fastboot** (`adb reboot fastboot`). Use `fastboot reboot-bootloader` for traditional Fastboot. Factory images should be flashed partition-by-partition, not via `flash-all.sh`.

### A/B Devices (most modern phones 2018+)
The tool logs the **current slot** (`_a` / `_b`) before every Fastboot flash. Partitions are written to the inactive slot and the slot is marked active automatically by Fastboot.

---

## ⚠️ General Safety Guidelines

1. **Unlock your bootloader first** — unlocking wipes userdata once (expected)
2. **Back up your data** before any flash or wipe operation
3. **Keep battery above 50%** — power failure mid-flash = brick
4. **Match images to your exact device** — wrong model/build = brick
5. **Never use OEM `flash_all` scripts** — they pass `-w` and erase everything
6. **vbmeta disabling is irreversible** without a full factory reset
7. **Never disable 🔴 Unsafe packages** in the debloater

---

## 🐛 Troubleshooting

### `adb` or `fastboot` not found
Install [Android Platform Tools](https://developer.android.com/tools/releases/platform-tools) and add the directory to your `PATH`. Restart the tool after updating PATH.

### Device not detected by ADB
- Enable **USB Debugging** (Settings → About Phone → tap Build Number 7× → Developer Options → USB Debugging)
- Use a data-capable USB cable (not charge-only)
- On Windows, install the [OEM USB driver](https://developer.android.com/studio/run/oem-usb)
- Run `adb devices` in a terminal and accept the authorisation prompt on your device

### Device not detected by Fastboot
- Reboot device into Fastboot: hold Power + Vol Down (varies by device)
- On Windows, install a universal ADB driver (e.g. Google USB Driver)
- Run `fastboot devices` to verify

### Flash fails with "FAILED (remote: 'Partition does not exist')"
The partition name is not present on this device. Some OEMs use different partition names or the partition is absent on certain models.

### Flash fails with "FAILED (remote: 'not allowed')"
The bootloader is locked. You must unlock the bootloader first (Settings → Developer Options → OEM Unlocking → then `fastboot flashing unlock`).

### Debloat: `pm disable-user` returns error
- Some carrier-branded packages are protected by SELinux policy
- Try re-enabling after a reboot if the device behaves unexpectedly
- System apps marked 🔴 Unsafe should never be disabled


## 🙏 Credits

- [Universal Android Debloater (UAD)](https://github.com/0x192/universal-android-debloater) — package list inspiration
- [Canta](https://github.com/samolego/Canta) — safety flag system inspiration
- [Android Open Source Project](https://source.android.com/) — ADB & Fastboot
- - Google themselves and everyone who gave me inspiration for making this tool

---

*Runs on dreams and hopes, made with ♥ by [auratech0](https://github.com/auratech0)*

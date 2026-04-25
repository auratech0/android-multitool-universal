```markdown
# Android Multitool Universal

A Python-based GUI tool for Android devices. Flash ROMs, debloat, manage backups, and run ADB/Fastboot commands without touching a terminal.

Works on Windows, Linux, and macOS. Uses only the standard library (plus Tkinter).

## Features

- **Flash**: Flash recovery, boot, vendor, vbmeta, or full ROM zips. Includes safety checklists and command preview.
- **Debloat**: Remove bloatware with safety flags (Safe, Recommended, Caution, Unsafe). Includes presets for Google, Xiaomi, Samsung, OnePlus, and AOSP.
- **Device Info**: Read `getprop` and `fastboot getvar` values in one click.
- **Reboot Controls**: Reboot to system, recovery, bootloader, sideload, or power off. Also supports temp booting an image.
- **ADB Tools**: Screenshots, file push/pull, APK install/uninstall, and a live Logcat viewer.
- **Shell**: Run any ADB or Fastboot command with proper argument handling.
- **Backup**: Backup apps, user data, and the internal storage.
- **Wireless ADB**: Connect to a device over WiFi after the initial USB setup.
- **Magisk Patching**: Patch boot images with Magisk and manage modules.
- **Build.prop Editor**: Edit build properties with a GUI.

## Requirements

- Python 3.8 or newer
- Android Platform Tools (ADB and Fastboot) installed and available in the system PATH

## Installation

1. Clone the repository:


git clone https://github.com/auratech0/android-multitool-universal
cd android-multitool-universal


2. Run the script:

python android_multitool.py



No extra dependencies are required. The tool uses only the Python standard library.

## How to Flash

1. Select a flash mode from the dropdown.
2. Read the warning and info banners for that mode.
3. Click Browse and select your .img or .zip file.
4. Tick all items in the Pre-Flash Safety Checklist.
5. Click START FLASH.
6. Review the command preview dialog and confirm.

## Safety Notes

- The tool never passes the `-w` (wipe) flag to Fastboot.
- It does not run OEM `flash_all` scripts, which usually wipe user data.
- A command preview is shown before any flash operation.
- Destructive actions require a second confirmation.

## Credits

Built by auratech0 (alexandertech99 on TikTok).

Thanks to the Universal Android Debloater and Canta projects for the debloat presets and safety flag system, and to the Android modding community on XDA.
```

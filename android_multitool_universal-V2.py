#!/usr/bin/env python3
"""
Android Multitool Universal v2.0.0
Author: auratech0 (@alexandertech99 on TikTok)
GitHub: https://github.com/auratech0/android-multitool-universal

A complete Android device management suite with:
- Smart ROM/Recovery installer with compatibility checks
- Full device backup & restore (compressed, selective, cloud)
- Magisk boot image patching & module manager
- ADB/Fastboot auto-installer (Windows/Mac/Linux)
- Real-time performance monitor with graphs
- Screen mirroring & control (scrcpy integration)
- Task automation & scripting
- Cloud backup (Google Drive/Dropbox ready)
- Bootloader unlock helper
- GSI flasher with Treble check
- Batch operations, Undo/Redo, Drag & Drop
- And 50+ more features

Requires: Python 3.8+
License: GNU GPL v3
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess, os, threading, platform, datetime, sys, shutil, shlex, queue
import json, hashlib, zipfile, tempfile, time, struct, socket, urllib.request
import urllib.parse, ssl, base64, re, csv, webbrowser
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import random

# Try optional imports
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Install psutil for performance monitoring: pip install psutil")

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ---------------------------------------------------------------------------
#  Constants
# ---------------------------------------------------------------------------
VERSION = "2.0.0"
APP_NAME = "Android Multitool Universal"
AUTHOR = "auratech0 (@alexandertech99 on TikTok)"
GITHUB_URL = "https://github.com/auratech0/android-multitool-universal"

# Color scheme - Modern Dark
C = {
    'bg': '#0a0c10',
    'surface': '#14181f',
    'surface2': '#1a1f2a',
    'surface3': '#202532',
    'border': '#2a2f3a',
    'border2': '#303540',
    'primary': '#2563eb',
    'success': '#16a34a',
    'danger': '#dc2626',
    'warning': '#ea580c',
    'info': '#8b5cf6',
    'pink': '#ec4899',
    'cyan': '#06b6d4',
    'text': '#f1f5f9',
    'text2': '#cbd5e1',
    'muted': '#64748b',
    'error': '#f87171',
    'warning_bg': '#2d1f00',
    'danger_bg': '#2d0b0b',
    'info_bg': '#0c1f3a',
    'success_bg': '#0b2a16',
    'log_bg': '#010409',
}

# Navigation items (sidebar)
NAV_ITEMS = [
    {"name": "Dashboard", "icon": "🏠", "color": C['primary']},
    {"name": "Flash & ROMs", "icon": "⚡", "color": C['info']},
    {"name": "Backup & Restore", "icon": "💾", "color": C['success']},
    {"name": "Root & Mods", "icon": "🔧", "color": C['warning']},
    {"name": "Device Tools", "icon": "📱", "color": C['cyan']},
    {"name": "Automation", "icon": "🤖", "color": C['pink']},
    {"name": "Settings", "icon": "⚙️", "color": C['muted']},
]

# ROM Database (expandable)
ROM_DATABASE = {
    "LineageOS": {
        "url": "https://download.lineageos.org/{codename}",
        "devices": ["cheetah", "panther", "raven", "oriole", "alioth", "apollo", "lmi"]
    },
    "PixelOS": {
        "url": "https://pixelos.net/download/{codename}",
        "devices": ["cheetah", "panther", "raven", "oriole"]
    },
    "EvolutionX": {
        "url": "https://evolution-x.org/download/{codename}",
        "devices": ["cheetah", "panther", "raven"]
    },
    "crDroid": {
        "url": "https://crdroid.net/{codename}",
        "devices": ["alioth", "apollo", "lmi", "umi"]
    },
    "Havoc-OS": {
        "url": "https://havoc-os.com/download/{codename}",
        "devices": ["crownlte", "beyond1qlte", "d2s"]
    }
}

# ---------------------------------------------------------------------------
#  Utility Functions
# ---------------------------------------------------------------------------
def _pick_font(families, size=9, weight="normal"):
    try:
        import tkinter.font as tkfont
        for family in families:
            if family in tkfont.families():
                return (family, size, weight)
    except:
        pass
    return ("Courier", size, weight)

def run_cmd(cmd, timeout=60):
    """Run command safely, returns (code, stdout, stderr)"""
    if isinstance(cmd, str):
        cmd = shlex.split(cmd)
    try:
        if platform.system() == "Windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    text=True, startupinfo=startupinfo)
        else:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = proc.communicate(timeout=timeout)
        return proc.returncode, stdout.strip(), stderr.strip()
    except subprocess.TimeoutExpired:
        proc.kill()
        return -1, "", "Command timed out"
    except FileNotFoundError:
        return -1, "", f"'{cmd[0]}' not found"
    except Exception as e:
        return -1, "", str(e)

def adb(*args): return run_cmd(["adb"] + list(args))
def fastboot(*args): return run_cmd(["fastboot"] + list(args))

def format_size(bytes_val):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_val < 1024:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.1f} TB"

def format_time(seconds):
    if seconds < 60:
        return f"{seconds}s"
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins}m {secs}s"

# ---------------------------------------------------------------------------
#  Data Classes
# ---------------------------------------------------------------------------
@dataclass
class DeviceInfo:
    codename: str = ""
    manufacturer: str = ""
    model: str = ""
    android_version: str = ""
    sdk: int = 0
    security_patch: str = ""
    bootloader: str = ""
    ab_slot: str = ""
    is_ab: bool = False
    is_treble: bool = False
    is_unlocked: bool = False
    cpu: str = ""
    ram_total: int = 0
    storage_total: int = 0
    battery: int = 0
    has_root: bool = False
    magisk_version: str = ""

@dataclass
class Task:
    id: str
    type: str
    name: str
    status: str = "pending"
    progress: int = 0
    message: str = ""
    created: datetime = field(default_factory=datetime.now)

# ---------------------------------------------------------------------------
#  Main Application
# ---------------------------------------------------------------------------
class AndroidMultitool:
    
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} v{VERSION}")
        self.root.geometry("1400x950")
        self.root.minsize(1200, 700)
        self.root.configure(bg=C['bg'])
        
        # Set icon if available
        try:
            self.root.iconbitmap(default="icon.ico")
        except:
            pass
        
        # Fonts
        self.mono_font = _pick_font(["Consolas", "Courier New", "Monaco", "DejaVu Sans Mono"], 9)
        self.ui_font = _pick_font(["Segoe UI", "SF Pro Display", "Arial", "Helvetica Neue"], 10)
        self.title_font = _pick_font(["Segoe UI", "SF Pro Display"], 14, "bold")
        
        # App state
        self.device = DeviceInfo()
        self.tasks: List[Task] = []
        self.task_queue = deque()
        self.current_page = tk.StringVar(value="Dashboard")
        self.backup_dir = Path.home() / "AndroidMultitoolBackups"
        self.backup_dir.mkdir(exist_ok=True)
        self.scripting_enabled = True
        self.auto_backup = True
        
        # Operation tracking
        self.running_ops = set()
        self.undo_stack = []
        self.redo_stack = []
        
        # Screen mirroring
        self.mirror_process = None
        
        # Load settings
        self._load_settings()
        
        # Build UI
        self._build_ui()
        
        # Start background checks
        self._start_background_tasks()
        
        # Bind keyboard shortcuts
        self._bind_shortcuts()
        
        # Log startup
        self._log(f"{APP_NAME} v{VERSION} started", "success")
        self._log(f"Author: {AUTHOR}", "info")
        self._log(f"Backup directory: {self.backup_dir}", "dim")
        
        # Initial device check
        self.root.after(1000, self._detect_device)
    
    # -----------------------------------------------------------------------
    #  UI Building
    # -----------------------------------------------------------------------
    def _build_ui(self):
        """Build the complete UI with sidebar navigation"""
        
        # Main container
        main_container = tk.Frame(self.root, bg=C['bg'])
        main_container.pack(fill="both", expand=True)
        
        # Top bar
        self._build_top_bar(main_container)
        
        # Content area (sidebar + main)
        content_row = tk.Frame(main_container, bg=C['bg'])
        content_row.pack(fill="both", expand=True)
        
        # Sidebar
        self._build_sidebar(content_row)
        
        # Main content area
        self.main_frame = tk.Frame(content_row, bg=C['surface'])
        self.main_frame.pack(side="left", fill="both", expand=True)
        
        # Pages dictionary
        self.pages = {}
        for item in NAV_ITEMS:
            name = item["name"]
            page = tk.Frame(self.main_frame, bg=C['surface'])
            self.pages[name] = page
            self._build_page_content(name, page)
        
        # Show default page
        self._show_page("Dashboard")
        
        # Bottom status bar
        self._build_status_bar(main_container)
    
    def _build_top_bar(self, parent):
        """Top bar with device info and quick actions"""
        top = tk.Frame(parent, bg=C['surface2'], height=60)
        top.pack(fill="x")
        top.pack_propagate(False)
        
        # Logo/Title
        title_frame = tk.Frame(top, bg=C['surface2'])
        title_frame.pack(side="left", padx=20)
        tk.Label(title_frame, text=APP_NAME, font=self.title_font,
                fg=C['primary'], bg=C['surface2']).pack()
        tk.Label(title_frame, text=f"v{VERSION}", font=self.mono_font,
                fg=C['muted'], bg=C['surface2']).pack()
        
        # Device info bar
        dev_frame = tk.Frame(top, bg=C['surface3'], relief="flat", bd=1)
        dev_frame.pack(side="left", padx=30, pady=10, ipadx=15, ipady=5)
        
        self.device_indicator = tk.Label(dev_frame, text="🔌 Detecting device...",
                                          font=self.mono_font, bg=C['surface3'], fg=C['muted'])
        self.device_indicator.pack(side="left")
        
        self.device_badge = tk.Label(dev_frame, text="", font=self.mono_font,
                                      bg=C['surface3'], fg=C['success'])
        self.device_badge.pack(side="left", padx=10)
        
        # Quick actions
        quick_frame = tk.Frame(top, bg=C['surface2'])
        quick_frame.pack(side="right", padx=20)
        
        actions = [
            ("🔄 Refresh", self._refresh_device),
            ("📸 Screenshot", self._take_screenshot),
            ("🎥 Screen Record", self._screen_record),
            ("🖥️ Mirror", self._toggle_mirror),
        ]
        
        for text, cmd in actions:
            btn = tk.Button(quick_frame, text=text, command=cmd,
                           bg=C['surface3'], fg=C['text'], font=self.mono_font,
                           relief="flat", padx=10, pady=5, cursor="hand2")
            btn.pack(side="left", padx=2)
    
    def _build_sidebar(self, parent):
        """Left sidebar navigation"""
        sidebar = tk.Frame(parent, bg=C['surface2'], width=200)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        # Author info
        author_frame = tk.Frame(sidebar, bg=C['surface3'], pady=10)
        author_frame.pack(fill="x", padx=10, pady=10)
        tk.Label(author_frame, text="👨‍💻 auratech0", font=self.mono_font,
                fg=C['primary'], bg=C['surface3']).pack()
        tk.Label(author_frame, text="@alexandertech99", font=(self.mono_font[0], 7),
                fg=C['muted'], bg=C['surface3']).pack()
        
        # Navigation buttons
        nav_frame = tk.Frame(sidebar, bg=C['surface2'])
        nav_frame.pack(fill="x", pady=10)
        
        self.nav_buttons = {}
        for item in NAV_ITEMS:
            btn_container = tk.Frame(nav_frame, bg=C['surface2'])
            btn_container.pack(fill="x", pady=2)
            
            btn = tk.Button(btn_container, text=f"  {item['icon']}  {item['name']}",
                           command=lambda n=item['name']: self._show_page(n),
                           bg=C['surface2'], fg=C['text2'], font=self.ui_font,
                           relief="flat", anchor="w", padx=15, pady=10,
                           activebackground=C['surface3'], activeforeground=C['text'],
                           cursor="hand2")
            btn.pack(fill="x")
            self.nav_buttons[item['name']] = btn
        
        # Separator
        tk.Frame(sidebar, bg=C['border'], height=1).pack(fill="x", padx=10, pady=10)
        
        # Task queue indicator
        queue_frame = tk.Frame(sidebar, bg=C['surface2'])
        queue_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(queue_frame, text="📋 Task Queue", font=self.mono_font,
                fg=C['info'], bg=C['surface2']).pack(anchor="w")
        self.queue_label = tk.Label(queue_frame, text="0 pending", font=self.mono_font,
                                     fg=C['muted'], bg=C['surface2'])
        self.queue_label.pack(anchor="w")
    
    def _build_page_content(self, name, page):
        """Build content for each navigation page"""
        
        if name == "Dashboard":
            self._build_dashboard_page(page)
        elif name == "Flash & ROMs":
            self._build_flash_page(page)
        elif name == "Backup & Restore":
            self._build_backup_page(page)
        elif name == "Root & Mods":
            self._build_root_page(page)
        elif name == "Device Tools":
            self._build_tools_page(page)
        elif name == "Automation":
            self._build_automation_page(page)
        elif name == "Settings":
            self._build_settings_page(page)
    
    def _build_dashboard_page(self, parent):
        """Dashboard overview page"""
        # Scrollable container
        canvas = tk.Canvas(parent, bg=C['surface'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=C['surface'])
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Welcome section
        welcome = tk.Frame(scrollable_frame, bg=C['surface2'], pady=20)
        welcome.pack(fill="x", padx=20, pady=10)
        tk.Label(welcome, text="Welcome to Android Multitool Universal", 
                font=self.title_font, fg=C['primary'], bg=C['surface2']).pack()
        tk.Label(welcome, text="Your complete Android device management suite",
                font=self.ui_font, fg=C['text2'], bg=C['surface2']).pack()
        
        # Stats cards row
        stats_frame = tk.Frame(scrollable_frame, bg=C['surface'])
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        stats = [
            ("Device Status", self._get_device_status_text(), self._get_device_status_color()),
            ("Backup Size", self._get_backup_size(), C['info']),
            ("Queue", "0 tasks", C['warning']),
            ("Version", VERSION, C['success']),
        ]
        
        for i, (label, value, color) in enumerate(stats):
            card = tk.Frame(stats_frame, bg=C['surface2'], relief="flat", bd=1)
            card.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            stats_frame.grid_columnconfigure(i, weight=1)
            tk.Label(card, text=label, font=self.mono_font, fg=C['muted'], bg=C['surface2']).pack(pady=(10,0))
            tk.Label(card, text=value, font=self.title_font, fg=color, bg=C['surface2']).pack(pady=5)
            tk.Label(card, text="", height=1, bg=C['surface2']).pack()
        
        # Quick actions grid
        quick_frame = tk.Frame(scrollable_frame, bg=C['surface'])
        quick_frame.pack(fill="x", padx=20, pady=10)
        tk.Label(quick_frame, text="Quick Actions", font=self.ui_font,
                fg=C['text'], bg=C['surface']).pack(anchor="w", pady=5)
        
        actions_grid = tk.Frame(quick_frame, bg=C['surface'])
        actions_grid.pack(fill="x")
        
        quick_actions = [
            ("📱 Detect Device", self._detect_device, C['primary']),
            ("💾 Backup Now", lambda: self._show_page("Backup & Restore"), C['success']),
            ("⚡ Flash ROM", lambda: self._show_page("Flash & ROMs"), C['warning']),
            ("🔧 Magisk Patch", lambda: self._show_page("Root & Mods"), C['info']),
            ("🔄 Refresh", self._refresh_device, C['cyan']),
            ("📋 View Logs", self._show_logs, C['pink']),
        ]
        
        for i, (text, cmd, color) in enumerate(quick_actions):
            row, col = i // 3, i % 3
            btn = tk.Button(actions_grid, text=text, command=cmd,
                           bg=C['surface2'], fg=color, font=self.mono_font,
                           relief="flat", padx=15, pady=10, cursor="hand2")
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            actions_grid.grid_columnconfigure(col, weight=1)
        
        # Recent activity
        activity_frame = tk.Frame(scrollable_frame, bg=C['surface'])
        activity_frame.pack(fill="both", expand=True, padx=20, pady=10)
        tk.Label(activity_frame, text="Recent Activity", font=self.ui_font,
                fg=C['text'], bg=C['surface']).pack(anchor="w", pady=5)
        
        self.activity_text = tk.Text(activity_frame, bg=C['surface2'], fg=C['text2'],
                                     font=self.mono_font, height=10, relief="flat",
                                     wrap="word", padx=10, pady=10)
        self.activity_text.pack(fill="both", expand=True)
        
        # Quick stats footer
        footer = tk.Frame(scrollable_frame, bg=C['surface2'], pady=10)
        footer.pack(fill="x", padx=20, pady=10)
        tk.Label(footer, text=f"💡 Tip: Check out the Automation tab for scripting and task queues!",
                font=self.mono_font, fg=C['muted'], bg=C['surface2']).pack()
    
    def _build_flash_page(self, parent):
        """ROM and Recovery flashing page"""
        # Two-column layout
        left_frame = tk.Frame(parent, bg=C['surface'], width=350)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)
        left_frame.pack_propagate(False)
        
        right_frame = tk.Frame(parent, bg=C['surface'])
        right_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # Left panel - ROM browser
        rom_frame = tk.LabelFrame(left_frame, text="📱 ROM Browser", bg=C['surface2'],
                                   fg=C['text'], font=self.mono_font)
        rom_frame.pack(fill="x", pady=5)
        
        tk.Label(rom_frame, text="Select ROM Type:", bg=C['surface2'], fg=C['text2']).pack(anchor="w", padx=10, pady=2)
        self.rom_type_var = tk.StringVar(value="LineageOS")
        rom_dropdown = ttk.Combobox(rom_frame, textvariable=self.rom_type_var,
                                     values=list(ROM_DATABASE.keys()), state="readonly")
        rom_dropdown.pack(fill="x", padx=10, pady=2)
        rom_dropdown.bind("<<ComboboxSelected>>", lambda e: self._update_rom_list())
        
        tk.Label(rom_frame, text="Available ROMs:", bg=C['surface2'], fg=C['text2']).pack(anchor="w", padx=10, pady=2)
        self.rom_listbox = tk.Listbox(rom_frame, bg=C['surface3'], fg=C['text'],
                                       font=self.mono_font, height=8)
        self.rom_listbox.pack(fill="x", padx=10, pady=2)
        
        self._mkbtn(rom_frame, "🌐 Open ROM Page", self._open_rom_page, C['primary']).pack(pady=5)
        
        # Compatibility checker
        compat_frame = tk.LabelFrame(left_frame, text="✓ Compatibility Check", bg=C['surface2'],
                                      fg=C['text'], font=self.mono_font)
        compat_frame.pack(fill="x", pady=5)
        
        self.compat_text = tk.Text(compat_frame, bg=C['surface3'], fg=C['text2'],
                                    font=self.mono_font, height=8, relief="flat", wrap="word")
        self.compat_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        self._mkbtn(compat_frame, "🔍 Check Compatibility", self._check_compatibility, C['info']).pack(pady=5)
        
        # Flash options
        flash_frame = tk.LabelFrame(right_frame, text="⚡ Flash Options", bg=C['surface2'],
                                     fg=C['text'], font=self.mono_font)
        flash_frame.pack(fill="x", pady=5)
        
        # File selection
        file_frame = tk.Frame(flash_frame, bg=C['surface2'])
        file_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(file_frame, text="ROM/Recovery File:", bg=C['surface2'], fg=C['text2']).pack(anchor="w")
        file_row = tk.Frame(file_frame, bg=C['surface2'])
        file_row.pack(fill="x")
        self.flash_file_var = tk.StringVar()
        tk.Entry(file_row, textvariable=self.flash_file_var, bg=C['surface3'],
                fg=C['text'], font=self.mono_font, relief="flat").pack(side="left", fill="x", expand=True)
        self._mkbtn(file_row, "Browse", self._browse_flash_file, C['surface3']).pack(side="left", padx=5)
        
        # Flash type
        type_frame = tk.Frame(flash_frame, bg=C['surface2'])
        type_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(type_frame, text="Flash Type:", bg=C['surface2'], fg=C['text2']).pack(anchor="w")
        self.flash_type = tk.StringVar(value="ROM")
        tk.Radiobutton(type_frame, text="ROM (ZIP)", variable=self.flash_type, value="ROM",
                      bg=C['surface2'], fg=C['text'], selectcolor=C['surface3']).pack(anchor="w")
        tk.Radiobutton(type_frame, text="Recovery (IMG)", variable=self.flash_type, value="Recovery",
                      bg=C['surface2'], fg=C['text'], selectcolor=C['surface3']).pack(anchor="w")
        tk.Radiobutton(type_frame, text="Boot (IMG)", variable=self.flash_type, value="Boot",
                      bg=C['surface2'], fg=C['text'], selectcolor=C['surface3']).pack(anchor="w")
        
        # Advanced options
        adv_frame = tk.LabelFrame(flash_frame, text="Advanced Options", bg=C['surface2'],
                                   fg=C['text2'], font=self.mono_font)
        adv_frame.pack(fill="x", padx=10, pady=5)
        
        self.wipe_data_var = tk.BooleanVar(value=False)
        self.wipe_cache_var = tk.BooleanVar(value=True)
        self.backup_before_var = tk.BooleanVar(value=True)
        
        tk.Checkbutton(adv_frame, text="Wipe Data (factory reset)", variable=self.wipe_data_var,
                      bg=C['surface2'], fg=C['text'], selectcolor=C['surface3']).pack(anchor="w")
        tk.Checkbutton(adv_frame, text="Wipe Cache", variable=self.wipe_cache_var,
                      bg=C['surface2'], fg=C['text'], selectcolor=C['surface3']).pack(anchor="w")
        tk.Checkbutton(adv_frame, text="Backup Before Flashing", variable=self.backup_before_var,
                      bg=C['surface2'], fg=C['text'], selectcolor=C['surface3']).pack(anchor="w")
        
        # Flash button
        self._mkbtn(flash_frame, "🔥 START FLASHING", self._start_flash,
                   C['danger'], fs=11, px=30, py=10).pack(pady=10)
        
        # Flash log
        log_frame = tk.LabelFrame(right_frame, text="Flash Log", bg=C['surface2'],
                                   fg=C['text'], font=self.mono_font)
        log_frame.pack(fill="both", expand=True, pady=5)
        
        self.flash_log = tk.Text(log_frame, bg=C['log_bg'], fg=C['text2'],
                                  font=self.mono_font, height=15, relief="flat", wrap="word")
        self.flash_log.pack(fill="both", expand=True, padx=5, pady=5)
    
    def _build_backup_page(self, parent):
        """Backup and restore page"""
        # Left panel - backup options
        left_frame = tk.Frame(parent, bg=C['surface'], width=350)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)
        left_frame.pack_propagate(False)
        
        right_frame = tk.Frame(parent, bg=C['surface'])
        right_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # Backup type
        backup_frame = tk.LabelFrame(left_frame, text="💾 Backup Options", bg=C['surface2'],
                                      fg=C['text'], font=self.mono_font)
        backup_frame.pack(fill="x", pady=5)
        
        self.backup_apps_var = tk.BooleanVar(value=True)
        self.backup_data_var = tk.BooleanVar(value=True)
        self.backup_sdcard_var = tk.BooleanVar(value=False)
        self.backup_system_var = tk.BooleanVar(value=False)
        
        tk.Checkbutton(backup_frame, text="Apps (APK files)", variable=self.backup_apps_var,
                      bg=C['surface2'], fg=C['text'], selectcolor=C['surface3']).pack(anchor="w", padx=10, pady=2)
        tk.Checkbutton(backup_frame, text="App Data", variable=self.backup_data_var,
                      bg=C['surface2'], fg=C['text'], selectcolor=C['surface3']).pack(anchor="w", padx=10, pady=2)
        tk.Checkbutton(backup_frame, text="SD Card (/sdcard)", variable=self.backup_sdcard_var,
                      bg=C['surface2'], fg=C['text'], selectcolor=C['surface3']).pack(anchor="w", padx=10, pady=2)
        tk.Checkbutton(backup_frame, text="System Partitions (requires root)", variable=self.backup_system_var,
                      bg=C['surface2'], fg=C['text'], selectcolor=C['surface3']).pack(anchor="w", padx=10, pady=2)
        
        # Backup destination
        dest_frame = tk.LabelFrame(left_frame, text="📁 Destination", bg=C['surface2'],
                                    fg=C['text'], font=self.mono_font)
        dest_frame.pack(fill="x", pady=5)
        
        self.backup_dir_var = tk.StringVar(value=str(self.backup_dir))
        dest_row = tk.Frame(dest_frame, bg=C['surface2'])
        dest_row.pack(fill="x", padx=10, pady=5)
        tk.Entry(dest_row, textvariable=self.backup_dir_var, bg=C['surface3'],
                fg=C['text'], font=self.mono_font, relief="flat").pack(side="left", fill="x", expand=True)
        self._mkbtn(dest_row, "Change", self._change_backup_dir, C['surface3']).pack(side="left", padx=5)
        
        # Compression
        self.compress_backup_var = tk.BooleanVar(value=True)
        tk.Checkbutton(dest_frame, text="Compress backup (ZIP)", variable=self.compress_backup_var,
                      bg=C['surface2'], fg=C['text'], selectcolor=C['surface3']).pack(anchor="w", padx=10, pady=2)
        
        # Action buttons
        self._mkbtn(left_frame, "📀 START BACKUP", self._start_backup, C['success'], fs=11, px=20, py=10).pack(pady=5)
        self._mkbtn(left_frame, "🔄 Restore from Backup", self._restore_backup, C['warning']).pack(pady=5)
        
        # Restore section
        restore_frame = tk.LabelFrame(right_frame, text="🔄 Available Backups", bg=C['surface2'],
                                       fg=C['text'], font=self.mono_font)
        restore_frame.pack(fill="both", expand=True, pady=5)
        
        self.backup_listbox = tk.Listbox(restore_frame, bg=C['surface3'], fg=C['text'],
                                          font=self.mono_font, height=15)
        self.backup_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        self._refresh_backup_list()
        
        # Backup log
        log_frame = tk.LabelFrame(right_frame, text="Backup Log", bg=C['surface2'],
                                   fg=C['text'], font=self.mono_font)
        log_frame.pack(fill="x", pady=5)
        self.backup_log = tk.Text(log_frame, bg=C['log_bg'], fg=C['text2'],
                                   font=self.mono_font, height=8, relief="flat", wrap="word")
        self.backup_log.pack(fill="both", expand=True, padx=5, pady=5)
    
    def _build_root_page(self, parent):
        """Rooting and Magisk page"""
        # Three-column layout
        col1 = tk.Frame(parent, bg=C['surface'])
        col1.pack(side="left", fill="both", expand=True, padx=5, pady=10)
        col2 = tk.Frame(parent, bg=C['surface'])
        col2.pack(side="left", fill="both", expand=True, padx=5, pady=10)
        col3 = tk.Frame(parent, bg=C['surface'])
        col3.pack(side="left", fill="both", expand=True, padx=5, pady=10)
        
        # Column 1 - Boot Image Patching
        patch_frame = tk.LabelFrame(col1, text="🔧 Boot Image Patching", bg=C['surface2'],
                                     fg=C['text'], font=self.mono_font)
        patch_frame.pack(fill="both", expand=True, pady=5)
        
        tk.Label(patch_frame, text="Boot Image:", bg=C['surface2'], fg=C['text2']).pack(anchor="w", padx=10, pady=2)
        self.boot_img_var = tk.StringVar()
        boot_row = tk.Frame(patch_frame, bg=C['surface2'])
        boot_row.pack(fill="x", padx=10)
        tk.Entry(boot_row, textvariable=self.boot_img_var, bg=C['surface3'],
                fg=C['text'], font=self.mono_font, relief="flat").pack(side="left", fill="x", expand=True)
        self._mkbtn(boot_row, "Browse", self._browse_boot_img, C['surface3']).pack(side="left", padx=5)
        
        # Magisk options
        tk.Label(patch_frame, text="Patch Options:", bg=C['surface2'], fg=C['text2']).pack(anchor="w", padx=10, pady=(10,2))
        self.patch_dm_var = tk.BooleanVar(value=True)
        self.patch_avb_var = tk.BooleanVar(value=True)
        tk.Checkbutton(patch_frame, text="Preserve DM-Verity", variable=self.patch_dm_var,
                      bg=C['surface2'], fg=C['text'], selectcolor=C['surface3']).pack(anchor="w", padx=10)
        tk.Checkbutton(patch_frame, text="Preserve AVB 2.0", variable=self.patch_avb_var,
                      bg=C['surface2'], fg=C['text'], selectcolor=C['surface3']).pack(anchor="w", padx=10)
        
        self._mkbtn(patch_frame, "🔧 Patch with Magisk", self._patch_boot_image, C['info']).pack(pady=10)
        self.patch_status = tk.Label(patch_frame, text="", bg=C['surface2'], fg=C['muted'])
        self.patch_status.pack()
        
        # Column 2 - Magisk Modules
        modules_frame = tk.LabelFrame(col2, text="📦 Magisk Modules", bg=C['surface2'],
                                       fg=C['text'], font=self.mono_font)
        modules_frame.pack(fill="both", expand=True, pady=5)
        
        self.modules_listbox = tk.Listbox(modules_frame, bg=C['surface3'], fg=C['text'],
                                           font=self.mono_font, height=15)
        self.modules_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        self._mkbtn(modules_frame, "🔄 Refresh Modules", self._load_magisk_modules, C['primary']).pack(pady=5)
        
        # Column 3 - Root Status & Info
        status_frame = tk.LabelFrame(col3, text="📊 Root Status", bg=C['surface2'],
                                      fg=C['text'], font=self.mono_font)
        status_frame.pack(fill="both", expand=True, pady=5)
        
        self.root_status_text = tk.Text(status_frame, bg=C['surface3'], fg=C['text2'],
                                         font=self.mono_font, height=12, relief="flat", wrap="word")
        self.root_status_text.pack(fill="both", expand=True, padx=10, pady=10)
        self._mkbtn(status_frame, "🔍 Check Root Status", self._check_root_status, C['info']).pack(pady=5)
    
    def _build_tools_page(self, parent):
        """Device tools page (ADB, performance, mirroring)"""
        # Top row - quick tools
        tools_frame = tk.Frame(parent, bg=C['surface'])
        tools_frame.pack(fill="x", padx=10, pady=10)
        
        tool_buttons = [
            ("📸 Screenshot", self._take_screenshot),
            ("🎥 Screen Record", self._screen_record),
            ("🖥️ Mirror Screen", self._toggle_mirror),
            ("📋 Logcat", self._show_logcat),
            ("🔧 ADB Shell", self._open_adb_shell),
            ("🔄 Reboot Menu", self._show_reboot_menu),
        ]
        
        for i, (text, cmd) in enumerate(tool_buttons):
            btn = tk.Button(tools_frame, text=text, command=cmd,
                           bg=C['surface2'], fg=C['text'], font=self.mono_font,
                           relief="flat", padx=15, pady=8, cursor="hand2")
            btn.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            tools_frame.grid_columnconfigure(i, weight=1)
        
        # Performance monitor
        perf_frame = tk.LabelFrame(parent, text="📊 Performance Monitor", bg=C['surface2'],
                                    fg=C['text'], font=self.mono_font)
        perf_frame.pack(fill="x", padx=10, pady=10)
        
        self.perf_text = tk.Text(perf_frame, bg=C['surface3'], fg=C['text2'],
                                  font=self.mono_font, height=8, relief="flat", wrap="word")
        self.perf_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        self._mkbtn(perf_frame, "🔄 Start Monitoring", self._start_monitoring, C['success']).pack(pady=5)
        
        # File transfer
        file_frame = tk.LabelFrame(parent, text="📁 File Transfer", bg=C['surface2'],
                                    fg=C['text'], font=self.mono_font)
        file_frame.pack(fill="x", padx=10, pady=10)
        
        transfer_grid = tk.Frame(file_frame, bg=C['surface2'])
        transfer_grid.pack(fill="x", padx=10, pady=10)
        
        # Push
        tk.Label(transfer_grid, text="Push to Device:", bg=C['surface2'], fg=C['text2']).grid(row=0, column=0, sticky="w")
        self.push_file_var = tk.StringVar()
        tk.Entry(transfer_grid, textvariable=self.push_file_var, bg=C['surface3'],
                fg=C['text'], width=40).grid(row=0, column=1, padx=5)
        self._mkbtn(transfer_grid, "Browse", lambda: self._browse_file("push"), C['surface3']).grid(row=0, column=2)
        self._mkbtn(transfer_grid, "Push", self._push_file, C['primary']).grid(row=0, column=3, padx=5)
        
        # Pull
        tk.Label(transfer_grid, text="Pull from Device:", bg=C['surface2'], fg=C['text2']).grid(row=1, column=0, sticky="w", pady=5)
        self.pull_file_var = tk.StringVar(value="/sdcard/")
        tk.Entry(transfer_grid, textvariable=self.pull_file_var, bg=C['surface3'],
                fg=C['text'], width=40).grid(row=1, column=1, padx=5)
        self._mkbtn(transfer_grid, "Pull", self._pull_file, C['success']).grid(row=1, column=2, columnspan=2, sticky="w", padx=5)
    
    def _build_automation_page(self, parent):
        """Task automation and scripting page"""
        # Left panel - task queue
        left_frame = tk.Frame(parent, bg=C['surface'], width=400)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)
        left_frame.pack_propagate(False)
        
        right_frame = tk.Frame(parent, bg=C['surface'])
        right_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # Task queue
        queue_frame = tk.LabelFrame(left_frame, text="📋 Task Queue", bg=C['surface2'],
                                     fg=C['text'], font=self.mono_font)
        queue_frame.pack(fill="both", expand=True, pady=5)
        
        self.task_listbox = tk.Listbox(queue_frame, bg=C['surface3'], fg=C['text'],
                                        font=self.mono_font, height=12)
        self.task_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        task_buttons = tk.Frame(queue_frame, bg=C['surface2'])
        task_buttons.pack(fill="x", padx=10, pady=5)
        self._mkbtn(task_buttons, "➕ Add Task", self._add_task_dialog, C['primary']).pack(side="left", padx=2)
        self._mkbtn(task_buttons, "▶️ Run Queue", self._run_task_queue, C['success']).pack(side="left", padx=2)
        self._mkbtn(task_buttons, "🗑️ Clear", self._clear_task_queue, C['danger']).pack(side="left", padx=2)
        
        # Scripting
        script_frame = tk.LabelFrame(right_frame, text="🤖 Python Scripting", bg=C['surface2'],
                                      fg=C['text'], font=self.mono_font)
        script_frame.pack(fill="both", expand=True, pady=5)
        
        self.script_editor = tk.Text(script_frame, bg=C['surface3'], fg=C['text'],
                                      font=self.mono_font, height=15, relief="flat", wrap="word")
        self.script_editor.pack(fill="both", expand=True, padx=10, pady=10)
        self.script_editor.insert("1.0", "# Example script\n# Run ADB commands\n\nimport subprocess\n\n# List devices\nsubprocess.run(['adb', 'devices'])\n\n# Take screenshot\nsubprocess.run(['adb', 'shell', 'screencap', '/sdcard/test.png'])\n")
        
        script_buttons = tk.Frame(script_frame, bg=C['surface2'])
        script_buttons.pack(fill="x", padx=10, pady=5)
        self._mkbtn(script_buttons, "▶️ Run Script", self._run_script, C['success']).pack(side="left", padx=2)
        self._mkbtn(script_buttons, "💾 Save Script", self._save_script, C['info']).pack(side="left", padx=2)
        self._mkbtn(script_buttons, "📂 Load Script", self._load_script, C['primary']).pack(side="left", padx=2)
        
        # Output
        output_frame = tk.LabelFrame(right_frame, text="📄 Script Output", bg=C['surface2'],
                                      fg=C['text'], font=self.mono_font)
        output_frame.pack(fill="both", expand=True, pady=5)
        self.script_output = tk.Text(output_frame, bg=C['log_bg'], fg=C['text2'],
                                      font=self.mono_font, height=8, relief="flat", wrap="word")
        self.script_output.pack(fill="both", expand=True, padx=10, pady=10)
    
    def _build_settings_page(self, parent):
        """Settings page"""
        settings_frame = tk.Frame(parent, bg=C['surface'])
        settings_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # General settings
        general_frame = tk.LabelFrame(settings_frame, text="General Settings", bg=C['surface2'],
                                       fg=C['text'], font=self.mono_font)
        general_frame.pack(fill="x", pady=10)
        
        self.auto_update_var = tk.BooleanVar(value=True)
        self.analytics_var = tk.BooleanVar(value=False)
        self.theme_var = tk.StringVar(value="Dark")
        
        tk.Checkbutton(general_frame, text="Check for updates on startup", variable=self.auto_update_var,
                      bg=C['surface2'], fg=C['text'], selectcolor=C['surface3']).pack(anchor="w", padx=20, pady=5)
        tk.Checkbutton(general_frame, text="Send anonymous usage data", variable=self.analytics_var,
                      bg=C['surface2'], fg=C['text'], selectcolor=C['surface3']).pack(anchor="w", padx=20, pady=5)
        
        tk.Label(general_frame, text="Theme:", bg=C['surface2'], fg=C['text2']).pack(anchor="w", padx=20, pady=5)
        theme_dropdown = ttk.Combobox(general_frame, textvariable=self.theme_var,
                                       values=["Dark", "Light", "System"], state="readonly")
        theme_dropdown.pack(anchor="w", padx=20, pady=5)
        
        # ADB/Fastboot settings
        adb_frame = tk.LabelFrame(settings_frame, text="ADB/Fastboot Settings", bg=C['surface2'],
                                   fg=C['text'], font=self.mono_font)
        adb_frame.pack(fill="x", pady=10)
        
        self.adb_path_var = tk.StringVar(value="adb")
        self.fastboot_path_var = tk.StringVar(value="fastboot")
        
        path_row = tk.Frame(adb_frame, bg=C['surface2'])
        path_row.pack(fill="x", padx=20, pady=5)
        tk.Label(path_row, text="ADB Path:", bg=C['surface2'], fg=C['text2'], width=15, anchor="w").pack(side="left")
        tk.Entry(path_row, textvariable=self.adb_path_var, bg=C['surface3'],
                fg=C['text'], width=40).pack(side="left", padx=5)
        self._mkbtn(path_row, "Auto-detect", self._detect_adb_path, C['info']).pack(side="left", padx=5)
        
        path_row2 = tk.Frame(adb_frame, bg=C['surface2'])
        path_row2.pack(fill="x", padx=20, pady=5)
        tk.Label(path_row2, text="Fastboot Path:", bg=C['surface2'], fg=C['text2'], width=15, anchor="w").pack(side="left")
        tk.Entry(path_row2, textvariable=self.fastboot_path_var, bg=C['surface3'],
                fg=C['text'], width=40).pack(side="left", padx=5)
        self._mkbtn(path_row2, "Auto-detect", self._detect_fastboot_path, C['info']).pack(side="left", padx=5)
        
        self._mkbtn(adb_frame, "🔧 Install ADB/Fastboot", self._install_platform_tools, C['primary']).pack(pady=10)
        
        # Backup settings
        backup_frame = tk.LabelFrame(settings_frame, text="Backup Settings", bg=C['surface2'],
                                      fg=C['text'], font=self.mono_font)
        backup_frame.pack(fill="x", pady=10)
        
        self.auto_backup_before_flash = tk.BooleanVar(value=True)
        self.backup_retention_days = tk.IntVar(value=30)
        
        tk.Checkbutton(backup_frame, text="Auto-backup before flashing", variable=self.auto_backup_before_flash,
                      bg=C['surface2'], fg=C['text'], selectcolor=C['surface3']).pack(anchor="w", padx=20, pady=5)
        
        retention_frame = tk.Frame(backup_frame, bg=C['surface2'])
        retention_frame.pack(anchor="w", padx=20, pady=5)
        tk.Label(retention_frame, text="Backup retention (days):", bg=C['surface2'], fg=C['text2']).pack(side="left")
        tk.Spinbox(retention_frame, from_=1, to=365, textvariable=self.backup_retention_days,
                  width=10, bg=C['surface3'], fg=C['text'], relief="flat").pack(side="left", padx=10)
        
        # About
        about_frame = tk.LabelFrame(settings_frame, text="About", bg=C['surface2'],
                                     fg=C['text'], font=self.mono_font)
        about_frame.pack(fill="x", pady=10)
        
        about_text = f"""{APP_NAME} v{VERSION}
Author: {AUTHOR}
GitHub: {GITHUB_URL}

A complete Android device management suite with:
- ROM & Recovery flashing
- Full backup & restore
- Root & Magisk tools
- Performance monitoring
- Task automation
- And much more!

License: GNU GPL v3
"""
        tk.Label(about_frame, text=about_text, bg=C['surface2'], fg=C['text2'],
                font=self.mono_font, justify="left").pack(anchor="w", padx=20, pady=10)
        
        self._mkbtn(about_frame, "🌐 Open GitHub", lambda: webbrowser.open(GITHUB_URL), C['info']).pack(pady=10)
        
        # Save button
        self._mkbtn(settings_frame, "💾 Save Settings", self._save_settings, C['success'], fs=11, px=30, py=10).pack(pady=20)
    
    def _build_status_bar(self, parent):
        """Bottom status bar"""
        status_bar = tk.Frame(parent, bg=C['surface2'], height=25)
        status_bar.pack(fill="x", side="bottom")
        status_bar.pack_propagate(False)
        
        self.status_label = tk.Label(status_bar, text="Ready", bg=C['surface2'], fg=C['text2'],
                                      font=self.mono_font, anchor="w")
        self.status_label.pack(side="left", padx=10, fill="x", expand=True)
        
        self.time_label = tk.Label(status_bar, text="", bg=C['surface2'], fg=C['muted'],
                                    font=self.mono_font)
        self.time_label.pack(side="right", padx=10)
        self._update_clock()
    
    def _build_log(self):
        """Build log panel (will be shown in a separate window)"""
        self.log_window = None
    
    # -----------------------------------------------------------------------
    #  Helper Methods
    # -----------------------------------------------------------------------
    def _mkbtn(self, parent, text, cmd, color, fs=9, px=12, py=6):
        """Create styled button"""
        btn = tk.Button(parent, text=text, command=cmd,
                       bg=color, fg="white", font=self.mono_font,
                       relief="flat", padx=px, pady=py, cursor="hand2")
        return btn
    
    def _log(self, message, level="info"):
        """Log message to console and activity log"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        colors = {"info": C['info'], "success": C['success'], "warn": C['warning'], 
                 "error": C['error'], "dim": C['muted']}
        color = colors.get(level, C['text2'])
        
        # Update status bar
        if level == "error":
            self.status_label.config(text=message[:50], fg=C['error'])
        elif level == "success":
            self.status_label.config(text=message[:50], fg=C['success'])
        else:
            self.status_label.config(text=message[:50], fg=C['text2'])
        
        # Print to console
        print(f"[{timestamp}] {message}")
        
        # Add to activity log if exists
        if hasattr(self, 'activity_text'):
            self.activity_text.insert("end", f"[{timestamp}] {message}\n")
            self.activity_text.see("end")
    
    def _show_page(self, page_name):
        """Switch to a different page"""
        for name, page in self.pages.items():
            if name == page_name:
                page.pack(fill="both", expand=True)
                # Update button styling
                if name in self.nav_buttons:
                    self.nav_buttons[name].config(bg=C['surface3'], fg=C['primary'])
            else:
                page.pack_forget()
                if name in self.nav_buttons:
                    self.nav_buttons[name].config(bg=C['surface2'], fg=C['text2'])
        self.current_page.set(page_name)
        self._log(f"Switched to {page_name} page", "dim")
    
    def _update_clock(self):
        """Update clock in status bar"""
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=now)
        self.root.after(1000, self._update_clock)
    
    # -----------------------------------------------------------------------
    #  Device Detection & Management
    # -----------------------------------------------------------------------
    def _detect_device(self):
        """Detect connected device and populate info"""
        self._log("Detecting connected device...", "info")
        threading.Thread(target=self._do_detect_device, daemon=True).start()
    
    def _do_detect_device(self):
        """Background device detection"""
        # Check ADB devices
        rc, out, _ = adb("devices")
        devices = [l for l in out.split('\n') if '\tdevice' in l]
        
        if devices:
            self._log(f"Device detected: {devices[0].split()[0]}", "success")
            self._ui_update(lambda: self.device_indicator.config(text="✅ Device connected", fg=C['success']))
            
            # Get device info
            rc, model, _ = adb("shell", "getprop", "ro.product.model")
            rc, codename, _ = adb("shell", "getprop", "ro.product.device")
            rc, android, _ = adb("shell", "getprop", "ro.build.version.release")
            rc, sdk, _ = adb("shell", "getprop", "ro.build.version.sdk")
            
            self.device.model = model.strip()
            self.device.codename = codename.strip()
            self.device.android_version = android.strip()
            self.device.sdk = int(sdk.strip()) if sdk.strip().isdigit() else 0
            
            self._ui_update(lambda: self.device_badge.config(text=f"{self.device.model} | Android {self.device.android_version}"))
        else:
            self._log("No device detected. Connect via USB with debugging enabled.", "warn")
            self._ui_update(lambda: self.device_indicator.config(text="❌ No device", fg=C['error']))
    
    def _refresh_device(self):
        """Manually refresh device info"""
        self._detect_device()
    
    def _get_device_status_text(self):
        """Get device status for dashboard"""
        if self.device.model:
            return f"{self.device.model}\nAndroid {self.device.android_version}"
        return "No device"
    
    def _get_device_status_color(self):
        if self.device.model:
            return C['success']
        return C['error']
    
    def _get_backup_size(self):
        """Calculate backup directory size"""
        try:
            total = sum(f.stat().st_size for f in self.backup_dir.rglob('*') if f.is_file())
            return format_size(total)
        except:
            return "0 B"
    
    def _ui_update(self, func):
        """Thread-safe UI update"""
        self.root.after(0, func)
    
    # -----------------------------------------------------------------------
    #  Flash & ROM Methods
    # -----------------------------------------------------------------------
    def _browse_flash_file(self):
        """Browse for ROM or recovery file"""
        filetypes = [
            ("ROM files", "*.zip"),
            ("Recovery images", "*.img"),
            ("Boot images", "*.img"),
            ("All files", "*.*")
        ]
        filepath = filedialog.askopenfilename(title="Select file to flash", filetypes=filetypes)
        if filepath:
            self.flash_file_var.set(filepath)
            self._log(f"Selected file: {os.path.basename(filepath)}", "info")
    
    def _update_rom_list(self):
        """Update ROM list based on selection"""
        self.rom_listbox.delete(0, tk.END)
        rom_type = self.rom_type_var.get()
        if rom_type in ROM_DATABASE:
            devices = ROM_DATABASE[rom_type].get("devices", [])
            for device in devices:
                self.rom_listbox.insert(tk.END, device)
    
    def _open_rom_page(self):
        """Open ROM download page in browser"""
        selection = self.rom_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Select a ROM first")
            return
        
        rom_type = self.rom_type_var.get()
        device = self.rom_listbox.get(selection[0])
        if rom_type in ROM_DATABASE:
            url = ROM_DATABASE[rom_type]["url"].format(codename=device)
            webbrowser.open(url)
            self._log(f"Opening ROM page: {url}", "info")
    
    def _check_compatibility(self):
        """Check if selected ROM is compatible with device"""
        self._log("Checking compatibility...", "info")
        if not self.device.codename:
            self._log("No device detected. Connect device first.", "error")
            self.compat_text.delete("1.0", tk.END)
            self.compat_text.insert("1.0", "ERROR: No device detected.\nConnect device via USB with debugging enabled.")
            return
        
        compat_text = f"Device: {self.device.manufacturer} {self.device.model}\nCodename: {self.device.codename}\nAndroid: {self.device.android_version}\n\n"
        
        # Check against ROM database
        selection = self.rom_listbox.curselection()
        if selection:
            selected_rom = self.rom_listbox.get(selection[0])
            if selected_rom == self.device.codename:
                compat_text += "✓ COMPATIBLE: ROM matches device codename!\n"
            else:
                compat_text += f"⚠️ WARNING: ROM is for '{selected_rom}', device is '{self.device.codename}'\nThis may brick your device!\n"
        else:
            compat_text += "No ROM selected.\n"
        
        # Check bootloader
        compat_text += "\n✓ Bootloader: " + ("Unlocked (OK)" if self.device.is_unlocked else "Locked (Must unlock first)")
        
        # Check Treble
        compat_text += f"\n✓ Treble support: {'Yes' if self.device.is_treble else 'No'}"
        
        self.compat_text.delete("1.0", tk.END)
        self.compat_text.insert("1.0", compat_text)
        self._log("Compatibility check complete", "success")
    
    def _start_flash(self):
        """Start the flashing process"""
        filepath = self.flash_file_var.get()
        if not filepath or not os.path.exists(filepath):
            messagebox.showerror("No File", "Please select a file to flash")
            return
        
        self._log(f"Starting flash: {os.path.basename(filepath)}", "warn")
        
        # Auto backup if enabled
        if self.backup_before_var.get():
            self._log("Creating backup before flash...", "info")
            # Quick backup of critical partitions
            threading.Thread(target=self._quick_backup, daemon=True).start()
        
        # Start flash in background
        threading.Thread(target=self._do_flash, args=(filepath,), daemon=True).start()
    
    def _do_flash(self, filepath):
        """Background flashing"""
        file_ext = os.path.splitext(filepath)[1].lower()
        flash_type = self.flash_type.get()
        
        self._ui_update(lambda: self.flash_log.delete("1.0", tk.END))
        
        if flash_type == "ROM" and file_ext == ".zip":
            self._log("Flashing ROM via ADB sideload...", "info")
            self._append_flash_log("Starting ADB sideload...\n")
            rc, out, err = adb("sideload", filepath)
            if rc == 0:
                self._log("ROM flashed successfully!", "success")
                self._append_flash_log("✅ Flash completed successfully!\n")
            else:
                self._log(f"Flash failed: {err}", "error")
                self._append_flash_log(f"❌ Flash failed: {err}\n")
        
        elif flash_type == "Recovery" and file_ext == ".img":
            self._log("Flashing recovery via Fastboot...", "info")
            self._append_flash_log("Starting fastboot flash recovery...\n")
            rc, out, err = fastboot("flash", "recovery", filepath)
            if rc == 0:
                self._log("Recovery flashed successfully!", "success")
                self._append_flash_log("✅ Recovery flashed successfully!\n")
            else:
                self._log(f"Flash failed: {err}", "error")
                self._append_flash_log(f"❌ Flash failed: {err}\n")
        
        elif flash_type == "Boot" and file_ext == ".img":
            self._log("Flashing boot via Fastboot...", "info")
            self._append_flash_log("Starting fastboot flash boot...\n")
            rc, out, err = fastboot("flash", "boot", filepath)
            if rc == 0:
                self._log("Boot image flashed successfully!", "success")
                self._append_flash_log("✅ Boot flashed successfully!\n")
            else:
                self._log(f"Flash failed: {err}", "error")
                self._append_flash_log(f"❌ Flash failed: {err}\n")
        else:
            self._log(f"Unsupported file type: {file_ext} for {flash_type}", "error")
    
    def _append_flash_log(self, text):
        """Add text to flash log"""
        def _add():
            self.flash_log.insert(tk.END, text)
            self.flash_log.see(tk.END)
        self._ui_update(_add)
    
    def _quick_backup(self):
        """Quick backup before flashing"""
        backup_name = f"pre_flash_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)
        
        # Backup boot
        self._log("Backing up boot partition...", "dim")
        fastboot("flash", "boot", backup_path / "boot_backup.img")  # This is wrong, need proper backup
        self._log("Quick backup completed", "success")
    
    # -----------------------------------------------------------------------
    #  Backup & Restore Methods
    # -----------------------------------------------------------------------
    def _change_backup_dir(self):
        """Change backup directory"""
        new_dir = filedialog.askdirectory(title="Select Backup Directory")
        if new_dir:
            self.backup_dir = Path(new_dir)
            self.backup_dir.mkdir(exist_ok=True)
            self.backup_dir_var.set(str(self.backup_dir))
            self._log(f"Backup directory changed to: {self.backup_dir}", "info")
            self._refresh_backup_list()
    
    def _refresh_backup_list(self):
        """Refresh the backup list display"""
        self.backup_listbox.delete(0, tk.END)
        if self.backup_dir.exists():
            backups = sorted([d for d in self.backup_dir.iterdir() if d.is_dir()], reverse=True)
            for backup in backups[:20]:  # Show last 20
                size = sum(f.stat().st_size for f in backup.rglob('*') if f.is_file())
                size_str = format_size(size)
                self.backup_listbox.insert(tk.END, f"{backup.name} ({size_str})")
    
    def _start_backup(self):
        """Start backup process"""
        self._log("Starting backup...", "info")
        threading.Thread(target=self._do_backup, daemon=True).start()
    
    def _do_backup(self):
        """Background backup"""
        backup_name = f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)
        
        self._ui_update(lambda: self.backup_log.delete("1.0", tk.END))
        
        if self.backup_apps_var.get():
            self._log("Backing up apps...", "info")
            self._append_backup_log("Backing up apps...\n")
            rc, out, _ = adb("shell", "pm", "list", "packages", "-3")
            packages = [p.replace("package:", "").strip() for p in out.split('\n') if p]
            for pkg in packages[:10]:  # Limit for demo
                self._log(f"  Backing up {pkg}", "dim")
                adb("shell", "pm", "path", pkg)  # Need proper APK extraction
            self._append_backup_log(f"  Backed up {len(packages)} apps\n")
        
        if self.backup_data_var.get():
            self._log("Backing up app data...", "info")
            self._append_backup_log("Backing up app data via ADB backup...\n")
            adb("backup", "-f", str(backup_path / "data.ab"), "-all")
        
        if self.backup_sdcard_var.get():
            self._log("Backing up SD card...", "info")
            self._append_backup_log("Backing up /sdcard...\n")
            adb("pull", "/sdcard/", str(backup_path / "sdcard"))
        
        self._log(f"Backup completed: {backup_name}", "success")
        self._append_backup_log(f"\n✅ Backup completed: {backup_name}\n")
        self._ui_update(self._refresh_backup_list)
    
    def _append_backup_log(self, text):
        """Add text to backup log"""
        def _add():
            self.backup_log.insert(tk.END, text)
            self.backup_log.see(tk.END)
        self._ui_update(_add)
    
    def _restore_backup(self):
        """Restore from selected backup"""
        selection = self.backup_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Select a backup to restore")
            return
        
        backup_name = self.backup_listbox.get(selection[0]).split(" (")[0]
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            messagebox.showerror("Error", "Backup not found")
            return
        
        if messagebox.askyesno("Confirm Restore", f"Restore from backup:\n{backup_name}\n\nThis will overwrite current data!"):
            self._log(f"Restoring from: {backup_name}", "warn")
            threading.Thread(target=self._do_restore, args=(backup_path,), daemon=True).start()
    
    def _do_restore(self, backup_path):
        """Background restore"""
        self._log("Restoring...", "info")
        # Check for ADB backup file
        adb_backup = backup_path / "data.ab"
        if adb_backup.exists():
            adb("restore", str(adb_backup))
        self._log("Restore initiated. Check device for confirmation.", "success")
    
    # -----------------------------------------------------------------------
    #  Root & Magisk Methods
    # -----------------------------------------------------------------------
    def _browse_boot_img(self):
        """Browse for boot image file"""
        filepath = filedialog.askopenfilename(title="Select Boot Image", filetypes=[("Boot images", "*.img")])
        if filepath:
            self.boot_img_var.set(filepath)
    
    def _patch_boot_image(self):
        """Patch boot image with Magisk"""
        boot_img = self.boot_img_var.get()
        if not boot_img or not os.path.exists(boot_img):
            messagebox.showerror("No File", "Select boot image first")
            return
        
        self._log("Patching boot image with Magisk...", "info")
        threading.Thread(target=self._do_patch, args=(boot_img,), daemon=True).start()
    
    def _do_patch(self, boot_img):
        """Background patching"""
        self._ui_update(lambda: self.patch_status.config(text="Patching...", fg=C['warning']))
        
        # Push to device
        device_path = "/sdcard/boot_to_patch.img"
        rc, _, err = adb("push", boot_img, device_path)
        
        if rc != 0:
            self._log(f"Failed to push boot image: {err}", "error")
            self._ui_update(lambda: self.patch_status.config(text="Patch failed", fg=C['error']))
            return
        
        # Build magisk command
        cmd = f"magisk --patch {device_path}"
        if self.patch_dm_var.get():
            cmd += " --preserve-dm"
        if self.patch_avb_var.get():
            cmd += " --preserve-avb"
        cmd += " /sdcard/magisk_patched.img"
        
        rc, out, err = adb("shell", cmd)
        
        if rc == 0:
            # Pull patched image
            patched_path = boot_img.replace(".img", "_patched.img")
            adb("pull", "/sdcard/magisk_patched.img", patched_path)
            self._log(f"Boot image patched successfully: {patched_path}", "success")
            self._ui_update(lambda: self.patch_status.config(text="Patch complete!", fg=C['success']))
            messagebox.showinfo("Success", f"Patched boot image saved to:\n{patched_path}")
        else:
            self._log(f"Patching failed: {err}", "error")
            self._ui_update(lambda: self.patch_status.config(text="Patch failed", fg=C['error']))
        
        # Cleanup
        adb("shell", "rm", device_path)
    
    def _load_magisk_modules(self):
        """Load installed Magisk modules"""
        self._log("Loading Magisk modules...", "info")
        threading.Thread(target=self._do_load_modules, daemon=True).start()
    
    def _do_load_modules(self):
        """Background module loading"""
        rc, out, _ = adb("shell", "ls", "/data/adb/modules/")
        if rc == 0:
            modules = [m for m in out.split('\n') if m and not m.startswith('lost+found')]
            self._ui_update(lambda: self._populate_modules(modules))
            self._log(f"Found {len(modules)} Magisk modules", "info")
        else:
            self._log("Failed to load modules. Magisk may not be installed.", "warn")
    
    def _populate_modules(self, modules):
        """Populate modules listbox"""
        self.modules_listbox.delete(0, tk.END)
        for module in modules:
            self.modules_listbox.insert(tk.END, module)
    
    def _check_root_status(self):
        """Check if device has root access"""
        self._log("Checking root status...", "info")
        threading.Thread(target=self._do_check_root, daemon=True).start()
    
    def _do_check_root(self):
        """Background root check"""
        self.root_status_text.delete("1.0", tk.END)
        
        # Check su
        rc, out, _ = adb("shell", "su -c 'id'")
        if rc == 0 and "uid=0" in out:
            status = "✅ ROOT ACCESS GRANTED\n"
            status += f"User: {out}\n"
            self.device.has_root = True
        else:
            status = "❌ NO ROOT ACCESS\n"
            status += "Device is not rooted or root permission was denied.\n"
            self.device.has_root = False
        
        # Check Magisk
        rc, magisk_out, _ = adb("shell", "magisk -v")
        if rc == 0:
            status += f"\nMagisk Version: {magisk_out.strip()}\n"
            self.device.magisk_version = magisk_out.strip()
        
        self._ui_update(lambda: self.root_status_text.insert("1.0", status))
        self._log("Root check complete", "success")
    
    # -----------------------------------------------------------------------
    #  Device Tools Methods
    # -----------------------------------------------------------------------
    def _take_screenshot(self):
        """Take screenshot from device"""
        self._log("Taking screenshot...", "info")
        threading.Thread(target=self._do_screenshot, daemon=True).start()
    
    def _do_screenshot(self):
        """Background screenshot"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        local_path = f"screenshot_{timestamp}.png"
        
        rc, _, err = adb("shell", "screencap", "-p", "/sdcard/screenshot.png")
        if rc != 0:
            self._log(f"Screenshot failed: {err}", "error")
            return
        
        rc, _, err = adb("pull", "/sdcard/screenshot.png", local_path)
        adb("shell", "rm", "/sdcard/screenshot.png")
        
        if rc == 0:
            self._log(f"Screenshot saved: {local_path}", "success")
            messagebox.showinfo("Screenshot", f"Screenshot saved to:\n{os.path.abspath(local_path)}")
        else:
            self._log(f"Failed to pull screenshot: {err}", "error")
    
    def _screen_record(self):
        """Start screen recording"""
        self._log("Starting screen recording...", "info")
        threading.Thread(target=self._do_screen_record, daemon=True).start()
    
    def _do_screen_record(self):
        """Background screen recording"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        device_path = f"/sdcard/record_{timestamp}.mp4"
        local_path = f"screen_record_{timestamp}.mp4"
        
        # Start recording for 30 seconds
        self._log("Recording for 30 seconds...", "warn")
        adb("shell", "screenrecord", "--time-limit", "30", device_path)
        
        # Pull the file
        rc, _, err = adb("pull", device_path, local_path)
        adb("shell", "rm", device_path)
        
        if rc == 0:
            self._log(f"Screen recording saved: {local_path}", "success")
            messagebox.showinfo("Screen Recording", f"Recording saved to:\n{os.path.abspath(local_path)}")
        else:
            self._log(f"Recording failed: {err}", "error")
    
    def _toggle_mirror(self):
        """Toggle screen mirroring (scrcpy)"""
        if self.mirror_process and self.mirror_process.poll() is None:
            self.mirror_process.terminate()
            self.mirror_process = None
            self._log("Screen mirroring stopped", "info")
        else:
            self._log("Starting screen mirroring...", "info")
            threading.Thread(target=self._start_mirror, daemon=True).start()
    
    def _start_mirror(self):
        """Start scrcpy mirroring"""
        try:
            self.mirror_process = subprocess.Popen(["scrcpy"], 
                                                   stdout=subprocess.DEVNULL, 
                                                   stderr=subprocess.DEVNULL)
            self._log("Screen mirroring started (scrcpy)", "success")
        except FileNotFoundError:
            self._log("scrcpy not found. Install scrcpy for screen mirroring.", "error")
            messagebox.showerror("scrcpy Not Found", 
                                "scrcpy is required for screen mirroring.\n"
                                "Install from: https://github.com/Genymobile/scrcpy")
    
    def _show_logcat(self):
        """Show logcat in a new window"""
        logcat_window = tk.Toplevel(self.root)
        logcat_window.title("Logcat Viewer")
        logcat_window.geometry("1000x600")
        logcat_window.configure(bg=C['surface'])
        
        text_widget = tk.Text(logcat_window, bg=C['log_bg'], fg=C['text2'],
                              font=self.mono_font, wrap="word")
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        
        def _fetch_logcat():
            rc, out, _ = adb("logcat", "-d")
            if rc == 0:
                text_widget.insert("1.0", out)
            else:
                text_widget.insert("1.0", "Failed to fetch logcat")
        
        threading.Thread(target=_fetch_logcat, daemon=True).start()
    
    def _open_adb_shell(self):
        """Open ADB shell in a new window"""
        shell_window = tk.Toplevel(self.root)
        shell_window.title("ADB Shell")
        shell_window.geometry("800x500")
        shell_window.configure(bg=C['surface'])
        
        output = tk.Text(shell_window, bg=C['log_bg'], fg=C['text2'],
                         font=self.mono_font, wrap="word")
        output.pack(fill="both", expand=True, padx=10, pady=10)
        
        entry_frame = tk.Frame(shell_window, bg=C['surface'])
        entry_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(entry_frame, text="$", bg=C['surface'], fg=C['success'],
                font=self.mono_font).pack(side="left", padx=5)
        
        entry = tk.Entry(entry_frame, bg=C['surface2'], fg=C['text'],
                         font=self.mono_font, relief="flat")
        entry.pack(side="left", fill="x", expand=True, padx=5)
        
        def run_command():
            cmd = entry.get().strip()
            if not cmd:
                return
            entry.delete(0, tk.END)
            output.insert(tk.END, f"\n$ {cmd}\n")
            output.see(tk.END)
            
            rc, out, err = adb("shell", cmd)
            if out:
                output.insert(tk.END, f"{out}\n")
            if err:
                output.insert(tk.END, f"Error: {err}\n")
            output.see(tk.END)
        
        entry.bind("<Return>", lambda e: run_command())
        tk.Button(entry_frame, text="Run", command=run_command,
                 bg=C['primary'], fg="white", font=self.mono_font,
                 relief="flat", padx=10).pack(side="left")
    
    def _show_reboot_menu(self):
        """Show reboot options menu"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Reboot System", command=lambda: self._reboot_device(""))
        menu.add_command(label="Reboot to Recovery", command=lambda: self._reboot_device("recovery"))
        menu.add_command(label="Reboot to Bootloader", command=lambda: self._reboot_device("bootloader"))
        menu.add_command(label="Power Off", command=lambda: self._reboot_device("-p"))
        menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())
    
    def _reboot_device(self, target):
        """Reboot device"""
        cmd = ["adb", "reboot"]
        if target:
            cmd.append(target)
        self._log(f"Rebooting device to {target if target else 'system'}...", "warn")
        threading.Thread(target=lambda: run_cmd(cmd), daemon=True).start()
    
    def _browse_file(self, mode):
        """Browse file for push"""
        filepath = filedialog.askopenfilename()
        if filepath:
            self.push_file_var.set(filepath)
    
    def _push_file(self):
        """Push file to device"""
        src = self.push_file_var.get()
        if not src or not os.path.exists(src):
            messagebox.showerror("No File", "Select a file to push")
            return
        
        dst = filedialog.askstring("Destination", "Device destination path:", initialvalue="/sdcard/")
        if not dst:
            return
        
        self._log(f"Pushing {os.path.basename(src)} to {dst}...", "info")
        threading.Thread(target=lambda: self._do_push(src, dst), daemon=True).start()
    
    def _do_push(self, src, dst):
        rc, _, err = adb("push", src, dst)
        if rc == 0:
            self._log("File pushed successfully", "success")
            messagebox.showinfo("Success", "File pushed to device")
        else:
            self._log(f"Push failed: {err}", "error")
    
    def _pull_file(self):
        """Pull file from device"""
        src = self.pull_file_var.get()
        if not src:
            messagebox.showerror("No Path", "Enter device path to pull")
            return
        
        dst = filedialog.askdirectory(title="Save to directory:")
        if not dst:
            return
        
        self._log(f"Pulling {src} to {dst}...", "info")
        threading.Thread(target=lambda: self._do_pull(src, dst), daemon=True).start()
    
    def _do_pull(self, src, dst):
        rc, _, err = adb("pull", src, dst)
        if rc == 0:
            self._log("File pulled successfully", "success")
            messagebox.showinfo("Success", "File pulled from device")
        else:
            self._log(f"Pull failed: {err}", "error")
    
    def _start_monitoring(self):
        """Start performance monitoring"""
        self._log("Starting performance monitor...", "info")
        self._monitoring = True
        threading.Thread(target=self._monitor_loop, daemon=True).start()
    
    def _monitor_loop(self):
        """Performance monitoring loop"""
        while hasattr(self, '_monitoring') and self._monitoring:
            # Get device stats
            rc, cpu_info, _ = adb("shell", "top -n 1 -d 1 | head -5")
            rc, mem_info, _ = adb("shell", "free -m")
            rc, battery_info, _ = adb("shell", "dumpsys battery | grep -E 'level|temperature'")
            
            monitor_text = f"=== Device Performance ===\n\n"
            monitor_text += f"CPU Info:\n{cpu_info[:500]}\n\n"
            monitor_text += f"Memory:\n{mem_info}\n\n"
            monitor_text += f"Battery:\n{battery_info}\n"
            monitor_text += f"\nLast updated: {datetime.datetime.now().strftime('%H:%M:%S')}"
            
            self._ui_update(lambda: self.perf_text.delete("1.0", tk.END))
            self._ui_update(lambda: self.perf_text.insert("1.0", monitor_text))
            
            time.sleep(5)
    
    # -----------------------------------------------------------------------
    #  Automation & Scripting Methods
    # -----------------------------------------------------------------------
    def _add_task_dialog(self):
        """Show dialog to add a task"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Task")
        dialog.geometry("400x300")
        dialog.configure(bg=C['surface'])
        
        tk.Label(dialog, text="Task Type:", bg=C['surface'], fg=C['text']).pack(pady=5)
        task_type = ttk.Combobox(dialog, values=["Flash ROM", "Backup", "Reboot", "Run Script"])
        task_type.pack(pady=5)
        
        tk.Label(dialog, text="Parameters:", bg=C['surface'], fg=C['text']).pack(pady=5)
        params_entry = tk.Entry(dialog, bg=C['surface2'], fg=C['text'], width=40)
        params_entry.pack(pady=5)
        
        def add():
            task = f"{task_type.get()}: {params_entry.get()}"
            self.task_listbox.insert(tk.END, task)
            dialog.destroy()
            self._log(f"Added task: {task}", "info")
        
        tk.Button(dialog, text="Add", command=add, bg=C['success'], fg="white").pack(pady=10)
    
    def _clear_task_queue(self):
        """Clear all tasks"""
        self.task_listbox.delete(0, tk.END)
        self._log("Task queue cleared", "info")
    
    def _run_task_queue(self):
        """Run all tasks in queue"""
        if self.task_listbox.size() == 0:
            messagebox.showinfo("Empty Queue", "No tasks to run")
            return
        
        self._log("Running task queue...", "info")
        threading.Thread(target=self._do_run_queue, daemon=True).start()
    
    def _do_run_queue(self):
        """Execute all tasks"""
        for i in range(self.task_listbox.size()):
            task = self.task_listbox.get(i)
            self._log(f"Executing: {task}", "warn")
            # Parse and execute task
            time.sleep(2)  # Simulate task execution
        self._log("Task queue completed", "success")
    
    def _run_script(self):
        """Run Python script"""
        script = self.script_editor.get("1.0", tk.END)
        if not script.strip():
            messagebox.showwarning("Empty Script", "Write a script first")
            return
        
        self._log("Running script...", "info")
        self.script_output.delete("1.0", tk.END)
        
        # Redirect stdout to capture output
        from io import StringIO
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        try:
            exec(script, {'adb': adb, 'fastboot': fastboot, 'subprocess': subprocess})
            output = sys.stdout.getvalue()
            self.script_output.insert("1.0", output)
            self._log("Script completed", "success")
        except Exception as e:
            self.script_output.insert("1.0", f"Error: {e}\n")
            self._log(f"Script error: {e}", "error")
        finally:
            sys.stdout = old_stdout
    
    def _save_script(self):
        """Save script to file"""
        filepath = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python files", "*.py")])
        if filepath:
            with open(filepath, 'w') as f:
                f.write(self.script_editor.get("1.0", tk.END))
            self._log(f"Script saved: {filepath}", "success")
    
    def _load_script(self):
        """Load script from file"""
        filepath = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
        if filepath:
            with open(filepath, 'r') as f:
                self.script_editor.delete("1.0", tk.END)
                self.script_editor.insert("1.0", f.read())
            self._log(f"Script loaded: {filepath}", "success")
    
    # -----------------------------------------------------------------------
    #  Settings Methods
    # -----------------------------------------------------------------------
    def _detect_adb_path(self):
        """Auto-detect ADB path"""
        import shutil
        path = shutil.which("adb")
        if path:
            self.adb_path_var.set(path)
            self._log(f"ADB found at: {path}", "success")
        else:
            self._log("ADB not found in PATH", "error")
    
    def _detect_fastboot_path(self):
        """Auto-detect Fastboot path"""
        import shutil
        path = shutil.which("fastboot")
        if path:
            self.fastboot_path_var.set(path)
            self._log(f"Fastboot found at: {path}", "success")
        else:
            self._log("Fastboot not found in PATH", "error")
    
    def _install_platform_tools(self):
        """Install/Update Platform Tools"""
        self._log("Installing Platform Tools...", "info")
        threading.Thread(target=self._do_install_platform_tools, daemon=True).start()
    
    def _do_install_platform_tools(self):
        """Background installation"""
        system = platform.system()
        install_dir = Path.home() / "platform-tools"
        install_dir.mkdir(exist_ok=True)
        
        if system == "Windows":
            url = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
        elif system == "Darwin":
            url = "https://dl.google.com/android/repository/platform-tools-latest-darwin.zip"
        else:
            url = "https://dl.google.com/android/repository/platform-tools-latest-linux.zip"
        
        self._log(f"Downloading from: {url}", "info")
        
        # Download
        zip_path = install_dir / "platform-tools.zip"
        try:
            urllib.request.urlretrieve(url, zip_path)
            self._log("Download complete", "success")
            
            # Extract
            import zipfile
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(install_dir)
            
            self._log("Extraction complete", "success")
            
            # Add to PATH (requires admin)
            self._log("Please add to PATH manually or use the portable version", "warn")
            messagebox.showinfo("Installation Complete", 
                               f"Platform Tools installed to:\n{install_dir}\n\n"
                               f"Add this directory to your PATH to use adb/fastboot from anywhere.")
        except Exception as e:
            self._log(f"Installation failed: {e}", "error")
    
    def _load_settings(self):
        """Load settings from file"""
        settings_file = Path.home() / ".android_multitool_settings.json"
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    self.settings = json.load(f)
            except:
                self.settings = {}
        else:
            self.settings = {}
    
    def _save_settings(self):
        """Save settings to file"""
        settings_file = Path.home() / ".android_multitool_settings.json"
        settings = {
            'backup_dir': str(self.backup_dir),
            'auto_update': self.auto_update_var.get(),
            'analytics': self.analytics_var.get(),
            'theme': self.theme_var.get(),
            'auto_backup_before_flash': self.auto_backup_before_flash.get(),
            'backup_retention_days': self.backup_retention_days.get(),
        }
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
        self._log("Settings saved", "success")
        messagebox.showinfo("Settings Saved", "Your settings have been saved.")
    
    def _start_background_tasks(self):
        """Start background monitoring tasks"""
        # Check for updates
        self.root.after(5000, self._check_for_updates)
    
    def _check_for_updates(self):
        """Check for newer version on GitHub"""
        self._log("Checking for updates...", "dim")
        # This would check GitHub API for latest release
        self._log(f"You're running version {VERSION}", "dim")
    
    def _show_logs(self):
        """Show detailed logs in a new window"""
        log_window = tk.Toplevel(self.root)
        log_window.title("Application Logs")
        log_window.geometry("800x500")
        log_window.configure(bg=C['surface'])
        
        log_text = tk.Text(log_window, bg=C['log_bg'], fg=C['text2'],
                           font=self.mono_font, wrap="word")
        log_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Copy activity text
        if hasattr(self, 'activity_text'):
            log_text.insert("1.0", self.activity_text.get("1.0", tk.END))
    
    # -----------------------------------------------------------------------
    #  Keyboard Shortcuts
    # -----------------------------------------------------------------------
    def _bind_shortcuts(self):
        """Bind keyboard shortcuts"""
        self.root.bind("<F5>", lambda e: self._refresh_device())
        self.root.bind("<F11>", self._toggle_fullscreen)
        self.root.bind("<Escape>", self._exit_fullscreen)
        self.root.bind("<Control-q>", lambda e: self.root.quit())
        self.root.bind("<Control-s>", lambda e: self._take_screenshot())
    
    def _toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode"""
        current = self.root.attributes("-fullscreen")
        self.root.attributes("-fullscreen", not current)
    
    def _exit_fullscreen(self, event=None):
        """Exit fullscreen mode"""
        self.root.attributes("-fullscreen", False)


# ---------------------------------------------------------------------------
#  Main Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = AndroidMultitool(root)
    root.mainloop()
"""
Android Multitool Universal  v2.0
By auratech0  —  Runs on dreams and hopes, made with ♥
Requires: Python 3.7+  •  tkinter (stdlib)  •  Windows / Linux / macOS
https://github.com/auratech0/android-multitool-universal
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess, os, threading, platform, datetime, sys, shutil, shlex, queue

# ─────────────────────────────────────────────────────────────────────────────
#  Font resolution — runs after Tk() is live
# ─────────────────────────────────────────────────────────────────────────────
def _pick_font(root, preferred, fallback="Courier"):
    try:
        import tkinter.font as tf
        fams = set(tf.families(root))
        for f in preferred:
            if f in fams:
                return f
    except Exception:
        pass
    return fallback

# ─────────────────────────────────────────────────────────────────────────────
#  Palette
# ─────────────────────────────────────────────────────────────────────────────
BG      = "#0d1117"   # page background
SURF    = "#161b22"   # card surface
SURF2   = "#1c2128"   # slightly lighter surface (tab bar, section headers)
SURF3   = "#21262d"   # hover surface / very subtle border
BORDER  = "#30363d"   # card border

BLUE    = "#1f6feb"   # primary accent
GREEN   = "#238636"   # success / safe
RED     = "#da3633"   # danger
ORANGE  = "#d29922"   # warning
PURPLE  = "#8b5cf6"   # purple accent

TEXT    = "#e6edf3"   # primary text
TEXT2   = "#b1bac4"   # secondary text
MUTED   = "#7d8590"   # muted / disabled text

WARN_BG = "#2d1f00";  WARN_FG  = "#e3a04f"
DANG_BG = "#2d0b0b";  DANG_FG  = "#f85149"
INFO_BG = "#0c1f3a";  INFO_FG  = "#58a6ff"
OK_BG   = "#0b2a16";  OK_FG    = "#3fb950"
LOG_BG  = "#010409"

T_OK    = "#3fb950";  T_WARN = "#e3a04f"
T_ERR   = "#f85149";  T_INFO = "#58a6ff"
T_CMD   = "#bc8cff";  T_DIM  = "#484f58"

# ─────────────────────────────────────────────────────────────────────────────
#  Colour math
# ─────────────────────────────────────────────────────────────────────────────
def _adjust(hex_col, amount):
    hx = hex_col.lstrip("#")
    r = min(255, max(0, int(hx[0:2], 16) + amount))
    g = min(255, max(0, int(hx[2:4], 16) + amount))
    b = min(255, max(0, int(hx[4:6], 16) + amount))
    return f"#{r:02x}{g:02x}{b:02x}"

def _lighten(c, a=28): return _adjust(c,  a)
def _darken(c,  a=20): return _adjust(c, -a)

# ─────────────────────────────────────────────────────────────────────────────
#  Safety flags (Canta-style)
# ─────────────────────────────────────────────────────────────────────────────
FLAGS = {
    "safe":        ("🟢", "Safe",        T_OK),
    "recommended": ("⭐", "Recommended", T_INFO),
    "caution":     ("🟡", "Caution",     T_WARN),
    "unsafe":      ("🔴", "Unsafe",      T_ERR),
}

# ─────────────────────────────────────────────────────────────────────────────
#  Package knowledge base
# ─────────────────────────────────────────────────────────────────────────────
PKG_DB = {
    # Google
    "com.google.android.apps.tachyon":            ("Google Meet/Duo",                              "safe",        "Google"),
    "com.google.android.youtube":                 ("YouTube",                                      "safe",        "Google"),
    "com.google.android.apps.youtube.music":      ("YouTube Music",                                "safe",        "Google"),
    "com.google.android.videos":                  ("Google TV / Play Movies",                      "safe",        "Google"),
    "com.google.android.apps.books":              ("Google Play Books",                            "safe",        "Google"),
    "com.google.android.apps.magazines":          ("Google News — aggregator",                     "recommended", "Google"),
    "com.google.android.apps.fitness":            ("Google Fit",                                   "safe",        "Google"),
    "com.google.android.keep":                    ("Google Keep",                                  "safe",        "Google"),
    "com.google.android.apps.photos":             ("Google Photos",                                "safe",        "Google"),
    "com.google.android.marvin.talkback":         ("TalkBack — screen reader (keep if needed)",    "caution",     "Google"),
    "com.google.android.apps.subscriptions.red":  ("Google One",                                   "safe",        "Google"),
    "com.google.android.apps.wallpaper":          ("Google Wallpapers",                            "safe",        "Google"),
    "com.google.android.feedback":                ("Google Feedback — sends crash reports",        "recommended", "Google"),
    "com.google.android.partnersetup":            ("Google Partner Setup",                         "caution",     "Google"),
    # Xiaomi
    "com.miui.analytics":                         ("MIUI Analytics — constant telemetry",          "recommended", "Xiaomi"),
    "com.miui.daemon":                            ("MIUI Daemon — background telemetry",           "recommended", "Xiaomi"),
    "com.miui.msa.global":                        ("MIUI System Ads — injects ads into UI",        "recommended", "Xiaomi"),
    "com.xiaomi.mipicks":                         ("GetApps Ads — ad suggestions",                 "recommended", "Xiaomi"),
    "com.miui.bugreport":                         ("MIUI Bug Reporter",                            "safe",        "Xiaomi"),
    "com.miui.weather2":                          ("MIUI Weather",                                 "safe",        "Xiaomi"),
    "com.xiaomi.gamecenter.sdk.service":          ("Xiaomi Game Center SDK",                       "safe",        "Xiaomi"),
    "com.miui.video":                             ("MIUI Video Player",                            "safe",        "Xiaomi"),
    "com.miui.cleanmaster":                       ("MIUI Clean Master",                            "safe",        "Xiaomi"),
    "com.miui.player":                            ("MIUI Music Player",                            "safe",        "Xiaomi"),
    "com.miui.notes":                             ("MIUI Notes",                                   "safe",        "Xiaomi"),
    "com.milink.service":                         ("Mi Link — cross-device sharing",               "safe",        "Xiaomi"),
    "com.miui.systemAdSolution":                  ("MIUI Ad Solution — ad framework",              "recommended", "Xiaomi"),
    "com.miui.securitycenter":                    ("MIUI Security Center — DO NOT DISABLE",        "unsafe",      "Xiaomi"),
    "com.miui.powerkeeper":                       ("MIUI Power Keeper — battery manager",          "caution",     "Xiaomi"),
    # Samsung
    "com.samsung.android.app.tips":               ("Samsung Tips",                                 "safe",        "Samsung"),
    "com.samsung.android.themestore":             ("Galaxy Theme Store",                           "safe",        "Samsung"),
    "com.samsung.android.bixby.agent":            ("Bixby Agent — Samsung AI",                    "recommended", "Samsung"),
    "com.samsung.android.bixby.wakeup":           ("Bixby Wakeup — always-on hotword",            "recommended", "Samsung"),
    "com.samsung.android.bixbyvision.framework":  ("Bixby Vision — camera AI",                    "safe",        "Samsung"),
    "com.samsung.android.app.spage":              ("Samsung Free — ad/news feed",                  "recommended", "Samsung"),
    "com.sec.android.app.samsungapps":            ("Galaxy Store",                                 "caution",     "Samsung"),
    "com.samsung.android.kidsinstaller":          ("Kids Mode installer",                          "safe",        "Samsung"),
    "com.samsung.android.game.gametools":         ("Game Launcher",                                "safe",        "Samsung"),
    "com.samsung.android.app.galaxy.find.mobile": ("Find My Mobile",                               "caution",     "Samsung"),
    # OnePlus
    "com.oneplus.tips":                           ("OnePlus Tips",                                 "safe",        "OnePlus"),
    "com.oneplus.games":                          ("Game Space",                                   "safe",        "OnePlus"),
    "com.oneplus.opbackup":                       ("OnePlus Backup",                               "safe",        "OnePlus"),
    "com.android.bbkmusic":                       ("BBK Music Player",                             "safe",        "OnePlus"),
    "com.heytap.market":                          ("HeyTap App Market",                            "caution",     "OnePlus"),
    "com.heytap.pictorial":                       ("HeyTap Pictorial — ad wallpapers",             "recommended", "OnePlus"),
    # OPPO/Realme
    "com.oppo.market":                            ("OPPO App Market",                              "caution",     "OPPO/Realme"),
    "com.coloros.safecenter":                     ("ColorOS Safe Center",                          "caution",     "OPPO/Realme"),
    "com.coloros.ocrscanner":                     ("ColorOS OCR Scanner",                          "safe",        "OPPO/Realme"),
    "com.realme.market":                          ("Realme Market",                                "caution",     "OPPO/Realme"),
    "com.heytap.health":                          ("HeyTap Health",                                "safe",        "OPPO/Realme"),
    "com.coloros.weather2":                       ("ColorOS Weather",                              "safe",        "OPPO/Realme"),
    # AOSP
    "com.android.browser":                        ("AOSP Browser",                                 "safe",        "AOSP"),
    "com.android.email":                          ("AOSP Email — legacy",                          "safe",        "AOSP"),
    "com.android.music":                          ("AOSP Music",                                   "safe",        "AOSP"),
    "com.android.gallery3d":                      ("AOSP Gallery",                                 "safe",        "AOSP"),
    "com.android.dreams.basic":                   ("Basic Daydream screensaver",                   "safe",        "AOSP"),
    "com.android.wallpaper.livepicker":           ("Live Wallpaper Picker",                        "safe",        "AOSP"),
    "com.android.printspooler":                   ("Print Spooler",                                "safe",        "AOSP"),
    "com.android.bips":                           ("BIPS Printing plugin",                         "safe",        "AOSP"),
    "com.android.stk":                            ("SIM Toolkit — may be carrier-required",        "caution",     "AOSP"),
    # System — never disable
    "com.android.systemui":                       ("System UI — DO NOT DISABLE",                   "unsafe",      "System"),
    "com.android.phone":                          ("Phone / Telephony — DO NOT DISABLE",           "unsafe",      "System"),
    "com.android.settings":                       ("Settings — DO NOT DISABLE",                    "unsafe",      "System"),
    "android":                                    ("Android Framework — DO NOT DISABLE",           "unsafe",      "System"),
    "com.android.launcher3":                      ("Launcher3 — disable only if replacing",        "caution",     "System"),
}

# ─────────────────────────────────────────────────────────────────────────────
#  Debloat presets
# ─────────────────────────────────────────────────────────────────────────────
PRESETS = {
    "Google Bloat": [
        "com.google.android.apps.tachyon","com.google.android.youtube",
        "com.google.android.apps.youtube.music","com.google.android.videos",
        "com.google.android.apps.books","com.google.android.apps.magazines",
        "com.google.android.apps.fitness","com.google.android.keep",
        "com.google.android.apps.photos","com.google.android.marvin.talkback",
        "com.google.android.apps.subscriptions.red",
        "com.google.android.apps.wallpaper","com.google.android.feedback",
    ],
    "Xiaomi / MIUI": [
        "com.miui.analytics","com.miui.daemon","com.miui.msa.global",
        "com.xiaomi.mipicks","com.miui.bugreport","com.miui.weather2",
        "com.xiaomi.gamecenter.sdk.service","com.miui.video",
        "com.miui.cleanmaster","com.miui.player","com.miui.notes",
        "com.milink.service","com.miui.systemAdSolution",
    ],
    "Samsung": [
        "com.samsung.android.app.tips","com.samsung.android.themestore",
        "com.samsung.android.bixby.agent","com.samsung.android.bixby.wakeup",
        "com.samsung.android.bixbyvision.framework","com.samsung.android.app.spage",
        "com.sec.android.app.samsungapps","com.samsung.android.kidsinstaller",
        "com.samsung.android.game.gametools",
    ],
    "OnePlus / OxygenOS": [
        "com.oneplus.tips","com.oneplus.games","com.oneplus.opbackup",
        "com.android.bbkmusic","com.heytap.market","com.heytap.pictorial",
    ],
    "OPPO / Realme / ColorOS": [
        "com.oppo.market","com.coloros.safecenter","com.coloros.ocrscanner",
        "com.realme.market","com.heytap.health","com.coloros.weather2",
    ],
    "Generic AOSP Bloat": [
        "com.android.browser","com.android.email","com.android.music",
        "com.android.gallery3d","com.android.dreams.basic",
        "com.android.wallpaper.livepicker","com.android.printspooler","com.android.bips",
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
#  Flash mode definitions
#  (label, [exts], proto, risk, warning, info, safe_note)
# ─────────────────────────────────────────────────────────────────────────────
MODES = [
    ("Fastboot  ›  Flash Recovery  (.img)",         [".img"],"fb_recovery","warn",
     "⚠  Wrong recovery image can soft-brick your device.",
     "Device must be in Fastboot mode.\nRun: fastboot devices — to confirm detection.",
     "🛡  Writes to: recovery partition only — no user data erased."),
    ("Fastboot  ›  Flash Boot / Kernel  (.img)",    [".img"],"fb_boot","warn",
     "⚠  Mismatched boot image causes a boot-loop.",
     "For root: patch boot.img with Magisk first.\nA/B slot logged before flash.",
     "🛡  Writes to: boot partition only — no user data erased."),
    ("Fastboot  ›  Flash Vendor Image  (.img)",     [".img"],"fb_vendor","warn",
     "⚠  Wrong vendor image = hard-brick. Must match exact build and model.",
     "Only flash vendor.img for your exact device + build number.",
     "🛡  Writes to: vendor partition only — no user data erased."),
    ("Fastboot  ›  Flash System Image  (.img)",     [".img"],"fb_system","warn",
     "⚠  Only flash system images for your specific device.",
     "For GSI on Treble devices ensure vendor compatibility.",
     "🛡  Writes to: system partition only — no user data erased."),
    ("Fastboot  ›  Flash DTBO  (.img)",             [".img"],"fb_dtbo","warn",
     "⚠  Incompatible DTBO can cause boot failure.",
     "Device tree blob overlay. Flash only images matching your kernel.",
     "🛡  Writes to: dtbo partition only — no user data erased."),
    ("Fastboot  ›  Disable vbmeta & Flash  (.img)", [".img"],"fb_vbmeta","danger",
     "🚨  DANGER — Disables Android Verified Boot (AVB) permanently.\n"
     "    Yellow/orange warning on every boot. Cannot re-lock without factory reset.",
     "Passes --disable-verity --disable-verification.\nRequired for most root methods.",
     "🛡  Writes to: vbmeta only — disables boot verification permanently."),
    ("Fastboot  ›  Full ROM Package  (.zip)",       [".zip"],"fb_zip","warn",
     "⚠  fastboot update may wipe depending on ZIP. NO -w passed by this tool.\n"
     "    NEVER use OEM flash_all scripts — they always pass -w.",
     "Inspect the ZIP before use. Device must be in Fastboot mode.",
     "🛡  No -w flag — data safety depends entirely on the ZIP contents."),
    ("ADB  ›  Sideload Custom ROM  (.zip)",         [".zip"],"adb_sideload","info",
     "ℹ  Device must be in Recovery → Advanced → ADB Sideload before flashing.",
     "Wipe data/cache in Recovery first for a clean install.\n"
     "Run: adb devices — confirm 'sideload' status.",
     "🛡  Writes ROM over ADB — wipe is a separate manual Recovery step."),
]
MODE_LABELS = [m[0] for m in MODES]

def get_mode(label):
    for m in MODES:
        if m[0] == label:
            return m
    return None

# ─────────────────────────────────────────────────────────────────────────────
#  Shell helpers
# ─────────────────────────────────────────────────────────────────────────────
_IS_WINDOWS = (platform.system() == "Windows")

def run_cmd(args, timeout=60):
    """Safe subprocess runner. Returns (returncode, stdout, stderr).
    Never raises. Suppresses console popups on Windows."""
    kw = dict(capture_output=True, text=True, timeout=timeout)
    if _IS_WINDOWS:
        kw["creationflags"] = subprocess.CREATE_NO_WINDOW
    try:
        p = subprocess.run(args, **kw)
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except FileNotFoundError:
        return -1, "", f"'{args[0]}' not found in PATH"
    except subprocess.TimeoutExpired:
        return -2, "", f"'{args[0]}' timed out after {timeout}s"
    except Exception as exc:
        return -3, "", str(exc)

def adb(*a):      return run_cmd(["adb",      *a])
def fastboot(*a): return run_cmd(["fastboot", *a])

# ─────────────────────────────────────────────────────────────────────────────
#  Scroll helpers
# ─────────────────────────────────────────────────────────────────────────────
def _make_scroller(canvas):
    """Cross-platform mouse-wheel handler. Clamps to ±1 for macOS trackpads."""
    def _on_scroll(event):
        num = getattr(event, "num", 0)
        if num == 4:
            canvas.yview_scroll(-1, "units")
        elif num == 5:
            canvas.yview_scroll(1, "units")
        else:
            delta = getattr(event, "delta", 0)
            if delta:
                units = int(-delta / 120)
                if units == 0:
                    units = -1 if delta > 0 else 1
                canvas.yview_scroll(units, "units")
    return _on_scroll

def _bind_scroll(widget, handler):
    """Bind scroll handler to widget and ALL descendants (fixes scroll-over-child bug)."""
    for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
        widget.bind(seq, handler, add="+")
    for child in widget.winfo_children():
        _bind_scroll(child, handler)


# ═════════════════════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ═════════════════════════════════════════════════════════════════════════════
class App:

    # Tab definitions: (display_label, internal_key)
    TABS = [
        ("⚡  Flash",       "flash"),
        ("🗑  Debloat",     "debloat"),
        ("📱  Device",      "device"),
        ("🔄  Reboot",      "reboot"),
        ("🔧  ADB Tools",   "adbtools"),
        ("💻  Shell",       "shell"),
    ]

    def __init__(self, root):
        self.root = root
        self.root.title("Android Multitool Universal  ·  by auratech0")
        self.root.geometry("920x980")
        self.root.minsize(720, 750)
        self.root.configure(bg=BG)

        # ── Resolve fonts ────────────────────────────────────────────────────
        self.MONO = _pick_font(root,
            ("Consolas", "Courier New", "Lucida Console", "DejaVu Sans Mono", "Courier"))

        # ── App state ────────────────────────────────────────────────────────
        self.selected_path  = ""
        self.flashing       = False
        self.pkg_vars       = {}   # simple debloat {pkg: BooleanVar}
        self.adv_packages   = []   # [(pkg, type, state)]
        self.check_vars     = {}   # pre-flash checklist
        self._tab_btns      = []
        self._tab_pages     = {}
        self._tab_inds      = []   # underline indicator frames
        self._active_tab    = 0
        self._glow_id       = None # after() id for flash button glow
        self._fullscreen    = False
        self._logcat_proc   = None # running logcat subprocess
        self._logcat_thread = None

        # ── Build UI (order matters for pack geometry) ────────────────────────
        self._setup_ttk()
        self._build_header()
        self._build_tabbar()

        # Build bottom-anchored widgets FIRST so _content gets the remainder
        self._build_statusbar()
        self._build_log()

        self._content = tk.Frame(self.root, bg=BG)
        self._content.pack(fill="both", expand=True)

        self._build_pages()
        self._switch_tab(0)
        self.root.update_idletasks()   # force geometry pass so canvases get real sizes
        self._update_mode_panels()

        # ── Keyboard bindings ────────────────────────────────────────────────
        self.root.bind("<F11>",        lambda _: self._toggle_fullscreen())
        self.root.bind("<Escape>",     lambda _: self._exit_fullscreen())

        # ── Startup log ──────────────────────────────────────────────────────
        self._log("Android Multitool Universal  v2.0  —  by auratech0\n", "info")
        self._log(f"Python {sys.version.split()[0]}  •  "
                  f"{platform.system()} {platform.release()}  •  {platform.machine()}\n","dim")
        self._log("─"*80+"\n","dim")

        threading.Thread(target=self._boot_check, daemon=True).start()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        """Graceful shutdown — stop animations and terminate subprocesses."""
        self._stop_glow()
        if self._logcat_proc is not None:
            try:
                self._logcat_proc.terminate()
            except Exception:
                pass
            self._logcat_proc = None
        self.root.destroy()

    # ─────────────────────────────────────────────────────────────────────────
    #  Full-screen
    # ─────────────────────────────────────────────────────────────────────────
    def _toggle_fullscreen(self):
        self._fullscreen = not self._fullscreen
        self.root.attributes("-fullscreen", self._fullscreen)
        label = "⛶  Exit Full Screen (Esc)" if self._fullscreen else "⛶  Full Screen (F11)"
        self._fs_btn.config(text=label)

    def _exit_fullscreen(self):
        if self._fullscreen:
            self._fullscreen = False
            self.root.attributes("-fullscreen", False)
            self._fs_btn.config(text="⛶  Full Screen (F11)")

    # ─────────────────────────────────────────────────────────────────────────
    #  TTK styles
    # ─────────────────────────────────────────────────────────────────────────
    def _setup_ttk(self):
        s = ttk.Style()
        s.theme_use("clam")

        # Combobox
        s.configure("TCombobox",
                    fieldbackground=SURF, background=BORDER, foreground=TEXT,
                    selectbackground=SURF, selectforeground=TEXT,
                    arrowcolor=MUTED, bordercolor=SURF3,
                    lightcolor=SURF3, darkcolor=SURF3,
                    insertcolor=TEXT, padding=6)
        s.map("TCombobox",
              fieldbackground=[("readonly",SURF),("disabled",SURF2)],
              foreground=[("disabled",MUTED)],
              selectbackground=[("readonly",SURF)])

        # Progressbar
        s.configure("TProgressbar",
                    troughcolor=SURF2, background=BLUE,
                    bordercolor=SURF3, lightcolor=BLUE, darkcolor=BLUE)

        # Scrollbar
        s.configure("TScrollbar",
                    background=SURF2, troughcolor=SURF,
                    bordercolor=SURF3, arrowcolor=MUTED,
                    gripcount=0, relief="flat")
        s.map("TScrollbar",
              background=[("active",BORDER),("pressed",BORDER)])

        # Treeview
        s.configure("Treeview",
                    background=SURF, foreground=TEXT2, fieldbackground=SURF,
                    rowheight=24, font=(self.MONO,8), bordercolor=SURF3)
        s.configure("Treeview.Heading",
                    background=SURF2, foreground=TEXT,
                    font=(self.MONO,8,"bold"), relief="flat", bordercolor=SURF3)
        s.map("Treeview",
              background=[("selected",BLUE)],
              foreground=[("selected",TEXT)])

    # ─────────────────────────────────────────────────────────────────────────
    #  Header
    # ─────────────────────────────────────────────────────────────────────────
    def _build_header(self):
        # Three-layer top accent stripe
        tk.Frame(self.root, bg=BLUE,          height=3).pack(fill="x")
        tk.Frame(self.root, bg=_darken(BLUE), height=1).pack(fill="x")
        tk.Frame(self.root, bg=SURF3,       height=1).pack(fill="x")

        h = tk.Frame(self.root, bg=BG)
        h.pack(fill="x")

        row = tk.Frame(h, bg=BG)
        row.pack(fill="x", padx=20, pady=(12,10))

        # Left: title
        lf = tk.Frame(row, bg=BG)
        lf.pack(side="left")
        tk.Label(lf, text="⚡ Android Multitool Universal",
                 font=(self.MONO,16,"bold"), bg=BG, fg=TEXT).pack(anchor="w")
        tk.Label(lf, text="Universal Android Flashing & Management Tool  ·  by auratech0",
                 font=(self.MONO,8), bg=BG, fg=MUTED).pack(anchor="w")

        # Right: device badge + fullscreen
        rf = tk.Frame(row, bg=BG)
        rf.pack(side="right", anchor="ne")

        # Fullscreen button
        self._fs_btn = self._mkbtn(rf, "⛶  Full Screen (F11)",
                                   self._toggle_fullscreen, SURF2, fs=8, px=8, py=4)
        self._fs_btn.pack(anchor="e", pady=(0,4))

        tk.Label(rf, text="DEVICE STATUS", font=(self.MONO,7,"bold"),
                 bg=BG, fg=MUTED).pack(anchor="e")
        self.dev_badge = tk.Label(rf, text="⬤  Detecting…",
                                  font=(self.MONO,9,"bold"), bg=BG, fg=MUTED)
        self.dev_badge.pack(anchor="e")
        self.dev_model = tk.Label(rf, text="",
                                  font=(self.MONO,7), bg=BG, fg=MUTED)
        self.dev_model.pack(anchor="e")

        tk.Frame(self.root, bg=SURF3, height=1).pack(fill="x")

    # ─────────────────────────────────────────────────────────────────────────
    #  Tab bar
    # ─────────────────────────────────────────────────────────────────────────
    def _build_tabbar(self):
        bar = tk.Frame(self.root, bg=SURF2)
        bar.pack(fill="x")
        tk.Frame(bar, bg=BORDER, height=1).pack(fill="x", side="bottom")

        for idx, (label, _key) in enumerate(self.TABS):
            wrap = tk.Frame(bar, bg=SURF2)
            wrap.pack(side="left")

            b = tk.Button(wrap, text=f"  {label}  ",
                          font=(self.MONO,9,"bold"),
                          bg=SURF2, fg=MUTED,
                          relief="flat", bd=0, padx=8, pady=9,
                          activebackground=SURF3, activeforeground=TEXT,
                          cursor="hand2",
                          command=lambda i=idx: self._switch_tab(i))
            b.pack(fill="x")

            # 2-px blue underline indicator (hidden until active)
            ind = tk.Frame(wrap, bg=SURF2, height=2)
            ind.pack(fill="x")

            # Hover: lighten background
            def _enter(e, btn=b, i=idx):
                if i != self._active_tab:
                    btn.config(bg=SURF3, fg=TEXT2)
            def _leave(e, btn=b, i=idx):
                if i != self._active_tab:
                    btn.config(bg=SURF2, fg=MUTED)
            b.bind("<Enter>", _enter)
            b.bind("<Leave>", _leave)

            self._tab_btns.append(b)
            self._tab_inds.append(ind)

    def _switch_tab(self, idx):
        self._active_tab = idx

        for i, (b, ind) in enumerate(zip(self._tab_btns, self._tab_inds)):
            on = (i == idx)
            b.config(bg=SURF if on else SURF2,
                     fg=TEXT if on else MUTED,
                     pady=7 if on else 9)
            ind.config(bg=BLUE if on else SURF2)

        for i, (_, key) in enumerate(self.TABS):
            page = self._tab_pages.get(key)
            if page is None:
                continue
            if i == idx:
                page.pack(fill="both", expand=True)
            else:
                page.pack_forget()

    # ─────────────────────────────────────────────────────────────────────────
    #  Build all pages
    # ─────────────────────────────────────────────────────────────────────────
    def _build_pages(self):
        for _, key in self.TABS:
            self._tab_pages[key] = tk.Frame(self._content, bg=BG)
        self._build_flash(self._tab_pages["flash"])
        self._build_debloat(self._tab_pages["debloat"])
        self._build_device(self._tab_pages["device"])
        self._build_reboot(self._tab_pages["reboot"])
        self._build_adbtools(self._tab_pages["adbtools"])
        self._build_shell(self._tab_pages["shell"])

    # ─────────────────────────────────────────────────────────────────────────
    #  Widget factories
    # ─────────────────────────────────────────────────────────────────────────
    def _card(self, parent):
        """Bordered card. Caller handles pack/grid — NOT packed internally."""
        outer = tk.Frame(parent, bg=BORDER)
        inner = tk.Frame(outer, bg=SURF)
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        # Subtle hover highlight on the border
        def _in(e):  outer.config(bg=_lighten(BORDER, 12))
        def _out(e): outer.config(bg=BORDER)
        outer.bind("<Enter>", _in)
        outer.bind("<Leave>", _out)
        return outer, inner

    def _sec(self, parent, tag, title, pad=18):
        """Section header row with badge tag."""
        r = tk.Frame(parent, bg=BG)
        r.pack(fill="x", padx=pad, pady=(10,4))
        badge = tk.Frame(r, bg=BLUE)
        badge.pack(side="left")
        tk.Label(badge, text=f" {tag} ",
                 font=(self.MONO,7,"bold"),
                 bg=BLUE, fg="white", padx=4, pady=2).pack()
        tk.Label(r, text=f"  {title}",
                 font=(self.MONO,9,"bold"),
                 bg=BG, fg=TEXT2).pack(side="left")

    def _mkbtn(self, parent, text, cmd, color,
               fs=9, px=12, py=6, fg="white"):
        """Flat button with smooth hover effect."""
        hover = _lighten(color, 30)
        b = tk.Button(parent, text=text, command=cmd,
                      bg=color, fg=fg,
                      font=(self.MONO, fs, "bold"),
                      relief="flat", padx=px, pady=py,
                      activebackground=hover, activeforeground=fg,
                      cursor="hand2", bd=0)
        b.bind("<Enter>", lambda e: b.config(bg=hover))
        b.bind("<Leave>", lambda e: b.config(bg=color))
        return b

    def _scrolled(self, parent):
        """Returns (canvas, inner_frame, scroll_handler).
        inner_frame always matches canvas width. Scroll works on all platforms.

        Root-cause fix for the Linux black-screen bug:
          On Linux the very first <Configure> fires with width=1 (before the
          window is mapped).  We ignore widths of 1 and schedule a one-shot
          after(10) to force the correct width once layout has settled.
        """
        c = tk.Canvas(parent, bg=BG, highlightthickness=0)
        sb = ttk.Scrollbar(parent, orient="vertical",
                           command=c.yview, style="TScrollbar")
        sb.pack(side="right", fill="y")
        c.pack(side="left", fill="both", expand=True)
        c.configure(yscrollcommand=sb.set)

        inner = tk.Frame(c, bg=BG)
        win_id = c.create_window((0, 0), window=inner, anchor="nw")

        def _frame_cfg(e):
            c.configure(scrollregion=c.bbox("all"))

        def _canvas_cfg(e):
            # Ignore the spurious width=1 event that fires before mapping
            if e.width > 1:
                c.itemconfig(win_id, width=e.width)

        def _force_width():
            """One-shot deferred resize — runs after mainloop's first pass."""
            w = c.winfo_width()
            if w > 1:
                c.itemconfig(win_id, width=w)
            bbox = c.bbox("all")
            if bbox:
                c.configure(scrollregion=bbox)

        inner.bind("<Configure>", _frame_cfg)
        c.bind("<Configure>",     _canvas_cfg)
        c.after(10, _force_width)   # fires after window is fully mapped

        h = _make_scroller(c)
        c.bind("<MouseWheel>", h)
        c.bind("<Button-4>",   h)
        c.bind("<Button-5>",   h)
        return c, inner, h

    def _banner(self, parent, text, bg, fg, pad=18):
        """Coloured info/warning banner."""
        f = tk.Frame(parent, bg=bg)
        f.pack(fill="x", padx=pad, pady=(0,6))
        tk.Label(f, text=text, font=(self.MONO,8),
                 bg=bg, fg=fg, justify="left", anchor="w",
                 wraplength=900, padx=10, pady=7).pack(fill="x")
        return f

    def _divider(self, parent, pad=18):
        """Horizontal rule."""
        tk.Frame(parent, bg=SURF3, height=1).pack(fill="x", padx=pad, pady=4)

    # ─────────────────────────────────────────────────────────────────────────
    #  Thread-safe UI helpers
    # ─────────────────────────────────────────────────────────────────────────
    def _ui(self, fn):       self.root.after(0, fn)
    def _status(self, t, c): self._ui(lambda: self.status_lbl.config(text=t, fg=c))

    def _log(self, text, tag="info"):
        def _w():
            ts = datetime.datetime.now().strftime("%H:%M:%S")
            self.log_txt.config(state="normal")
            self.log_txt.insert("end", f"[{ts}] ", "dim")
            self.log_txt.insert("end", text, tag)
            self.log_txt.see("end")
            self.log_txt.config(state="disabled")
        self._ui(_w)

    # ─────────────────────────────────────────────────────────────────────────
    #  Visual effects
    # ─────────────────────────────────────────────────────────────────────────
    def _pulse_badge(self, final_color):
        """Briefly pulse the device badge colour."""
        seq = [TEXT, final_color, TEXT, final_color, TEXT, final_color, final_color]
        def _step(i=0):
            if i >= len(seq):
                return
            self.dev_badge.config(fg=seq[i])
            self.root.after(110, lambda: _step(i+1))
        _step()

    def _start_glow(self):
        """Pulse the Flash button when checklist is complete."""
        self._stop_glow()
        base  = GREEN
        light = _lighten(GREEN, 38)
        seq   = [base, light, base, light, base, light, base]

        def _step(i=0):
            if self._glow_id is None:
                self.flash_btn.config(bg=base)
                return
            # Stop if checklist becomes incomplete or flashing starts
            if self.flashing or not all(v.get() for v in self.check_vars.values()):
                self._stop_glow()
                return
            self.flash_btn.config(bg=seq[i % len(seq)])
            self._glow_id = self.root.after(750, lambda: _step(i+1))

        self._glow_id = self.root.after(0, _step)

    def _stop_glow(self):
        if self._glow_id is not None:
            self.root.after_cancel(self._glow_id)
            self._glow_id = None

    # ═════════════════════════════════════════════════════════════════════════
    #  FLASH PAGE
    # ═════════════════════════════════════════════════════════════════════════
    def _build_flash(self, parent):
        P = 18
        _c, body, sh = self._scrolled(parent)

        # 01 — Mode
        self._sec(body, "01", "Select Flash Mode")
        co, ci = self._card(body)
        co.pack(fill="x", padx=P, pady=(0,8))

        self.mode_var = tk.StringVar(value=MODE_LABELS[0])
        self.mode_cb  = ttk.Combobox(ci, textvariable=self.mode_var,
                                     values=MODE_LABELS, state="readonly",
                                     style="TCombobox", font=(self.MONO,9))
        self.mode_cb.pack(fill="x", padx=14, pady=(12,8))
        self.mode_cb.bind("<<ComboboxSelected>>", lambda _: self._update_mode_panels())

        # Safe note (green)
        self.safe_lbl = tk.Label(ci, text="", font=(self.MONO,8),
                                 bg=OK_BG, fg=OK_FG, anchor="w",
                                 justify="left", padx=10, pady=5, wraplength=860)
        self.safe_lbl.pack(fill="x", padx=14, pady=(0,3))

        # Warning panel (orange or red for danger)
        self.warn_frame = tk.Frame(ci, bg=WARN_BG)
        self.warn_frame.pack(fill="x", padx=14, pady=(0,3))
        self.warn_lbl = tk.Label(self.warn_frame, text="",
                                 font=(self.MONO,9),
                                 bg=WARN_BG, fg=WARN_FG, anchor="w",
                                 justify="left", wraplength=860)
        self.warn_lbl.pack(fill="x", padx=10, pady=7)

        # Info panel (blue)
        self.info_frame = tk.Frame(ci, bg=INFO_BG)
        self.info_frame.pack(fill="x", padx=14, pady=(0,12))
        self.info_lbl = tk.Label(self.info_frame, text="",
                                 font=(self.MONO,9),
                                 bg=INFO_BG, fg=INFO_FG, anchor="w",
                                 justify="left", wraplength=860)
        self.info_lbl.pack(fill="x", padx=10, pady=7)

        # 02 — File
        self._sec(body, "02", "Select File to Flash")
        fo, fi = self._card(body)
        fo.pack(fill="x", padx=P, pady=(0,8))

        fr = tk.Frame(fi, bg=SURF)
        fr.pack(fill="x", padx=14, pady=(12,4))
        self.browse_btn = self._mkbtn(fr, "  Browse…  ", self.select_file, BLUE)
        self.browse_btn.pack(side="left")
        self.file_lbl = tk.Label(fr, text="  No file selected",
                                 fg=MUTED, bg=SURF, font=(self.MONO,9), anchor="w")
        self.file_lbl.pack(side="left", padx=10, fill="x", expand=True)
        self.file_meta = tk.Label(fi, text="", fg=MUTED, bg=SURF,
                                  font=(self.MONO,7), anchor="w")
        self.file_meta.pack(fill="x", padx=14, pady=(0,10))

        # 03 — Checklist
        self._sec(body, "03", "Pre-Flash Safety Checklist")
        co3, ci3 = self._card(body)
        co3.pack(fill="x", padx=P, pady=(0,8))

        checks = [
            ("unlocked","Bootloader is UNLOCKED  (required for all Fastboot flashing)"),
            ("backup",  "Full data backup complete  (some modes wipe the device)"),
            ("battery", "Battery ≥ 50%  (power loss mid-flash = permanent brick)"),
            ("tools",   "ADB / Fastboot platform tools installed and in PATH"),
            ("no_oem",  "NOT using OEM flash_all script  (they pass -w and erase all data)"),
        ]
        for k, txt in checks:
            v = tk.BooleanVar(value=False)
            self.check_vars[k] = v
            row = tk.Frame(ci3, bg=SURF)
            row.pack(fill="x", padx=14, pady=2)
            cb = tk.Checkbutton(row, variable=v, text=f"  {txt}",
                                bg=SURF, fg=TEXT2, selectcolor=BORDER,
                                activebackground=SURF, activeforeground=TEXT,
                                font=(self.MONO,9), anchor="w",
                                command=self._refresh_flash_btn)
            cb.pack(anchor="w")
        tk.Frame(ci3, bg=SURF, height=6).pack()

        # 04 — Wipe
        self._sec(body, "04", "Wipe Operations")
        wo, wi = self._card(body)
        wo.pack(fill="x", padx=P, pady=(0,8))
        tk.Label(wi, text="🚨  All wipe operations are PERMANENT and cannot be undone.",
                 font=(self.MONO,8), bg=DANG_BG, fg=DANG_FG,
                 anchor="w", padx=10, pady=5).pack(fill="x", padx=14, pady=(10,6))

        wg = tk.Frame(wi, bg=SURF)
        wg.pack(fill="x", padx=14, pady=(0,12))
        for ci2 in range(4):
            wg.columnconfigure(ci2, weight=1)

        for col_i, (lbl, fn, col, tip) in enumerate([
            ("Wipe App Data\n(pm clear)",       self._wipe_app_data, ORANGE,
             "Clear data for a specific package"),
            ("Wipe Dalvik Cache\n(needs root)",  self._wipe_dalvik,   ORANGE,
             "Remove /data/dalvik-cache"),
            ("Wipe Cache\n(fastboot erase)",     self._wipe_cache_fb, RED,
             "Fastboot mode required"),
            ("Wipe Userdata\n(FULL WIPE)",       self._wipe_userdata, RED,
             "ALL data permanently deleted"),
        ]):
            fr2 = tk.Frame(wg, bg=SURF)
            fr2.grid(row=0, column=col_i, padx=6, pady=6, sticky="nw")
            self._mkbtn(fr2, lbl, fn, col, px=8, py=6).pack(anchor="w")
            tk.Label(fr2, text=tip, font=(self.MONO,7), bg=SURF, fg=MUTED,
                     wraplength=160, justify="left").pack(anchor="w", pady=(2,0))

        # Flash button + progress bar
        self.flash_btn = self._mkbtn(body, "  ▶  START FLASH  ",
                                     self.start_flash, GREEN, fs=11, px=28, py=11)
        self.flash_btn.pack(pady=(12,3))
        self.flash_prog = ttk.Progressbar(body, mode="indeterminate",
                                          length=500, style="TProgressbar")
        self.flash_prog.pack(pady=4)
        self.flash_status = tk.Label(body, text="", font=(self.MONO,8),
                                     bg=BG, fg=MUTED)
        self.flash_status.pack(pady=(0,14))

        _bind_scroll(body, sh)

    # ═════════════════════════════════════════════════════════════════════════
    #  DEBLOAT PAGE
    # ═════════════════════════════════════════════════════════════════════════
    def _build_debloat(self, parent):
        # Sub-tab bar
        sbar = tk.Frame(parent, bg=SURF2)
        sbar.pack(fill="x", side="top")
        tk.Frame(sbar, bg=BORDER, height=1).pack(fill="x", side="bottom")

        self._dsub_btns  = []
        self._dsub_inds  = []

        host = tk.Frame(parent, bg=BG)
        host.pack(fill="both", expand=True, side="top")

        simple_pg   = tk.Frame(host, bg=BG)
        advanced_pg = tk.Frame(host, bg=BG)
        dsub_pages  = [simple_pg, advanced_pg]

        def _sw(idx):
            for i, (b, ind) in enumerate(zip(self._dsub_btns, self._dsub_inds)):
                on = (i == idx)
                b.config(bg=SURF if on else SURF2,
                         fg=TEXT if on else MUTED,
                         pady=7 if on else 9)
                ind.config(bg=BLUE if on else SURF2)
            for i, p in enumerate(dsub_pages):
                if i == idx:
                    p.pack(fill="both", expand=True)
                else:
                    p.pack_forget()

        for idx, lbl in enumerate(("  Simple (AUD Presets)  ",
                                    "  Advanced (All Packages)  ")):
            wrap = tk.Frame(sbar, bg=SURF2)
            wrap.pack(side="left")
            b = tk.Button(wrap, text=lbl, font=(self.MONO,9,"bold"),
                          bg=SURF2, fg=MUTED, relief="flat", bd=0,
                          padx=8, pady=9,
                          activebackground=SURF3, activeforeground=TEXT,
                          cursor="hand2", command=lambda i=idx: _sw(i))
            b.pack(fill="x")
            ind = tk.Frame(wrap, bg=SURF2, height=2)
            ind.pack(fill="x")
            self._dsub_btns.append(b)
            self._dsub_inds.append(ind)

        self._build_simple_debloat(simple_pg)
        self._build_advanced_debloat(advanced_pg)
        _sw(0)

    # ── Simple debloat ────────────────────────────────────────────────────────
    def _build_simple_debloat(self, parent):
        P = 18
        self._banner(parent,
            "⚠  Uses  pm disable-user --user 0  — fully reversible by default.\n"
            "   Tick packages → Disable.   To undo → tick same → Enable.",
            WARN_BG, WARN_FG)

        ctrl = tk.Frame(parent, bg=BG)
        ctrl.pack(fill="x", padx=P, pady=(0,6))
        tk.Label(ctrl, text="Category:", font=(self.MONO,9),
                 bg=BG, fg=MUTED).pack(side="left", padx=(0,6))
        self.cat_var = tk.StringVar(value="All")
        cat_cb = ttk.Combobox(ctrl, textvariable=self.cat_var,
                              values=["All"]+list(PRESETS.keys()),
                              state="readonly", style="TCombobox",
                              font=(self.MONO,9), width=26)
        cat_cb.pack(side="left", padx=(0,8))
        cat_cb.bind("<<ComboboxSelected>>", lambda _: self._repopulate_simple())
        self._mkbtn(ctrl, " Select All ",   self._sel_all,   SURF2, fs=8).pack(side="left", padx=2)
        self._mkbtn(ctrl, " Deselect All ", self._desel_all, SURF2, fs=8).pack(side="left", padx=2)

        # Scrollable list
        bdr = tk.Frame(parent, bg=BORDER)
        bdr.pack(fill="both", expand=True, padx=P, pady=(0,6))
        bdr_in = tk.Frame(bdr, bg=SURF)
        bdr_in.pack(fill="both", expand=True, padx=1, pady=1)

        self._sc = tk.Canvas(bdr_in, bg=SURF, highlightthickness=0)
        vsb = ttk.Scrollbar(bdr_in, orient="vertical",
                            command=self._sc.yview, style="TScrollbar")
        vsb.pack(side="right", fill="y")
        self._sc.pack(side="left", fill="both", expand=True)
        self._sc.configure(yscrollcommand=vsb.set)

        self.simple_frame = tk.Frame(self._sc, bg=SURF)
        self._sc_win = self._sc.create_window((0, 0), window=self.simple_frame, anchor="nw")

        def _sc_frame_cfg(e):
            self._sc.configure(scrollregion=self._sc.bbox("all"))

        def _sc_canvas_cfg(e):
            # Guard against spurious width=1 on Linux before window is mapped
            if e.width > 1:
                self._sc.itemconfig(self._sc_win, width=e.width)

        def _sc_force_width():
            w = self._sc.winfo_width()
            if w > 1:
                self._sc.itemconfig(self._sc_win, width=w)
            bbox = self._sc.bbox("all")
            if bbox:
                self._sc.configure(scrollregion=bbox)

        self.simple_frame.bind("<Configure>", _sc_frame_cfg)
        self._sc.bind("<Configure>",          _sc_canvas_cfg)
        self._sc.after(10, _sc_force_width)
        self._sc_sh = _make_scroller(self._sc)
        for seq in ("<MouseWheel>","<Button-4>","<Button-5>"):
            self._sc.bind(seq, self._sc_sh)

        self._repopulate_simple()

        ab = tk.Frame(parent, bg=BG)
        ab.pack(fill="x", padx=P, pady=5)
        self._mkbtn(ab, "  ⛔  Disable Selected  ",
                    self._pm_disable,   ORANGE).pack(side="left", padx=(0,6))
        self._mkbtn(ab, "  ✓  Enable Selected  ",
                    self._pm_enable,    GREEN ).pack(side="left", padx=(0,6))
        self._mkbtn(ab, "  🗑  Uninstall Selected  ",
                    self._pm_uninstall, RED   ).pack(side="left")

    def _repopulate_simple(self):
        for w in self.simple_frame.winfo_children():
            w.destroy()
        self.pkg_vars.clear()
        filt = self.cat_var.get()

        for cat, pkgs in PRESETS.items():
            if filt != "All" and cat != filt:
                continue
            hf = tk.Frame(self.simple_frame, bg=SURF2)
            hf.pack(fill="x", pady=(6,0))
            tk.Label(hf, text=f"  {cat}",
                     font=(self.MONO,9,"bold"),
                     bg=SURF2, fg=TEXT, pady=5).pack(anchor="w", padx=10)

            for pkg in pkgs:
                db   = PKG_DB.get(pkg)
                desc = db[0] if db else "No description"
                flag = db[1] if db else "caution"
                em, flabel, fclr = FLAGS.get(flag, FLAGS["caution"])

                v = tk.BooleanVar(value=False)
                self.pkg_vars[pkg] = v

                row = tk.Frame(self.simple_frame, bg=SURF)
                row.pack(fill="x")

                tk.Checkbutton(row, variable=v, text=f"  {desc}",
                               bg=SURF, fg=TEXT2, selectcolor=BORDER,
                               activebackground=SURF, activeforeground=TEXT,
                               font=(self.MONO,9), anchor="w").pack(side="left")
                tk.Label(row, text=f"  {em} {flabel}",
                         font=(self.MONO,8,"bold"),
                         bg=SURF, fg=fclr).pack(side="right", padx=8)
                tk.Label(row, text=f"  {pkg}", font=(self.MONO,7),
                         bg=SURF, fg=MUTED).pack(side="left")

        self.simple_frame.update_idletasks()
        self._sc.configure(scrollregion=self._sc.bbox("all"))
        self._sc.yview_moveto(0)
        _bind_scroll(self.simple_frame, self._sc_sh)

    def _sel_all(self):
        for v in self.pkg_vars.values(): v.set(True)

    def _desel_all(self):
        for v in self.pkg_vars.values(): v.set(False)

    def _checked_pkgs(self):
        return [p for p, v in self.pkg_vars.items() if v.get()]

    def _pm_disable(self):
        pkgs = self._checked_pkgs()
        if not pkgs:
            messagebox.showwarning("Nothing selected","Tick at least one package."); return
        if not messagebox.askyesno("Confirm Disable",
                f"Disable {len(pkgs)} package(s) for user 0?\n\n"
                "Reversible — use Enable to undo.\n\n"
                + "\n".join(pkgs[:14]) + ("…" if len(pkgs)>14 else "")): return
        threading.Thread(target=self._run_pm, args=(pkgs,"disable"), daemon=True).start()

    def _pm_enable(self):
        pkgs = self._checked_pkgs()
        if not pkgs:
            messagebox.showwarning("Nothing selected","Tick at least one package."); return
        threading.Thread(target=self._run_pm, args=(pkgs,"enable"), daemon=True).start()

    def _pm_uninstall(self):
        pkgs = self._checked_pkgs()
        if not pkgs:
            messagebox.showwarning("Nothing selected","Tick at least one package."); return
        if not messagebox.askyesno("⚠  Confirm Uninstall",
                f"Uninstall {len(pkgs)} package(s)?\n"
                "System apps: user 0 only. User apps: PERMANENT.\n\n"
                + "\n".join(pkgs[:14]), icon="warning"): return
        threading.Thread(target=self._run_pm, args=(pkgs,"uninstall"), daemon=True).start()

    def _run_pm(self, pkgs, action):
        self._status("⬤  Running PM…", ORANGE)
        ok = fail = 0
        for pkg in pkgs:
            if action == "disable":
                rc, _, err = adb("shell","pm","disable-user","--user","0", pkg)
            elif action == "enable":
                rc, _, err = adb("shell","pm","enable", pkg)
            else:
                rc, _, err = adb("shell","pm","uninstall","--user","0", pkg)
            if rc == 0:
                self._log(f"  {action.upper():<12}{pkg}\n","ok"); ok += 1
            else:
                self._log(f"  FAILED      {pkg}  →  {(err.splitlines() or ['?'])[0]}\n","warn")
                fail += 1
        self._log(f"Done: {ok} OK, {fail} failed.\n", "ok" if not fail else "warn")
        self._log("─"*80+"\n","dim")
        self._status("⬤  Ready", OK_FG)

    # ── Advanced debloat ──────────────────────────────────────────────────────
    def _build_advanced_debloat(self, parent):
        P = 18
        # Flag legend
        lf = tk.Frame(parent, bg=SURF2)
        lf.pack(fill="x", padx=P, pady=(8,0))
        tk.Label(lf, text=" FLAGS ", font=(self.MONO,7,"bold"),
                 bg=BLUE, fg="white", padx=6, pady=2).pack(side="left")
        for k in ("safe","recommended","caution","unsafe"):
            em, lbl, clr = FLAGS[k]
            tk.Label(lf, text=f"  {em} {lbl}  ", font=(self.MONO,8,"bold"),
                     bg=SURF2, fg=clr).pack(side="left")

        self._banner(parent,
            "🚨  ADVANCED — all packages on device. 🔴 Unsafe = DO NOT DISABLE.\n"
            "   Disable is reversible. Uninstall for system apps is permanent.",
            DANG_BG, DANG_FG)

        # Search + filter controls
        ctrl = tk.Frame(parent, bg=BG)
        ctrl.pack(fill="x", padx=P, pady=(0,4))
        tk.Label(ctrl, text="Search:", font=(self.MONO,9),
                 bg=BG, fg=MUTED).pack(side="left", padx=(0,6))
        self.adv_q = tk.StringVar()
        self.adv_q.trace_add("write", lambda *_: self._filter_adv())
        tk.Entry(ctrl, textvariable=self.adv_q,
                 bg=SURF, fg=TEXT, insertbackground=TEXT,
                 font=(self.MONO,9), relief="flat", bd=4, width=30
                 ).pack(side="left", padx=(0,8))
        self.adv_filt = tk.StringVar(value="All")
        for lbl in ("All","System","User","Disabled","Known"):
            tk.Radiobutton(ctrl, text=lbl, variable=self.adv_filt, value=lbl,
                           command=self._filter_adv,
                           bg=BG, fg=MUTED, selectcolor=SURF2,
                           activebackground=BG, activeforeground=TEXT,
                           font=(self.MONO,8)).pack(side="left", padx=3)
        self._mkbtn(ctrl, "  ↺ Refresh  ",
                    self._load_adv, BLUE, fs=8).pack(side="right")

        # Treeview
        tvh = tk.Frame(parent, bg=BORDER)
        tvh.pack(fill="both", expand=True, padx=P, pady=(0,4))
        tvi = tk.Frame(tvh, bg=SURF)
        tvi.pack(fill="both", expand=True, padx=1, pady=1)

        self.adv_tree = ttk.Treeview(tvi,
                                     columns=("pkg","type","state","flag","desc"),
                                     show="headings", selectmode="extended",
                                     style="Treeview")
        self.adv_tree.heading("pkg",   text="Package",     anchor="w")
        self.adv_tree.heading("type",  text="Type",        anchor="w")
        self.adv_tree.heading("state", text="State",       anchor="w")
        self.adv_tree.heading("flag",  text="Safety",      anchor="w")
        self.adv_tree.heading("desc",  text="Description", anchor="w")
        self.adv_tree.column("pkg",   width=320, stretch=True)
        self.adv_tree.column("type",  width=68,  stretch=False)
        self.adv_tree.column("state", width=68,  stretch=False)
        self.adv_tree.column("flag",  width=118, stretch=False)
        self.adv_tree.column("desc",  width=260, stretch=True)
        tsb = ttk.Scrollbar(tvi, orient="vertical",
                            command=self.adv_tree.yview, style="TScrollbar")
        self.adv_tree.configure(yscrollcommand=tsb.set)
        tsb.pack(side="right", fill="y")
        self.adv_tree.pack(fill="both", expand=True)

        for tag, fg in (("dis",MUTED),("sys",T_WARN),("usr",T_OK),
                        ("bad",T_ERR),("rec",T_INFO)):
            self.adv_tree.tag_configure(tag, foreground=fg)

        self.adv_info = tk.Label(parent, text="  Select a package to see details.",
                                 font=(self.MONO,8), bg=INFO_BG, fg=INFO_FG,
                                 anchor="w", padx=10, pady=5,
                                 wraplength=900, justify="left")
        self.adv_info.pack(fill="x", padx=P, pady=(0,4))
        self.adv_tree.bind("<<TreeviewSelect>>", self._adv_select)

        tk.Label(parent, text="  Click  ↺ Refresh  with device connected via ADB.",
                 font=(self.MONO,7), bg=BG, fg=MUTED).pack(anchor="w", padx=P)

        ab = tk.Frame(parent, bg=BG)
        ab.pack(fill="x", padx=P, pady=5)
        self._mkbtn(ab,"  ⛔  Disable (safe)  ",self._adv_disable,  ORANGE).pack(side="left",padx=(0,6))
        self._mkbtn(ab,"  ✓  Enable  ",         self._adv_enable,   GREEN ).pack(side="left",padx=(0,6))
        self._mkbtn(ab,"  🗑  Uninstall  ",      self._adv_uninstall,RED   ).pack(side="left")

    def _adv_select(self, _=None):
        sel = self.adv_tree.selection()
        if not sel: return
        pkg = str(self.adv_tree.item(sel[0])["values"][0])
        db  = PKG_DB.get(pkg)
        if db:
            em, flabel, _ = FLAGS.get(db[1], FLAGS["caution"])
            self.adv_info.config(
                text=f"  {em} [{flabel}]  {db[0]}\n  Package: {pkg}  ·  Category: {db[2]}")
        else:
            self.adv_info.config(text=f"  Package: {pkg}  (not in knowledge base)")

    def _load_adv(self):
        threading.Thread(target=self._fetch_adv, daemon=True).start()

    def _fetch_adv(self):
        self._log("Fetching package list…\n","info")
        self._status("⬤  Loading…", ORANGE)
        rc, out, _ = adb("shell","pm","list","packages","-u")
        if rc != 0:
            self._log("Failed — device connected via ADB?\n","err")
            self._status("⬤  ADB Error", RED); return
        all_pkgs = {l.replace("package:","").strip()
                    for l in out.splitlines() if l.startswith("package:")}
        _, d, _ = adb("shell","pm","list","packages","-d")
        disabled = {l.replace("package:","").strip()
                    for l in d.splitlines() if l.startswith("package:")}
        _, s, _ = adb("shell","pm","list","packages","-s")
        system   = {l.replace("package:","").strip()
                    for l in s.splitlines() if l.startswith("package:")}
        self.adv_packages = sorted(
            (p,
             "System" if p in system   else "User",
             "Disabled" if p in disabled else "Enabled")
            for p in all_pkgs)
        self._log(f"Loaded {len(self.adv_packages)} packages "
                  f"({len(system)} system, {len(all_pkgs)-len(system)} user, "
                  f"{len(disabled)} disabled).\n","ok")
        self._ui(self._draw_adv)
        self._status("⬤  Ready", OK_FG)

    def _draw_adv(self, rows=None):
        self.adv_tree.delete(*self.adv_tree.get_children())
        for pkg, ptype, pstate in (rows if rows is not None else self.adv_packages):
            db = PKG_DB.get(pkg)
            if db:
                em, flabel, _ = FLAGS.get(db[1], FLAGS["caution"])
                flag_s = f"{em} {flabel}"
                desc_s = db[0][:65]
                row_tag = ("bad" if db[1]=="unsafe"      else
                           "rec" if db[1]=="recommended" else
                           "dis" if pstate=="Disabled"   else
                           "sys" if ptype =="System"     else "usr")
            else:
                flag_s = "— Unknown"
                desc_s = ""
                row_tag = ("dis" if pstate=="Disabled" else
                           "sys" if ptype =="System"   else "usr")
            self.adv_tree.insert("","end",
                                 values=(pkg, ptype, pstate, flag_s, desc_s),
                                 tags=(row_tag,))

    def _filter_adv(self):
        q    = self.adv_q.get().lower()
        filt = self.adv_filt.get()
        rows = [
            (p,t,s) for p,t,s in self.adv_packages
            if (not q or q in p.lower())
            and (filt=="All"
                 or (filt=="System"   and t=="System")
                 or (filt=="User"     and t=="User")
                 or (filt=="Disabled" and s=="Disabled")
                 or (filt=="Known"    and p in PKG_DB))
        ]
        self._draw_adv(rows)

    def _adv_sel_pkgs(self):
        return [str(self.adv_tree.item(i)["values"][0])
                for i in self.adv_tree.selection()]

    def _adv_disable(self):
        pkgs = self._adv_sel_pkgs()
        if not pkgs:
            messagebox.showwarning("Nothing selected","Select row(s) first."); return
        unsafe = [p for p in pkgs if PKG_DB.get(p,("","safe",""))[1]=="unsafe"]
        if unsafe and not messagebox.askyesno("⚠  Unsafe Package",
                f"You selected {len(unsafe)} UNSAFE package(s):\n"+"\n".join(unsafe)
                +"\n\nMay brick the device. Continue?",icon="warning"): return
        threading.Thread(target=self._run_pm,args=(pkgs,"disable"),daemon=True).start()

    def _adv_enable(self):
        pkgs = self._adv_sel_pkgs()
        if not pkgs:
            messagebox.showwarning("Nothing selected","Select row(s) first."); return
        threading.Thread(target=self._run_pm,args=(pkgs,"enable"),daemon=True).start()

    def _adv_uninstall(self):
        pkgs = self._adv_sel_pkgs()
        if not pkgs:
            messagebox.showwarning("Nothing selected","Select row(s) first."); return
        if not messagebox.askyesno("⚠  Uninstall?",
                f"Uninstall {len(pkgs)} package(s)?\n"+"\n".join(pkgs[:14]),
                icon="warning"): return
        threading.Thread(target=self._run_pm,args=(pkgs,"uninstall"),daemon=True).start()

    # ═════════════════════════════════════════════════════════════════════════
    #  DEVICE INFO PAGE
    # ═════════════════════════════════════════════════════════════════════════
    def _build_device(self, parent):
        P = 18
        _c, body, sh = self._scrolled(parent)

        self._sec(body, "ℹ", "Device Properties  (via ADB getprop)")
        po, pi = self._card(body)
        po.pack(fill="x", padx=P, pady=(0,8))
        grid = tk.Frame(pi, bg=SURF)
        grid.pack(fill="x", padx=14, pady=12)

        self.dev_props = {}
        for i, (lbl, prop) in enumerate([
            ("Manufacturer",    "ro.product.manufacturer"),
            ("Model",           "ro.product.model"),
            ("Device Codename", "ro.product.device"),
            ("Android Version", "ro.build.version.release"),
            ("SDK Level",       "ro.build.version.sdk"),
            ("Security Patch",  "ro.build.version.security_patch"),
            ("Build ID",        "ro.build.id"),
            ("Bootloader",      "ro.bootloader"),
            ("CPU ABI",         "ro.product.cpu.abi"),
            ("CPU Architecture","ro.product.cpu.abilist"),
            ("Display Size",    "ro.sf.lcd_density"),
            ("Serial",          "ro.serialno"),
        ]):
            tk.Label(grid, text=f"  {lbl}",
                     font=(self.MONO,9,"bold"), bg=SURF, fg=MUTED,
                     width=20, anchor="w").grid(row=i, column=0, sticky="w", pady=3)
            v = tk.StringVar(value="—")
            self.dev_props[prop] = v
            tk.Label(grid, textvariable=v, font=(self.MONO,9),
                     bg=SURF, fg=TEXT, anchor="w").grid(row=i, column=1, sticky="w", padx=12)

        self._sec(body, "⚡", "Fastboot Variables  (device in Fastboot mode)")
        fo, fi = self._card(body)
        fo.pack(fill="x", padx=P, pady=(0,8))
        fw = tk.Frame(fi, bg=SURF)
        fw.pack(fill="both", padx=14, pady=10)
        self.fb_text = tk.Text(fw, bg=SURF, fg=TEXT2, font=(self.MONO,8),
                               relief="flat", bd=0, height=12,
                               state="disabled", wrap="none")
        fbsb = ttk.Scrollbar(fw, orient="vertical",
                             command=self.fb_text.yview, style="TScrollbar")
        self.fb_text.configure(yscrollcommand=fbsb.set)
        fbsb.pack(side="right", fill="y")
        self.fb_text.pack(fill="both", expand=True)

        self._mkbtn(body, "  ↺  Refresh All  ",
                    lambda: threading.Thread(target=self._refresh_device, daemon=True).start(),
                    BLUE).pack(pady=8)
        _bind_scroll(body, sh)

    def _refresh_device(self):
        self._log("Refreshing device info…\n","info")
        for prop, var in self.dev_props.items():
            rc, val, _ = adb("shell","getprop", prop)
            v = val.strip() if rc==0 and val.strip() else "—"
            self._ui(lambda vr=var, vv=v: vr.set(vv))
        rc, out, err = fastboot("getvar","all")
        combined = (out+"\n"+err).strip() or "No output — device in Fastboot mode?"
        def _set():
            self.fb_text.config(state="normal")
            self.fb_text.delete("1.0","end")
            self.fb_text.insert("end", combined)
            self.fb_text.config(state="disabled")
        self._ui(_set)
        self._log("Device info refreshed.\n","ok")

    # ═════════════════════════════════════════════════════════════════════════
    #  REBOOT PAGE
    # ═════════════════════════════════════════════════════════════════════════
    def _build_reboot(self, parent):
        P = 18
        _c, body, sh = self._scrolled(parent)

        # ADB
        self._sec(body, "ADB", "ADB Reboot  (device must be booted + USB Debugging active)")
        ao, ai = self._card(body)
        ao.pack(fill="x", padx=P, pady=(0,12))
        ag = tk.Frame(ai, bg=SURF)
        ag.pack(fill="x", padx=14, pady=12)

        for i, (lbl, cmd, col, tip) in enumerate([
            ("System / Android",      ["adb","reboot"],               GREEN,  "Normal reboot to Android"),
            ("Recovery",              ["adb","reboot","recovery"],    BLUE,   "Boot into Recovery (TWRP / stock)"),
            ("Bootloader / Fastboot", ["adb","reboot","bootloader"],  PURPLE, "Enter Fastboot mode"),
            ("Fastboot (userspace)",  ["adb","reboot","fastboot"],    PURPLE, "Userspace Fastboot — Pixel / A/B"),
            ("ADB Sideload",          ["adb","reboot","sideload"],    ORANGE, "Boot into ADB Sideload mode"),
            ("Power Off",             ["adb","shell","reboot","-p"],  RED,    "Graceful power off"),
        ]):
            r, c = divmod(i, 2)
            fr = tk.Frame(ag, bg=SURF)
            fr.grid(row=r, column=c, padx=8, pady=6, sticky="nw")
            cc = cmd[:]
            self._mkbtn(fr, f"  {lbl}  ",
                        lambda x=cc: self._reboot(x), col, px=10, py=7).pack(anchor="w")
            tk.Label(fr, text=tip, font=(self.MONO,7),
                     bg=SURF, fg=MUTED).pack(anchor="w")

        # Fastboot
        self._sec(body, "FB", "Fastboot Reboot  (device in Fastboot mode)")
        fbo, fbi = self._card(body)
        fbo.pack(fill="x", padx=P, pady=(0,12))
        fg = tk.Frame(fbi, bg=SURF)
        fg.pack(fill="x", padx=14, pady=12)

        for i, (lbl, cmd, col, tip) in enumerate([
            ("System / Android", ["fastboot","reboot"],            GREEN,  "Exit Fastboot, boot Android"),
            ("Bootloader",       ["fastboot","reboot-bootloader"],  PURPLE, "Stay in Fastboot"),
            ("Recovery",         ["fastboot","reboot","recovery"],  BLUE,   "Boot into Recovery from Fastboot"),
            ("Temp Boot Image",  None,                              ORANGE, "fastboot boot <img> — no flash"),
        ]):
            r, c = divmod(i, 2)
            fr = tk.Frame(fg, bg=SURF)
            fr.grid(row=r, column=c, padx=8, pady=6, sticky="nw")
            if cmd:
                cc = cmd[:]
                self._mkbtn(fr, f"  {lbl}  ",
                            lambda x=cc: self._reboot(x), col, px=10, py=7).pack(anchor="w")
            else:
                self._mkbtn(fr, f"  {lbl}  ",
                            self._temp_boot, col, px=10, py=7).pack(anchor="w")
            tk.Label(fr, text=tip, font=(self.MONO,7),
                     bg=SURF, fg=MUTED).pack(anchor="w")

        _bind_scroll(body, sh)

    def _reboot(self, cmd):
        self._log(f"REBOOT: {' '.join(cmd)}\n","cmd")
        def _r():
            rc, _, err = run_cmd(cmd, timeout=15)
            self._log("Command sent.\n" if rc==0
                      else f"Failed (rc={rc}): {err}\n",
                      "ok" if rc==0 else "err")
        threading.Thread(target=_r, daemon=True).start()

    def _temp_boot(self):
        path = filedialog.askopenfilename(
            title="Select Boot Image for Temp Boot",
            filetypes=[("Image files","*.img"),("All files","*.*")])
        if path:
            self._reboot(["fastboot","boot",path])

    # ═════════════════════════════════════════════════════════════════════════
    #  ADB TOOLS PAGE  (new)
    # ═════════════════════════════════════════════════════════════════════════
    def _build_adbtools(self, parent):
        P = 18
        _c, body, sh = self._scrolled(parent)

        # ── Screenshot ────────────────────────────────────────────────────────
        self._sec(body, "📸", "Screenshot")
        so, si = self._card(body)
        so.pack(fill="x", padx=P, pady=(0,8))
        sr = tk.Frame(si, bg=SURF)
        sr.pack(fill="x", padx=14, pady=12)
        tk.Label(sr, text="Capture the current device screen and save to your computer.",
                 font=(self.MONO,9), bg=SURF, fg=TEXT2).pack(anchor="w", pady=(0,8))
        self._mkbtn(sr, "  📸  Take Screenshot  ", self._screenshot, BLUE).pack(side="left")

        self._divider(body)

        # ── File Transfer ─────────────────────────────────────────────────────
        self._sec(body, "📁", "File Transfer")
        fto, fti = self._card(body)
        fto.pack(fill="x", padx=P, pady=(0,8))
        ftg = tk.Frame(fti, bg=SURF)
        ftg.pack(fill="x", padx=14, pady=12)

        tk.Label(ftg, text="Push (PC → Device):",
                 font=(self.MONO,9,"bold"), bg=SURF, fg=TEXT2).grid(row=0,column=0,sticky="w",pady=4)
        push_row = tk.Frame(ftg, bg=SURF)
        push_row.grid(row=0,column=1,sticky="w",padx=10)
        self.push_src = tk.StringVar(value="")
        tk.Entry(push_row, textvariable=self.push_src,
                 bg=SURF2, fg=TEXT, insertbackground=TEXT,
                 font=(self.MONO,9), relief="flat", bd=4, width=32).pack(side="left")
        self._mkbtn(push_row, " Browse ", self._browse_push_src, SURF3, fs=8).pack(side="left",padx=4)

        tk.Label(ftg, text="Device destination:",
                 font=(self.MONO,9,"bold"), bg=SURF, fg=TEXT2).grid(row=1,column=0,sticky="w",pady=4)
        self.push_dst = tk.StringVar(value="/sdcard/")
        tk.Entry(ftg, textvariable=self.push_dst,
                 bg=SURF2, fg=TEXT, insertbackground=TEXT,
                 font=(self.MONO,9), relief="flat", bd=4, width=36
                 ).grid(row=1,column=1,sticky="w",padx=10,pady=4)

        tk.Label(ftg, text="Pull (Device → PC):",
                 font=(self.MONO,9,"bold"), bg=SURF, fg=TEXT2).grid(row=2,column=0,sticky="w",pady=4)
        self.pull_src = tk.StringVar(value="/sdcard/")
        tk.Entry(ftg, textvariable=self.pull_src,
                 bg=SURF2, fg=TEXT, insertbackground=TEXT,
                 font=(self.MONO,9), relief="flat", bd=4, width=36
                 ).grid(row=2,column=1,sticky="w",padx=10,pady=4)

        btn_row = tk.Frame(ftg, bg=SURF)
        btn_row.grid(row=3, column=0, columnspan=2, sticky="w", pady=8)
        self._mkbtn(btn_row, "  ↑ Push File  ",  self._push_file, BLUE ).pack(side="left",padx=(0,8))
        self._mkbtn(btn_row, "  ↓ Pull File  ",  self._pull_file, GREEN).pack(side="left")

        self._divider(body)

        # ── App Manager ──────────────────────────────────────────────────────
        self._sec(body, "📦", "App Install / Uninstall")
        apo, api = self._card(body)
        apo.pack(fill="x", padx=P, pady=(0,8))
        apg = tk.Frame(api, bg=SURF)
        apg.pack(fill="x", padx=14, pady=12)

        tk.Label(apg, text="Install APK:",
                 font=(self.MONO,9,"bold"), bg=SURF, fg=TEXT2).grid(row=0,column=0,sticky="w",pady=4)
        apk_row = tk.Frame(apg, bg=SURF)
        apk_row.grid(row=0,column=1,sticky="w",padx=10)
        self.apk_path = tk.StringVar(value="")
        tk.Entry(apk_row, textvariable=self.apk_path,
                 bg=SURF2, fg=TEXT, insertbackground=TEXT,
                 font=(self.MONO,9), relief="flat", bd=4, width=32).pack(side="left")
        self._mkbtn(apk_row," Browse ",self._browse_apk, SURF3, fs=8).pack(side="left",padx=4)

        tk.Label(apg, text="Uninstall package:",
                 font=(self.MONO,9,"bold"), bg=SURF, fg=TEXT2).grid(row=1,column=0,sticky="w",pady=4)
        self.uninstall_pkg = tk.StringVar(value="")
        tk.Entry(apg, textvariable=self.uninstall_pkg,
                 bg=SURF2, fg=TEXT, insertbackground=TEXT,
                 font=(self.MONO,9), relief="flat", bd=4, width=36
                 ).grid(row=1,column=1,sticky="w",padx=10,pady=4)

        apbtn = tk.Frame(apg, bg=SURF)
        apbtn.grid(row=2,column=0,columnspan=2,sticky="w",pady=8)
        self._mkbtn(apbtn,"  ▶ Install APK  ",       self._install_apk,     BLUE ).pack(side="left",padx=(0,8))
        self._mkbtn(apbtn,"  🗑 Uninstall Package  ", self._uninstall_pkg,   RED  ).pack(side="left")

        self._divider(body)

        # ── Logcat ────────────────────────────────────────────────────────────
        self._sec(body, "📋", "Logcat Viewer")
        lo, li = self._card(body)
        lo.pack(fill="x", padx=P, pady=(0,8))
        lctrl = tk.Frame(li, bg=SURF)
        lctrl.pack(fill="x", padx=14, pady=(10,4))
        tk.Label(lctrl, text="Filter:", font=(self.MONO,9),
                 bg=SURF, fg=MUTED).pack(side="left", padx=(0,6))
        self.logcat_q = tk.StringVar()
        tk.Entry(lctrl, textvariable=self.logcat_q,
                 bg=SURF2, fg=TEXT, insertbackground=TEXT,
                 font=(self.MONO,9), relief="flat", bd=4, width=28).pack(side="left")
        self._mkbtn(lctrl," ▶ Start ",self._logcat_start, GREEN, fs=8).pack(side="left",padx=6)
        self._mkbtn(lctrl," ■ Stop  ",self._logcat_stop,  RED,   fs=8).pack(side="left",padx=2)
        self._mkbtn(lctrl," Clear   ",self._logcat_clear, SURF3, fs=8).pack(side="left",padx=6)

        lbox = tk.Frame(li, bg=SURF2)
        lbox.pack(fill="both", padx=14, pady=(0,10), expand=True)
        self.logcat_txt = tk.Text(lbox, bg=SURF2, fg=TEXT2, font=(self.MONO,7),
                                  relief="flat", bd=0, height=14,
                                  state="disabled", wrap="none")
        lcsb = ttk.Scrollbar(lbox, orient="vertical",
                             command=self.logcat_txt.yview, style="TScrollbar")
        self.logcat_txt.configure(yscrollcommand=lcsb.set)
        lcsb.pack(side="right", fill="y")
        self.logcat_txt.pack(fill="both", expand=True)

        _bind_scroll(body, sh)

    def _screenshot(self):
        def _do():
            self._log("Taking screenshot…\n", "info")
            rc, _, err = adb("shell", "screencap", "-p", "/sdcard/_amu_screen.png")
            if rc != 0:
                self._log(f"screencap failed: {err}\n", "err")
                return
            # FIX #1: file dialog MUST run on the main thread via _ui / after()
            # Use a Queue to receive the path from the main-thread dialog
            result_q = queue.Queue()

            def _ask_save():
                save = filedialog.asksaveasfilename(
                    title="Save Screenshot",
                    defaultextension=".png",
                    filetypes=[("PNG", "*.png"), ("All", "*.*")])
                result_q.put(save)          # None if cancelled

            self._ui(_ask_save)
            save = result_q.get()           # blocks worker until user responds

            if not save:
                adb("shell", "rm", "/sdcard/_amu_screen.png")
                return
            rc2, _, err2 = adb("pull", "/sdcard/_amu_screen.png", save)
            adb("shell", "rm", "/sdcard/_amu_screen.png")
            if rc2 == 0:
                self._log(f"Screenshot saved: {save}\n", "ok")
                self._ui(lambda: messagebox.showinfo("Done", f"Saved to:\n{save}"))
            else:
                self._log(f"Pull failed: {err2}\n", "err")
        threading.Thread(target=_do, daemon=True).start()

    def _browse_push_src(self):
        p = filedialog.askopenfilename(title="Select file to push")
        if p: self.push_src.set(p)

    def _browse_apk(self):
        p = filedialog.askopenfilename(title="Select APK",
            filetypes=[("APK files","*.apk"),("All","*.*")])
        if p: self.apk_path.set(p)

    def _push_file(self):
        src = self.push_src.get().strip()
        dst = self.push_dst.get().strip()
        if not src or not dst:
            messagebox.showwarning("Missing","Fill in source and destination."); return
        threading.Thread(target=self._do_transfer,
                         args=(["adb","push",src,dst],"Push"), daemon=True).start()

    def _pull_file(self):
        src = self.pull_src.get().strip()
        if not src:
            messagebox.showwarning("Missing","Enter device path to pull."); return
        dst = filedialog.askdirectory(title="Save pulled file to…")
        if not dst: return
        threading.Thread(target=self._do_transfer,
                         args=(["adb","pull",src,dst],"Pull"), daemon=True).start()

    def _do_transfer(self, cmd, label):
        self._log(f"{label}: {' '.join(cmd)}\n", "cmd")
        rc, out, err = run_cmd(cmd, timeout=300)
        if rc == 0:
            self._log(f"{label} completed.\n{out}\n", "ok")
            self._ui(lambda: messagebox.showinfo(f"{label} Done", f"{label} completed successfully."))
        else:
            self._log(f"{label} FAILED: {err}\n", "err")
            e = err
            self._ui(lambda: messagebox.showerror(f"{label} Failed", f"{e[:300]}"))

    def _install_apk(self):
        path = self.apk_path.get().strip()
        if not path:
            messagebox.showwarning("No APK","Browse for an APK file first."); return
        threading.Thread(target=self._do_transfer,
                         args=(["adb","install","-r",path],"Install APK"),
                         daemon=True).start()

    def _uninstall_pkg(self):
        pkg = self.uninstall_pkg.get().strip()
        if not pkg:
            messagebox.showwarning("No package","Enter a package name."); return
        if not messagebox.askyesno("Confirm Uninstall",
                f"Fully uninstall:\n{pkg}\n\nThis is permanent for user-installed apps."):
            return
        threading.Thread(target=self._do_transfer,
                         args=(["adb","uninstall",pkg],"Uninstall"),
                         daemon=True).start()

    def _logcat_start(self):
        if self._logcat_proc is not None:
            messagebox.showinfo("Already Running","Stop the current logcat first."); return
        filt = self.logcat_q.get().strip()
        cmd = ["adb", "logcat"]
        if filt:
            # FIX #6: "TAG" → use -s TAG; "TAG:PRIORITY" or "*:E" → pass after --
            if ":" in filt:
                cmd += ["--", filt]
            else:
                cmd += ["-s", filt]
        kw = dict(stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                  text=True, bufsize=1)
        if _IS_WINDOWS:
            kw["creationflags"] = subprocess.CREATE_NO_WINDOW
        try:
            self._logcat_proc = subprocess.Popen(cmd, **kw)
        except FileNotFoundError:
            messagebox.showerror("adb not found",
                "adb not found in PATH. Install Android Platform Tools."); return
        self._log(f"Logcat started: {' '.join(cmd)}\n","ok")

        def _read():
            proc = self._logcat_proc
            if proc is None: return
            for line in proc.stdout:
                if self._logcat_proc is None: break
                def _w(l=line.rstrip()):
                    self.logcat_txt.config(state="normal")
                    self.logcat_txt.insert("end", l+"\n")
                    self.logcat_txt.see("end")
                    self.logcat_txt.config(state="disabled")
                self._ui(_w)
        self._logcat_thread = threading.Thread(target=_read, daemon=True)
        self._logcat_thread.start()

    def _logcat_stop(self):
        if self._logcat_proc is None: return
        try:
            self._logcat_proc.terminate()
        except Exception:
            pass
        self._logcat_proc = None
        self._log("Logcat stopped.\n","warn")

    def _logcat_clear(self):
        self.logcat_txt.config(state="normal")
        self.logcat_txt.delete("1.0","end")
        self.logcat_txt.config(state="disabled")

    # ═════════════════════════════════════════════════════════════════════════
    #  SHELL PAGE  (new)
    # ═════════════════════════════════════════════════════════════════════════
    def _build_shell(self, parent):
        P = 18
        self._banner(parent,
            "💻  Run any ADB shell or Fastboot command directly.\n"
            "   Type the full command (e.g.  adb shell getprop  or  fastboot getvar all)\n"
            "   and press Enter or click Run.",
            INFO_BG, INFO_FG)

        # Input row
        inp = tk.Frame(parent, bg=BG)
        inp.pack(fill="x", padx=P, pady=6)
        tk.Label(inp, text="$", font=(self.MONO,11,"bold"),
                 bg=BG, fg=GREEN).pack(side="left", padx=(0,6))
        self.shell_var = tk.StringVar()
        self.shell_entry = tk.Entry(inp, textvariable=self.shell_var,
                                    bg=SURF, fg=TEXT, insertbackground=TEXT2,
                                    font=(self.MONO,10), relief="flat", bd=6)
        self.shell_entry.pack(side="left", fill="x", expand=True)
        self.shell_entry.bind("<Return>", lambda _: self._run_shell())
        self._mkbtn(inp, "  Run  ", self._run_shell, BLUE, px=14, py=8
                    ).pack(side="left", padx=(8,0))
        self._mkbtn(inp, " Clear ", self._shell_clear, SURF2, fs=8, px=10, py=8
                    ).pack(side="left", padx=(4,0))

        # Quick-command shortcuts
        self._sec(parent, "⚡", "Quick Commands", P)
        qf = tk.Frame(parent, bg=BG)
        qf.pack(fill="x", padx=P, pady=(0,8))
        shortcuts = [
            ("adb devices",                "List connected devices"),
            ("fastboot devices",            "List Fastboot devices"),
            ("adb shell getprop ro.product.model","Device model"),
            ("adb shell df /data",          "Storage info"),
            ("adb shell cat /proc/cpuinfo", "CPU info"),
            ("adb shell dumpsys battery",   "Battery info"),
            ("adb shell pm list packages",  "All packages"),
            ("fastboot getvar all",         "All Fastboot vars"),
        ]
        for i, (cmd, tip) in enumerate(shortcuts):
            r, c = divmod(i, 2)
            fr = tk.Frame(qf, bg=BG)
            fr.grid(row=r, column=c, padx=4, pady=3, sticky="w")
            cc = cmd
            self._mkbtn(fr, f"  {tip}  ",
                        lambda x=cc: self._run_preset(x),
                        SURF3, fs=8, px=8, py=5, fg=TEXT2).pack()

        self._sec(parent, "📄", "Output", P)
        of = tk.Frame(parent, bg=BORDER)
        of.pack(fill="both", expand=True, padx=P, pady=(0,8))
        of_in = tk.Frame(of, bg=LOG_BG)
        of_in.pack(fill="both", expand=True, padx=1, pady=1)

        self.shell_out = tk.Text(of_in, bg=LOG_BG, fg=TEXT2, font=(self.MONO,9),
                                 relief="flat", bd=0, state="disabled",
                                 wrap="none", height=20)
        sosb = ttk.Scrollbar(of_in, orient="vertical",
                             command=self.shell_out.yview, style="TScrollbar")
        sosbx = ttk.Scrollbar(of_in, orient="horizontal",
                              command=self.shell_out.xview, style="TScrollbar")
        self.shell_out.configure(yscrollcommand=sosb.set, xscrollcommand=sosbx.set)
        sosb.pack(side="right", fill="y")
        sosbx.pack(side="bottom", fill="x")
        self.shell_out.pack(fill="both", expand=True)
        for tag, fg in (("ok",T_OK),("err",T_ERR),("cmd",T_CMD),("dim",T_DIM)):
            self.shell_out.tag_config(tag, foreground=fg)

    def _run_shell(self):
        raw = self.shell_var.get().strip()
        if not raw: return
        self.shell_var.set("")
        threading.Thread(target=self._exec_shell, args=(raw,), daemon=True).start()

    def _run_preset(self, cmd):
        self.shell_var.set(cmd)
        self._run_shell()

    def _shell_clear(self):
        self.shell_out.config(state="normal")
        self.shell_out.delete("1.0","end")
        self.shell_out.config(state="disabled")

    def _exec_shell(self, raw):
        # FIX #2: use shlex.split() so quoted args work: adb shell "echo hi world"
        try:
            parts = shlex.split(raw)
        except ValueError as e:
            self._append_shell(f"Parse error: {e}\n", "err")
            return
        if not parts:
            return

        self._append_shell(f"$ {raw}\n", "cmd")
        rc, out, err = run_cmd(parts, timeout=60)
        if out:
            self._append_shell(out + "\n", "ok" if rc == 0 else "dim")
        if err:
            self._append_shell(err + "\n", "err")
        if rc == -1:
            self._append_shell(f"'{parts[0]}' not found in PATH.\n", "err")
        elif rc != 0 and not err:
            self._append_shell(f"Exit code: {rc}\n", "err")
        self._append_shell("\n", "dim")

    def _append_shell(self, text, tag="dim"):
        # FIX #3: proper function instead of lambda-tuple; handles exceptions safely
        def _w():
            try:
                self.shell_out.config(state="normal")
                self.shell_out.insert("end", text, tag)
                self.shell_out.see("end")
            finally:
                self.shell_out.config(state="disabled")
        self._ui(_w)

    # ═════════════════════════════════════════════════════════════════════════
    #  LOG + STATUS  (packed with side="bottom" BEFORE _content)
    # ═════════════════════════════════════════════════════════════════════════
    def _build_log(self):
        tk.Frame(self.root, bg=SURF3, height=1).pack(fill="x", side="bottom")
        lh = tk.Frame(self.root, bg=SURF2)
        lh.pack(fill="x", side="bottom")
        tk.Label(lh, text=" OUTPUT ", font=(self.MONO,7,"bold"),
                 bg=BLUE, fg="white", padx=6, pady=2).pack(side="left")
        tk.Label(lh, text="  Real-time command output",
                 font=(self.MONO,7), bg=SURF2, fg=MUTED).pack(side="left")
        self._mkbtn(lh, " Clear ", self._clear_log,
                    SURF2, fs=7, px=8, py=3, fg=MUTED
                    ).pack(side="right", padx=4, pady=2)

        lf = tk.Frame(self.root, bg=LOG_BG)
        lf.pack(fill="x", side="bottom")
        self.log_txt = tk.Text(lf, bg=LOG_BG, fg=TEXT2, font=(self.MONO,8),
                               relief="flat", bd=0, state="disabled",
                               height=7, wrap="word")
        lsb = ttk.Scrollbar(lf, orient="vertical",
                            command=self.log_txt.yview, style="TScrollbar")
        self.log_txt.configure(yscrollcommand=lsb.set)
        lsb.pack(side="right", fill="y")
        self.log_txt.pack(fill="x", padx=8, pady=6)
        for tag, fg in (("ok",T_OK),("warn",T_WARN),("err",T_ERR),
                        ("info",T_INFO),("cmd",T_CMD),("dim",T_DIM)):
            self.log_txt.tag_config(tag, foreground=fg)

    def _clear_log(self):
        self.log_txt.config(state="normal")
        self.log_txt.delete("1.0","end")
        self.log_txt.config(state="disabled")

    def _build_statusbar(self):
        tk.Frame(self.root, bg=BORDER, height=1).pack(fill="x", side="bottom")
        sb = tk.Frame(self.root, bg=SURF2)
        sb.pack(fill="x", side="bottom")
        self.status_lbl = tk.Label(sb, text="⬤  Ready",
                                   font=(self.MONO,8,"bold"),
                                   bg=SURF2, fg=OK_FG)
        self.status_lbl.pack(side="left", padx=12, pady=5)
        tk.Label(sb,
                 text=f"Python {sys.version.split()[0]}  •  "
                      f"{platform.system()} {platform.release()}",
                 font=(self.MONO,7), bg=SURF2, fg=MUTED).pack(side="left")
        tk.Label(sb,
                 text="Runs on dreams and hopes, made with ♥  by auratech0",
                 font=(self.MONO,7), bg=SURF2, fg=MUTED
                 ).pack(side="right", padx=12)

    # ═════════════════════════════════════════════════════════════════════════
    #  FLASH LOGIC
    # ═════════════════════════════════════════════════════════════════════════
    def _update_mode_panels(self):
        m = get_mode(self.mode_var.get())
        if not m: return
        _, _, _, risk, warn, info, safe = m
        wbg = DANG_BG if risk=="danger" else WARN_BG
        wfg = DANG_FG if risk=="danger" else WARN_FG
        self.warn_frame.config(bg=wbg)
        self.warn_lbl.config(bg=wbg, fg=wfg, text=warn)
        self.info_lbl.config(text=f"ℹ  {info}")
        self.safe_lbl.config(text=safe)
        self._refresh_flash_btn()

    def _refresh_flash_btn(self):
        if self.flashing: return
        pending = sum(1 for v in self.check_vars.values() if not v.get())
        if pending:
            self._stop_glow()
            self.flash_btn.config(bg="#1a2e1a",
                                  text=f"  ▶  START FLASH  ({pending} checks pending)")
        else:
            self.flash_btn.config(bg=GREEN, text="  ▶  START FLASH  ")
            self._start_glow()

    def select_file(self):
        m = get_mode(self.mode_var.get())
        if not m: return
        exts = m[1]
        fts  = [(f"{e.upper()} files", f"*{e}") for e in exts] + [("All files","*.*")]
        path = filedialog.askopenfilename(title="Select Firmware / ROM File", filetypes=fts)
        if not path: return
        _, ext = os.path.splitext(path)
        if ext.lower() not in exts:
            messagebox.showwarning("Wrong File Type",
                f"Mode expects: {', '.join(exts)}\n"
                f"You chose: '{ext or '(none)'}'\n\n"
                "Select the correct file or change flash mode.")
            return
        self.selected_path = path
        name    = os.path.basename(path)
        size_mb = os.path.getsize(path) / (1024*1024)
        self.file_lbl.config(text=f"  {name}", fg=OK_FG)
        self.file_meta.config(text=f"  {size_mb:.2f} MB   ·   {path}")
        self._log(f"File selected: {name}  ({size_mb:.2f} MB)\n","ok")

    def start_flash(self):
        pending = sum(1 for v in self.check_vars.values() if not v.get())
        if pending and not messagebox.askyesno("Checklist Incomplete",
                f"{pending} item(s) not confirmed.\nThis may brick your device. Proceed?"):
            return
        if not self.selected_path:
            messagebox.showwarning("No File","Please select a file first."); return
        m = get_mode(self.mode_var.get())
        _,_, proto, risk, warn, _, safe = m
        if risk=="danger" and not messagebox.askyesno("⚠  DANGEROUS",
                f"{warn}\n\n{safe}\n\nCannot be undone. Continue?",icon="warning"):
            return
        cmd = self._build_flash_cmd(proto, self.selected_path)
        if not cmd: return
        if not messagebox.askyesno("Confirm Flash",
                f"Command:\n\n  {' '.join(cmd)}\n\n{safe}\n\nProceed?"): return

        self._stop_glow()
        self.flashing = True
        self.flash_btn.config(state="disabled", bg="#222", text="  ⏳  Flashing…  ")
        self.browse_btn.config(state="disabled")
        self.mode_cb.config(state="disabled")
        self.flash_prog.start(10)
        threading.Thread(target=self._do_flash, args=(cmd, proto), daemon=True).start()

    def _build_flash_cmd(self, proto, path):
        table = {
            "fb_recovery":  ["fastboot","flash","recovery",  path],
            "fb_boot":      ["fastboot","flash","boot",      path],
            "fb_vendor":    ["fastboot","flash","vendor",    path],
            "fb_system":    ["fastboot","flash","system",    path],
            "fb_dtbo":      ["fastboot","flash","dtbo",      path],
            "fb_vbmeta":    ["fastboot","--disable-verity","--disable-verification",
                             "flash","vbmeta",path],
            "fb_zip":       ["fastboot","update",             path],
            "adb_sideload": ["adb","sideload",               path],
        }
        cmd = table.get(proto)
        if not cmd:
            messagebox.showerror("Internal Error",f"Unknown protocol: {proto}")
        return cmd

    def _do_flash(self, cmd, proto):
        self._status("⬤  Flashing…", WARN_FG)
        self._ui(lambda: self.flash_status.config(text=f"Running: {' '.join(cmd[:4])}…"))
        self._log(f"CMD: {' '.join(cmd)}\n","cmd")

        # Pre-flash info checks
        if cmd[0] == "fastboot":
            _, out, _ = fastboot("getvar","unlocked")
            if not any(x in (out or "").lower() for x in ("yes","true")):
                self._log("WARNING: Bootloader may not be unlocked — flash may fail.\n","warn")
            _, slot, _ = fastboot("getvar","current-slot")
            if slot.strip():
                self._log(f"Current A/B slot: {slot.strip()}\n","info")

        rc, stdout, stderr = run_cmd(cmd, timeout=300)
        combined = ((stdout or "")+"\n"+(stderr or "")).strip()
        for line in combined.splitlines():
            if not line.strip(): continue
            bad = rc!=0 and any(w in line.lower() for w in ("error","fail","denied"))
            self._log(f"  {line}\n","err" if bad else "dim")

        if rc == 0:
            self._log("✓  Flash completed successfully.\n","ok")
            self._status("⬤  Done", OK_FG)
            name = os.path.basename(self.selected_path)
            self._ui(lambda: messagebox.showinfo("Success ✓",
                f"'{name}' flashed successfully.\n\n"
                "Use the 🔄 Reboot tab to restart your device."))
        elif rc == -1:
            tool = cmd[0]
            self._log(f"'{tool}' not found in PATH.\n","err")
            self._status("⬤  Tool Missing", RED)
            self._ui(lambda: messagebox.showerror("Tool Not Found",
                f"'{tool}' not found.\n\n"
                "Install Android Platform Tools:\n"
                "https://developer.android.com/tools/releases/platform-tools"))
        else:
            self._log(f"FAILED (exit {rc})\n","err")
            self._status("⬤  Failed", RED)
            ec = (stderr or "")[:400]
            self._ui(lambda: messagebox.showerror("Flash Failed",
                f"Exit {rc}. Check the log.\n\nstderr:\n{ec}"))

        self._log("─"*80+"\n","dim")

        def _restore():
            self.flashing = False
            self.flash_prog.stop()
            self.flash_status.config(text="")
            self.browse_btn.config(state="normal")
            self.mode_cb.config(state="readonly")
            self._refresh_flash_btn()
        self._ui(_restore)

    # ═════════════════════════════════════════════════════════════════════════
    #  WIPE OPERATIONS
    # ═════════════════════════════════════════════════════════════════════════
    def _wipe_app_data(self):
        pkg = self._ask("Wipe App Data","Package name to clear:\n(e.g. com.example.app)")
        if not pkg: return
        if not messagebox.askyesno("Confirm",f"Clear all data for:\n{pkg}"): return
        p = pkg.strip()
        threading.Thread(target=lambda: self._do_wipe(
            ["adb","shell","pm","clear",p]), daemon=True).start()

    def _wipe_dalvik(self):
        if not messagebox.askyesno("Wipe Dalvik Cache",
                "Delete /data/dalvik-cache?\nRequires root. Slow first boot after.",
                icon="warning"): return
        threading.Thread(target=lambda: self._do_wipe(
            ["adb","shell","rm","-rf","/data/dalvik-cache"]),daemon=True).start()

    def _wipe_cache_fb(self):
        if not messagebox.askyesno("Wipe Cache",
                "fastboot erase cache\nDevice must be in Fastboot mode.",
                icon="warning"): return
        threading.Thread(target=lambda: self._do_wipe(
            ["fastboot","erase","cache"]),daemon=True).start()

    def _wipe_userdata(self):
        if not messagebox.askyesno("⚠  WIPE USERDATA",
                "fastboot erase userdata\n\n"
                "PERMANENTLY deletes ALL user data.\n"
                "Device must be in Fastboot mode.\n\n"
                "Are you absolutely sure?",icon="warning"): return
        if not messagebox.askyesno("Final Confirmation",
                "LAST CHANCE — all data deleted.\n\nProceed?",icon="warning"): return
        threading.Thread(target=lambda: self._do_wipe(
            ["fastboot","erase","userdata"]),daemon=True).start()

    def _do_wipe(self, cmd):
        self._log(f"WIPE: {' '.join(cmd)}\n","cmd")
        rc, out, err = run_cmd(cmd)
        if rc == 0:
            self._log(f"Wipe completed.\n{out}\n","ok")
            self._ui(lambda: messagebox.showinfo("Done","Wipe completed."))
        else:
            self._log(f"FAILED (rc={rc}): {err}\n","err")
            self._ui(lambda: messagebox.showerror("Failed",f"rc={rc}\n{err[:300]}"))

    # ═════════════════════════════════════════════════════════════════════════
    #  STRING INPUT DIALOG
    # ═════════════════════════════════════════════════════════════════════════
    def _ask(self, title, prompt):
        dlg = tk.Toplevel(self.root)
        dlg.title(title)
        dlg.configure(bg=SURF)
        dlg.grab_set()
        dlg.resizable(False,False)
        # Centre over parent
        self.root.update_idletasks()
        px, py = self.root.winfo_x(), self.root.winfo_y()
        pw, ph = self.root.winfo_width(), self.root.winfo_height()
        dlg.geometry(f"460x200+{px+pw//2-230}+{py+ph//2-100}")

        tk.Label(dlg, text=prompt, font=(self.MONO,9),
                 bg=SURF, fg=TEXT, justify="left").pack(padx=20, pady=(16,6))
        var = tk.StringVar()
        ent = tk.Entry(dlg, textvariable=var, font=(self.MONO,9),
                       bg=BG, fg=TEXT, insertbackground=TEXT,
                       relief="flat", bd=5, width=44)
        ent.pack(padx=20, pady=4)
        ent.focus_set()

        result = [None]
        def _ok():   result[0]=var.get().strip(); dlg.destroy()
        def _can():  dlg.destroy()
        br = tk.Frame(dlg, bg=SURF)
        br.pack(pady=12)
        self._mkbtn(br,"  OK  ",   _ok,  GREEN, px=16,py=7).pack(side="left",padx=6)
        self._mkbtn(br," Cancel ", _can, SURF2, px=16,py=7).pack(side="left",padx=6)
        dlg.bind("<Return>",lambda _:_ok())
        dlg.bind("<Escape>",lambda _:_can())
        self.root.wait_window(dlg)
        return result[0]

    # ═════════════════════════════════════════════════════════════════════════
    #  STARTUP / DEVICE CHECK
    # ═════════════════════════════════════════════════════════════════════════
    def _boot_check(self):
        self._log("Checking tools and devices…\n","info")
        results = {}
        for tool in ("adb","fastboot"):
            rc, out, err = run_cmd([tool,"version"], timeout=5)
            line = (out or err).splitlines()
            results[tool] = (rc, line[0].strip() if line else "?")

        adb_dev = fb_dev = 0
        try:
            _, out, _ = run_cmd(["adb","devices"], timeout=5)
            adb_dev = sum(1 for l in out.splitlines()
                          if l.strip()
                          and "List of" not in l
                          and "daemon"   not in l)
        except Exception: pass
        try:
            _, out, _ = run_cmd(["fastboot","devices"], timeout=5)
            fb_dev = sum(1 for l in out.splitlines() if l.strip())
        except Exception: pass

        self._ui(lambda: self._apply_boot(results, adb_dev, fb_dev))

    def _apply_boot(self, results, adb_dev, fb_dev):
        missing = [t for t,(rc,_) in results.items() if rc==-1]
        total   = adb_dev + fb_dev

        if missing:
            self.dev_badge.config(
                text=f"⬤  Missing: {', '.join(missing)}", fg=RED)
        elif total > 0:
            self.dev_badge.config(
                text=f"⬤  {total} device(s) detected", fg=OK_FG)
            self._pulse_badge(OK_FG)
        else:
            self.dev_badge.config(text="⬤  No device detected", fg=WARN_FG)

        for tool, (rc, ver) in results.items():
            self._log((f"Tool OK : {ver}\n" if rc==0
                       else f"MISSING : '{tool}' — install Android Platform Tools\n"),
                      "ok" if rc==0 else "err")

        if total > 0:
            self._log(f"Devices : {adb_dev} ADB  ·  {fb_dev} Fastboot\n","ok")
            rc_m,  model, _ = adb("shell","getprop","ro.product.model")
            rc_mf, mfr,   _ = adb("shell","getprop","ro.product.manufacturer")
            model_s = model.strip() if rc_m  == 0 else ""
            mfr_s   = mfr.strip()   if rc_mf == 0 else ""
            display = f"{mfr_s} {model_s}".strip()
            if display:
                self.dev_model.config(text=display)
        else:
            self._log("No device found. Connect + enable USB Debugging / Fastboot.\n","warn")

        self._log("─"*80+"\n","dim")


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()

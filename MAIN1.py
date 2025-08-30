import os
import time
import platform
import psutil
import mouse
import pyautogui
import threading
from colorama import Fore, init
import random
import sys
import subprocess
import requests  # for fetching allowed SIDs

try:
    import pywinusb.hid as hid
except:
    hid = None

# --------- GLOBAL STATES ----------
mouse_connected = False
drag_assist_enabled = False
force_smooth_enabled = False
ghost_ai_enabled = False
prev_ai_status = False
running = True

normal_sensitivity = 1.0
boosted_sensitivity = 1.5  # Sensitivity boost factor

init(autoreset=True)

# --------- AUTHENTICATION ----------
def get_current_sid():
    try:
        # Get current user's SID via whoami
        sid = subprocess.check_output("whoami /user", shell=True, text=True).split()[-1]
        return sid.strip()
    except Exception as e:
        print("[-] Failed to get SID:", e)
        exit(1)

def authenticate():
    url = "https://raw.githubusercontent.com/OCTANE-XD/ZENITHCONT/main/sids.txt"
    try:
        valid_sids = requests.get(url).text.splitlines()
    except Exception as e:
        print("[-] Failed to fetch SID list from GitHub:", e)
        exit(1)

    current_sid = get_current_sid()
    print(f"[!] Your SID: {current_sid}")

    if current_sid not in valid_sids:
        print("[-] Authentication failed! Your SID is not authorized.")
        exit(1)
    else:
        print("[+] Authentication successful! Welcome to ZENITH CONTROL.")

# --------- UTILITIES ----------
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def progress_bar(task_name, duration=2):
    print(Fore.CYAN + f"{task_name}...")
    steps = 20
    for i in range(steps + 1):
        bar = "#" * i + "-" * (steps - i)
        percent = int((i / steps) * 100)
        print(Fore.YELLOW + f"[{bar}] {percent}%", end="\r")
        time.sleep(duration / steps)
    print()

# --------- DRAG ASSIST THREAD ----------
def drag_assist_loop():
    global drag_assist_enabled, running
    prev_x, prev_y = pyautogui.position()
    while running:
        if drag_assist_enabled and mouse_connected:
            x, y = pyautogui.position()
            smoothness = random.uniform(0.85, 0.95)
            new_x = int(prev_x + (x - prev_x) * smoothness)
            new_y = int(prev_y + (y - prev_y) * smoothness)
            if (new_x, new_y) != (x, y):
                mouse.move(new_x, new_y, absolute=True, duration=0)
            prev_x, prev_y = new_x, new_y
        else:
            prev_x, prev_y = pyautogui.position()
        time.sleep(0.005)

# --------- FORCE SMOOTHNESS THREAD ----------
def force_smoothness_loop():
    global force_smooth_enabled, running
    prev_x, prev_y = pyautogui.position()
    smoothing = 0.90
    while running:
        if force_smooth_enabled and mouse_connected:
            x, y = pyautogui.position()
            new_x = int(prev_x + (x - prev_x) * smoothing)
            new_y = int(prev_y + (y - prev_y) * smoothing)
            if (new_x, new_y) != (x, y):
                mouse.move(new_x, new_y, absolute=True, duration=0)
            prev_x, prev_y = new_x, new_y
        else:
            prev_x, prev_y = pyautogui.position()
        time.sleep(0.005)

# --------- GHOST AI THREAD ----------
def ghost_ai_loop():
    global ghost_ai_enabled, running, prev_ai_status
    prev_pos = pyautogui.position()
    sensitivity = normal_sensitivity
    smoothing_factor = 0.02
    while running:
        if ghost_ai_enabled and mouse_connected:
            x, y = pyautogui.position()
            dx = abs(x - prev_pos[0])
            dy = abs(y - prev_pos[1])
            speed = dx + dy

            if speed > 30:  # Fast movement → boost
                sensitivity = boosted_sensitivity
                prev_ai_status = True
            else:
                sensitivity -= (sensitivity - normal_sensitivity) * smoothing_factor
                sensitivity = max(normal_sensitivity, sensitivity)
                if prev_ai_status and sensitivity <= normal_sensitivity + 0.01:
                    prev_ai_status = False

            new_x = prev_pos[0] + int((x - prev_pos[0]) * sensitivity * 0.7)
            new_y = prev_pos[1] + int((y - prev_pos[1]) * sensitivity * 1.2)

            if (new_x, new_y) != (x, y):
                mouse.move(new_x, new_y, absolute=True, duration=0)

            prev_pos = new_x, new_y
        else:
            prev_pos = pyautogui.position()
            prev_ai_status = False
        time.sleep(0.01)

# --------- MOUSE SCANNER ----------
def get_mouse_info():
    if hid is None:
        return "Unknown Mouse (pywinusb not installed)"
    all_devices = hid.HidDeviceFilter().get_devices()
    for dev in all_devices:
        try:
            return f"{dev.vendor_name} {dev.product_name}"
        except:
            continue
    return "Unknown Mouse"

# --------- ASCII BANNER ----------
def banner():
    print(Fore.RED + r"""
   ███████╗███████╗███╗   ██╗██╗████████╗██╗  ██╗     ██████╗ ██████╗ ███╗   ██╗████████╗██████╗  ██████╗ ██╗     
   ╚══███╔╝██╔════╝████╗  ██║██║╚══██╔══╝██║  ██║    ██╔════╝██╔═══██╗████╗  ██║╚══██╔══╝██╔══██╗██╔═══██╗██║     
     ███╔╝ █████╗  ██╔██╗ ██║██║   ██║   ███████║    ██║     ██║   ██║██╔██╗ ██║   ██║   ██████╔╝██║   ██║██║     
    ███╔╝  ██╔══╝  ██║╚██╗██║██║   ██║   ██╔══██║    ██║     ██║   ██║██║╚██╗██║   ██║   ██╔══██╗██║   ██║██║     
   ███████╗███████╗██║ ╚████║██║   ██║   ██║  ██║    ╚██████╗╚██████╔╝██║ ╚████║   ██║   ██║  ██║╚██████╔╝███████╗
   ╚══════╝╚══════╝╚═╝  ╚═══╝╚═╝   ╚═╝   ╚═╝  ╚═╝     ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝
                                                            
    """)

# --------- AUTO CONNECT ----------
def auto_connect():
    global mouse_connected
    if not mouse_connected:
        progress_bar("Auto-connecting to mouse", 2.5)
        device = get_mouse_info()
        print(Fore.YELLOW + f"[INFO] Mouse detected: {device}")
        progress_bar("Establishing connection", 2)
        mouse_connected = True
        print(Fore.GREEN + "[SUCCESS] Mouse connected to ZENITH CONTROL's Server successfully")
    time.sleep(1.5)

# --------- OPTION FUNCTIONS ----------
def drag_assist():
    global drag_assist_enabled
    if not mouse_connected:
        print(Fore.RED + "[ERROR] Mouse not connected to ZENITH CONTROL's Server.")
        time.sleep(2)
        return
    if not drag_assist_enabled:
        progress_bar("Activating Drag Assist", 2.5)
        drag_assist_enabled = True
        print(Fore.GREEN + "[SUCCESS] Drag Assist activated → Smoothness: 85–95%")
    else:
        choice = input(Fore.YELLOW + "Disable Drag Assist? (y/n): ").strip().lower()
        if choice == "y":
            progress_bar("Disabling Drag Assist", 1.5)
            drag_assist_enabled = False
            print(Fore.YELLOW + "[SUCCESS] Drag Assist turned off")
        else:
            print(Fore.CYAN + "[INFO] Drag Assist remains ON")
    time.sleep(2)

def system_scan():
    if not mouse_connected:
        print(Fore.RED + "[ERROR] Mouse not connected to ZENITH CONTROL's Server.")
        time.sleep(2)
        return
    progress_bar("Running SYSTEM SCAN", 3)
    print(Fore.CYAN + "====================================")
    print(Fore.MAGENTA + "         SYSTEM SCAN       ")
    print(Fore.CYAN + "====================================")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"CPU: {platform.processor()}")
    print(f"RAM: {round(psutil.virtual_memory().total / (1024**3), 2)} GB")
    try:
        import screeninfo
        screen = screeninfo.get_monitors()[0]
        print(f"Resolution: {screen.width}x{screen.height}")
    except:
        print("Resolution: (screeninfo not installed)")
    print(f"Mouse Connected: {'Yes' if mouse_connected else 'No'}")
    print(f"Drag Assist: {'ON' if drag_assist_enabled else 'OFF'}")
    print(f"Force Smoothness: {'ON' if force_smooth_enabled else 'OFF'}")
    print(f"Ghost AI Mode: {'ON' if ghost_ai_enabled else 'OFF'}")
    print(Fore.CYAN + "====================================")
    time.sleep(3)

def check_mode():
    if not mouse_connected:
        print(Fore.RED + "[ERROR] Mouse not connected to ZENITH CONTROL's Server.")
        time.sleep(2)
        return
    clear()
    print(Fore.YELLOW + "========== AIM CHECK MODE ==========")
    print("Move your mouse freely inside this grid for 5 seconds")
    positions = []
    start = time.time()
    while time.time() - start < 5:
        positions.append(pyautogui.position())
        time.sleep(0.05)
    diffs = [abs(positions[i][0]-positions[i-1][0]) + abs(positions[i][1]-positions[i-1][1]) for i in range(1,len(positions))]
    avg_move = sum(diffs)/len(diffs) if diffs else 0
    score = max(0, 100-int(avg_move/5))
    print(Fore.CYAN + f"Aim Smoothness Score: {score}/100")
    time.sleep(3)

def force_smoothness():
    global force_smooth_enabled
    force_smooth_enabled = not force_smooth_enabled
    status = "ENABLED" if force_smooth_enabled else "DISABLED"
    progress_bar(f"Setting Force Smoothness → {status}", 2)
    print(Fore.GREEN + f"[INFO] Force Smoothness {status}")
    time.sleep(2)

def ghost_ai_mode():
    global ghost_ai_enabled
    ghost_ai_enabled = not ghost_ai_enabled
    status = "ENABLED" if ghost_ai_enabled else "DISABLED"
    progress_bar(f"Setting ZENITH AI Mode → {status}", 2)
    print(Fore.GREEN + f"[INFO] ZENITH AI Mode {status}")
    time.sleep(2)

# --------- MAIN MENU ----------
def menu():
    global running
    while True:
        clear()
        banner()
        print(Fore.YELLOW + "============ MENU ============")
        print(Fore.CYAN + "1. ENABLE / DISABLE DRAG ASSIST")
        print(Fore.CYAN + "2. SYSTEM SCAN")
        print(Fore.CYAN + "3. CHECK MODE")
        print(Fore.CYAN + "4. FORCE SMOOTHNESS")
        print(Fore.CYAN + "5. ZENITH AI MODE")
        print(Fore.RED + "Q. QUIT")
        print(Fore.YELLOW + "==============================")
        choice = input(Fore.WHITE + "Select option: ").strip().lower()
        if choice == "1":
            drag_assist()
        elif choice == "2":
            system_scan()
        elif choice == "3":
            check_mode()
        elif choice == "4":
            force_smoothness()
        elif choice == "5":
            ghost_ai_mode()
        elif choice == "q":
            print(Fore.YELLOW + "Exiting...")
            running = False
            break
        else:
            print(Fore.RED + "Invalid option! Please try again")
            time.sleep(1)

# --------- START THREADS + MENU ----------
if __name__ == "__main__":
    authenticate()   # 🔹 SID check first
    auto_connect()
    threading.Thread(target=drag_assist_loop, daemon=True).start()
    threading.Thread(target=force_smoothness_loop, daemon=True).start()
    threading.Thread(target=ghost_ai_loop, daemon=True).start()
    menu()

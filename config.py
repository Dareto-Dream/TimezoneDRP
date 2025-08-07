import tkinter as tk
from tkinter import messagebox
import os
from zoneinfo import available_timezones, ZoneInfo
from datetime import datetime
import threading
from tzlocal import get_localzone_name
import webbrowser

from dotenv import load_dotenv

ENV_FILE = ".env"
CLIENT_ID = "1402709604588322836"
IMAGE_MODES = ["Auto", "Day", "Night"]
LABEL_MODES = ["Abbreviation", "City/Region"]
presence_thread = None
stop_event = None

try:
    CITIES = sorted([tz for tz in available_timezones() if "/" in tz and not tz.startswith("Etc/")])
except Exception:
    CITIES = ["Asia/Tashkent", "America/Los_Angeles", "Europe/London", "Pacific/Honolulu"]

def get_offset_label(tz_name):
    now = datetime.now(ZoneInfo(tz_name))
    offset_hours = now.utcoffset().total_seconds() / 3600
    offset_str = f"{offset_hours:+.1f}" if ".0" not in f"{offset_hours:+.1f}" else f"{int(offset_hours):+d}"
    abbrev = now.tzname()
    label = f"{abbrev} (UTC{offset_str})"
    return label, offset_hours, abbrev

def auto_detect_timezone():
    try:
        detected = get_localzone_name()
        if detected in CITIES:
            idx = CITIES.index(detected)
            listbox.selection_clear(0, tk.END)
            listbox.selection_set(idx)
            listbox.see(idx)
            city_var.set(detected)
            search_var.set(detected)
            messagebox.showinfo("Detected", f"Detected timezone: {detected}")
        else:
            messagebox.showerror("Not found", f"Detected timezone '{detected}' not in city list.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to auto-detect timezone: {e}")

def save_env():
    # Always pull selected item from the listbox
    try:
        selected_idx = listbox.curselection()
        if not selected_idx:
            tz_name = CITIES[0]  # fallback
        else:
            tz_name = listbox.get(selected_idx)
    except Exception:
        tz_name = city_var.get()
    if tz_name not in CITIES:
        messagebox.showerror("Invalid Timezone", "Please select a valid timezone from the list.")
        return
    label, offset, abbrev = get_offset_label(tz_name)
    image_mode = image_mode_var.get().lower()
    label_mode = label_mode_var.get().lower()
    city = tz_name.split('/')[-1].replace('_', ' ')
    with open(ENV_FILE, "w") as f:
        f.write(f"DISCORD_CLIENT_ID={CLIENT_ID}\n")
        f.write(f"TIMEZONE_LABEL={label}\n")
        f.write(f"TIMEZONE_OFFSET={offset}\n")
        f.write(f"TIMEZONE_NAME={tz_name}\n")
        f.write(f"TIMEZONE_CITY={city}\n")
        f.write(f"TIMEZONE_ABBREV={abbrev}\n")
        f.write(f"IMAGE_MODE={image_mode}\n")
        f.write(f"LABEL_MODE={label_mode}\n")
    messagebox.showinfo("Saved", f"Config saved to {ENV_FILE}")

def report_bug():
    webbrowser.open("https://github.com/dareto-dream/timezonedrp/issues")

def buy_me_coffee():
    webbrowser.open("buymeacoffee.com/dareto0ream")


def launch_script():
    global presence_thread, stop_event
    save_env()

    # Stop any existing presence thread
    if stop_event is not None:
        print("[GUI] Stopping previous presence thread...")
        stop_event.set()  # Signal it to exit

    # Start new presence thread with a fresh stop_event
    import main
    from threading import Event
    stop_event = Event()
    def run_presence():
        main.run(stop_event=stop_event)
    presence_thread = threading.Thread(target=run_presence, daemon=True)
    presence_thread.start()

def filter_timezones(event):
    typed = search_var.get().lower()
    filtered = [tz for tz in CITIES if typed in tz.lower()]
    listbox.delete(0, tk.END)
    for tz in filtered:
        listbox.insert(tk.END, tz)
    if filtered:
        listbox.selection_set(0)
        city_var.set(filtered[0])

def on_select(event):
    if listbox.curselection():
        selected = listbox.get(listbox.curselection())
        city_var.set(selected)

root = tk.Tk()
root.title("Discord Timezone DRP Config")

# For Windows .ico or PNG (fallback for Linux/Mac)
try:
    # .ico for Windows
    root.iconbitmap("icon.ico")
except Exception:
    # fallback: use PNG for Linux/Mac
    try:
        from tkinter import PhotoImage
        icon = PhotoImage(file="icon.png")
        root.iconphoto(True, icon)
    except Exception:
        pass  # don't crash if no icon

tk.Label(root, text="Discord Client ID").grid(row=0, column=0, sticky="w")
tk.Label(root, text=CLIENT_ID).grid(row=0, column=1, sticky="w")

tk.Label(root, text="Search Timezone:").grid(row=1, column=0, sticky="w")
search_var = tk.StringVar()
search_entry = tk.Entry(root, textvariable=search_var, width=32)
search_entry.grid(row=1, column=1, sticky="w")

tk.Label(root, text="Timezone (Region/City)").grid(row=2, column=0, sticky="w")
city_var = tk.StringVar(value="Asia/Tashkent")
listbox = tk.Listbox(root, height=8, width=32)
listbox.grid(row=2, column=1, sticky="w")
for tz in CITIES:
    listbox.insert(tk.END, tz)

# Load .env and auto-select previous config values
load_dotenv(ENV_FILE, override=True)
city_env        = os.getenv("TIMEZONE_NAME", CITIES[0])
image_mode_env  = os.getenv("IMAGE_MODE", "Auto").capitalize()
label_mode_env  = os.getenv("LABEL_MODE", "Abbreviation").capitalize()

city_var.set(city_env)
image_mode_var = tk.StringVar(root)
image_mode_var.set(image_mode_env)
label_mode_var = tk.StringVar(root)
label_mode_var.set(label_mode_env)
search_var.set(city_env)

try:
    idx = CITIES.index(city_env)
    listbox.selection_clear(0, tk.END)
    listbox.selection_set(idx)
    listbox.see(idx)
except ValueError:
    listbox.selection_set(0)
    city_var.set(CITIES[0])

search_entry.bind('<KeyRelease>', filter_timezones)
listbox.bind('<<ListboxSelect>>', on_select)

tk.Label(root, text="Image Mode").grid(row=3, column=0, sticky="w")
tk.OptionMenu(root, image_mode_var, *IMAGE_MODES).grid(row=3, column=1, sticky="w")

tk.Label(root, text="Label Style").grid(row=4, column=0, sticky="w")
tk.OptionMenu(root, label_mode_var, *LABEL_MODES).grid(row=4, column=1, sticky="w")

action_frame = tk.Frame(root)
action_frame.grid(row=5, column=0, columnspan=3, pady=10)

tk.Button(action_frame, text="Save Config", command=save_env).pack(side=tk.LEFT, padx=10)
tk.Button(action_frame, text="Save and Launch", command=launch_script).pack(side=tk.LEFT, padx=10)
tk.Button(root, text="Auto Detect Timezone", command=auto_detect_timezone).grid(row=1, column=2, padx=10)

button_frame = tk.Frame(root)
button_frame.grid(row=6, column=0, columnspan=3, pady=10)

tk.Button(button_frame, text="Report Bug", command=report_bug).pack(side=tk.LEFT, padx=10)
tk.Button(button_frame, text="Buy Me a Coffee", command=buy_me_coffee).pack(side=tk.LEFT, padx=10)


root.mainloop()
#!/usr/bin/env python3
"""
waitmic.py -- watch for a USB audio device to appear.

    python3 waitmic.py

Polls twice a second and prints the moment a device shows up or disappears.
Run it while you reseat the cable, so you can see immediately which cable and
which port actually work, instead of guessing and re-running --list.

Ctrl-C to stop.
"""
import subprocess, sys, time

def usb_names():
    r = subprocess.run(['ioreg', '-rc', 'IOUSBHostDevice'],
                       capture_output=True, text=True)
    return sorted({l.split('=')[1].strip().strip('"')
                   for l in r.stdout.splitlines()
                   if 'USB Product Name' in l})

# NOTE: deliberately no PortAudio query here. Re-initialising PortAudio in a
# loop to pick up new devices throws "Audio Hardware: Unknown Property", and
# ioreg is the more reliable signal anyway -- if the device is not on the USB
# bus, no audio API will ever see it.

print("\n  Watching for USB devices. Reseat the cable now.")
print("  Ctrl-C to stop.\n")
prev_u = None
try:
    while True:
        u = usb_names()
        if u != prev_u:
            t = time.strftime('%H:%M:%S')
            if u:
                print(f"  [{t}] CONNECTED: " + ", ".join(u))
                print(f"           -> ab chalao:  python3 record.py --list")
            else:
                print(f"  [{t}] nothing on the USB bus")
            prev_u = u
        time.sleep(0.5)
except KeyboardInterrupt:
    print("\n  stopped\n")

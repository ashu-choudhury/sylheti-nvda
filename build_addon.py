#!/usr/bin/env python3
"""
Packages the NVDA add-on directory into a `.nvda-addon` bundle.
"""

import os
import zipfile

ADDON_DIR = os.path.join(os.path.dirname(__file__), "addon")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "sylheti-tts.nvda-addon")

def package():
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    print(f"Packaging {ADDON_DIR} into {OUTPUT_FILE}...")
    with zipfile.ZipFile(OUTPUT_FILE, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(ADDON_DIR):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, ADDON_DIR)
                print(f"  Adding: {rel_path}")
                zf.write(full_path, rel_path)

    size = os.path.getsize(OUTPUT_FILE)
    print(f"\nSuccess! Created {OUTPUT_FILE} ({size:,} bytes)")

if __name__ == "__main__":
    package()

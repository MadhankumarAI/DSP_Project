"""
Experiment 5: Build a virus simulation tool - safe, educational, and
non-malicious - to help you understand how malware might behave in a
system, and how defenders can detect or prevent it.
"""
import random

SIGNATURE = "X-SIM-VIRUS-42"  # fake, harmless signature - nothing here touches real files
files = {f"file{i}.txt": "normal content" for i in range(1, 6)}

def show_files():
    for name, content in files.items():
        print(f"  {name}: {'INFECTED' if SIGNATURE in content else 'clean'}")

def infect_random_file():
    clean_files = [name for name, content in files.items() if SIGNATURE not in content]
    if clean_files:
        target = random.choice(clean_files)
        files[target] += " " + SIGNATURE
        print(f"[Infect] {target} got infected (simulated).")

def scan_and_disinfect():
    cleaned = 0
    for name, content in files.items():
        if SIGNATURE in content:
            files[name] = content.replace(SIGNATURE, "").strip()
            cleaned += 1
    print(f"[Scan] Disinfected {cleaned} file(s).")

print("Files before infection:")
show_files()

infect_random_file()
infect_random_file()
print("\nFiles after simulated spread:")
show_files()

scan_and_disinfect()
print("\nFiles after scan & disinfect:")
show_files()

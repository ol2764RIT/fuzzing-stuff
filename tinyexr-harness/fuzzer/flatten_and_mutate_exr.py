import os
import shutil
import subprocess

# === Configuration ===
CORPUS_DIR = "./corpus"
OUTPUT_DIR = "./mutated"
MUTATIONS_PER_FILE = 5
RADAMSA_BIN = "radamsa"

def is_exr_file(filename):
    return filename.lower().endswith(".exr")

def flatten_corpus():
    print("[*] Flattening corpus directory...")
    for root, dirs, files in os.walk(CORPUS_DIR):
        if root == CORPUS_DIR:
            continue  # Skip top-level

        for file in files:
            if is_exr_file(file):
                src = os.path.join(root, file)
                dest = os.path.join(CORPUS_DIR, file)

                # If name conflict, rename
                if os.path.exists(dest):
                    base, ext = os.path.splitext(file)
                    i = 1
                    while True:
                        new_name = f"{base}_{i}{ext}"
                        dest = os.path.join(CORPUS_DIR, new_name)
                        if not os.path.exists(dest):
                            break
                        i += 1

                shutil.move(src, dest)
                print(f"[+] Moved {src} → {dest}")

def mutate_file(file_path):
    with open(file_path, "rb") as f:
        original_data = f.read()

    base_name = os.path.basename(file_path)

    for i in range(MUTATIONS_PER_FILE):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_filename = f"{base_name}.fuzz{i}.exr"
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        try:
            mutated = subprocess.check_output([RADAMSA_BIN], input=original_data)
            with open(output_path, "wb") as out_f:
                out_f.write(mutated)
            print(f"[+] Wrote: {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"[!] Radamsa failed for {file_path}: {e}")
        except Exception as e:
            print(f"[!] Error for {file_path}: {e}")

def walk_and_mutate():
    for file in os.listdir(CORPUS_DIR):
        path = os.path.join(CORPUS_DIR, file)
        if os.path.isfile(path) and is_exr_file(file):
            mutate_file(path)

if __name__ == "__main__":
    flatten_corpus()
    walk_and_mutate()
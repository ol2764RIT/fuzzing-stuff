import os
import zipfile
import random

# Save ZIPs into this directory
CORPUS_DIR = "corpus"
os.makedirs(CORPUS_DIR, exist_ok=True)

SAMPLE_FILE = "⚠️_payload.txt"
PAYLOAD = b"This is a deliberately strange ZIP file.\n"

def create_payload_file():
    with open(SAMPLE_FILE, "wb") as f:
        f.write(PAYLOAD)

def make_zip(zip_path, arcname=None):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(SAMPLE_FILE, arcname or SAMPLE_FILE)

def generate_zero_width_zips():
    zwc = "\u200b\u200c\u200d\u2060"
    name = f"{CORPUS_DIR}/zero_width{zwc}.zip"
    make_zip(name)

def generate_rtl_zips():
    rtl = "\u202e"  # Right-to-left override
    fake_name = f"{CORPUS_DIR}/normal{rtl}fdp.exe.zip"
    make_zip(fake_name)

def generate_unicode_zips():
    names = [
        "💣_explosive.zip",
        "文件.zip",        # Chinese
        "файл.zip",        # Russian
        "ملف.zip",         # Arabic
        "ファイル.zip",    # Japanese
        "फ़ाइल.zip",       # Hindi
        "🧬_🦠_🧪.zip"
    ]
    for name in names:
        make_zip(f"{CORPUS_DIR}/{name}")

def generate_dot_trick_zips():
    names = [
        "report.final.v1.zip",
        "hidden.txt.zip",
        "resume.pdf.exe.zip",
        "photo.jpg.exe.zip"
    ]
    for name in names:
        make_zip(f"{CORPUS_DIR}/{name}")

def generate_weird_hexname_zips():
    hex_part = ''.join(random.choice('0123456789abcdef') for _ in range(8))
    name = f"{CORPUS_DIR}/weird_{hex_part}.zip"
    make_zip(name)

def generate_no_extension_zip():
    make_zip(f"{CORPUS_DIR}/no_extension")

def generate_weird_internal_filenames():
    filenames = [
        "nul.txt",
        "com1.txt",
        "aux.txt",
        "\u200b\u200csecret.txt",  # zero-width
        "file🚫.txt",
        "🤐🗜️.txt",
        "𝕱𝖎𝖑𝖊_𝕬𝖗𝖈𝖍𝖎𝖛𝖊.txt",
    ]
    for i, fname in enumerate(filenames):
        zip_name = f"{CORPUS_DIR}/internal_weird_{i}.zip"
        with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(SAMPLE_FILE, arcname=fname)

def cleanup():
    if os.path.exists(SAMPLE_FILE):
        os.remove(SAMPLE_FILE)

if __name__ == "__main__":
    print("🌀 Generating ultra-weird ZIP files into ./corpus/")
    create_payload_file()
    generate_zero_width_zips()
    generate_rtl_zips()
    generate_unicode_zips()
    generate_dot_trick_zips()
    generate_weird_hexname_zips()
    generate_no_extension_zip()
    generate_weird_internal_filenames()
    cleanup()
    print("✅ All done! Check the ./corpus/ directory.")

import os
import zipfile
import random
from pathlib import Path

CORPUS_DIR = "zip_corpus"
VALID_DIR = f"{CORPUS_DIR}/valid"
EDGE_DIR = f"{CORPUS_DIR}/edge"
RECURSIVE_DIR = f"{CORPUS_DIR}/recursive"

TEXT_SAMPLE = b"Sample text content.\n"

os.makedirs(VALID_DIR, exist_ok=True)
os.makedirs(EDGE_DIR, exist_ok=True)
os.makedirs(RECURSIVE_DIR, exist_ok=True)

def create_text_file(name, content=TEXT_SAMPLE):
    with open(name, "wb") as f:
        f.write(content)

def make_zip(output, file_list, compression=zipfile.ZIP_DEFLATED):
    with zipfile.ZipFile(output, "w", compression) as zipf:
        for file in file_list:
            zipf.write(file, arcname=os.path.basename(file))

def make_valid_zips():
    # Empty ZIP
    make_zip(f"{VALID_DIR}/empty.zip", [])

    # One file, no compression
    create_text_file("file1.txt")
    make_zip(f"{VALID_DIR}/one_file_nocompress.zip", ["file1.txt"], compression=zipfile.ZIP_STORED)

    # One file, with compression
    make_zip(f"{VALID_DIR}/one_file_compress.zip", ["file1.txt"])

    # Multiple files
    create_text_file("file2.txt", b"Another file")
    make_zip(f"{VALID_DIR}/multi_file.zip", ["file1.txt", "file2.txt"])

    # Long filename
    long_name = "a" * 200 + ".txt"
    create_text_file(long_name)
    make_zip(f"{VALID_DIR}/long_filename.zip", [long_name])

    # Odd metadata (ZIP will ignore most)
    make_zip(f"{VALID_DIR}/timestamped.zip", ["file1.txt"])

    # Large file
    with open("bigfile.txt", "wb") as f:
        f.write(b"A" * (1024 * 1024))  # 1MB
    make_zip(f"{VALID_DIR}/large_file.zip", ["bigfile.txt"])

    # Nested ZIP (1 level)
    make_zip("nested.zip", ["file1.txt"])
    make_zip(f"{VALID_DIR}/zip_in_zip.zip", ["nested.zip"])

def make_edge_case_zips():
    def corrupt_bytes(path, offsets):
        with open(path, "rb") as f:
            data = bytearray(f.read())
        for offset in offsets:
            if offset < len(data):
                data[offset] ^= 0xFF  # flip byte
        with open(path.replace(".zip", "_corrupt.zip"), "wb") as f:
            f.write(data)

    make_zip("base.zip", ["file1.txt"])
    corrupt_bytes("base.zip", [0, 2, 10])  # corrupt header bytes
    os.rename("base_corrupt.zip", f"{EDGE_DIR}/corrupt_header.zip")

    # Truncated
    with open("base.zip", "rb") as f:
        truncated = f.read()[:-30]
    with open(f"{EDGE_DIR}/truncated.zip", "wb") as f:
        f.write(truncated)

    # 0-length file
    create_text_file("zero.txt", b"")
    make_zip(f"{EDGE_DIR}/zero_length.zip", ["zero.txt"])

    # Weird compression flag
    make_zip("weird.zip", ["file1.txt"])
    with open("weird.zip", "rb") as f:
        data = bytearray(f.read())
    data[8] = 0x99  # nonsense compression method
    with open(f"{EDGE_DIR}/weird_compression.zip", "wb") as f:
        f.write(data)

def make_recursive_zips(depth=20):
    base_zip = f"{RECURSIVE_DIR}/zip_0.zip"
    make_zip(base_zip, ["file1.txt"])
    prev_zip = base_zip
    for i in range(1, depth + 1):
        new_zip = f"{RECURSIVE_DIR}/zip_{i}.zip"
        make_zip(new_zip, [prev_zip])
        prev_zip = new_zip

def cleanup_temp_files():
    for f in ["file1.txt", "file2.txt", "bigfile.txt", "zero.txt", "nested.zip", "base.zip", "weird.zip", "long_name.txt"]:
        if os.path.exists(f):
            os.remove(f)
    for f in Path('.').glob('a*.txt'):
        os.remove(f)

if __name__ == "__main__":
    print("🛠️ Generating ZIP corpus...")
    make_valid_zips()
    make_edge_case_zips()
    make_recursive_zips()
    cleanup_temp_files()
    print("✅ Done! Corpus saved in ./zip_corpus/")

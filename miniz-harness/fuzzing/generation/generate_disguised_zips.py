import os
import zipfile
import tarfile
import gzip
import lzma
from pathlib import Path

CORPUS_DIR = "disguised_zip_corpus"
os.makedirs(CORPUS_DIR, exist_ok=True)

# Sample content
TEXT_CONTENT = b"This is a test file.\n"
SAMPLE_FILE = "sample.txt"

def create_sample_file():
    with open(SAMPLE_FILE, "wb") as f:
        f.write(TEXT_CONTENT)

def make_real_zip(zip_name):
    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(SAMPLE_FILE)

def make_tar(tar_name):
    with tarfile.open(tar_name, "w") as tar:
        tar.add(SAMPLE_FILE)

def make_gzip(gz_name):
    with open(SAMPLE_FILE, "rb") as f_in, gzip.open(gz_name, "wb") as f_out:
        f_out.write(f_in.read())

def make_xz(xz_name):
    with open(SAMPLE_FILE, "rb") as f_in, lzma.open(xz_name, "wb") as f_out:
        f_out.write(f_in.read())

def generate_disguised_zips():
    print("🔧 Creating disguised archive files...")

    create_sample_file()

    # Step 1: Make other formats and rename as .zip
    make_tar("sample.tar")
    make_gzip("sample.gz")
    make_xz("sample.xz")

    os.rename("sample.tar", f"{CORPUS_DIR}/tar_disguised_as_zip.zip")
    os.rename("sample.gz", f"{CORPUS_DIR}/gz_disguised_as_zip.zip")
    os.rename("sample.xz", f"{CORPUS_DIR}/xz_disguised_as_zip.zip")

    # Step 2: Make valid ZIP and rename as other formats
    make_real_zip("real.zip")

    misleading_exts = [".tar", ".gz", ".xz", ".exe", ".doc", ".png", ".mp3", ".txt"]
    for ext in misleading_exts:
        fake_name = f"{CORPUS_DIR}/zip_disguised_as{ext}.zip"
        os.rename("real.zip", fake_name)
        make_real_zip("real.zip")  # recreate for next one

    # Step 3: Double extensions
    double_exts = [
        "archive.zip.exe",
        "resume.docx.zip",
        "image.png.zip",
        "music.mp3.zip",
        "notavirus.zip.scr",
    ]
    for name in double_exts:
        dst = f"{CORPUS_DIR}/{name}"
        os.rename("real.zip", dst)
        make_real_zip("real.zip")

    print("✅ Disguised ZIP files saved in ./disguised_zip_corpus")

def cleanup():
    if os.path.exists(SAMPLE_FILE):
        os.remove(SAMPLE_FILE)
    if os.path.exists("real.zip"):
        os.remove("real.zip")

if __name__ == "__main__":
    generate_disguised_zips()
    cleanup()

import os
import zipfile

CORPUS_DIR = "niche_zip_extensions"
os.makedirs(CORPUS_DIR, exist_ok=True)

SAMPLE_FILE = "niche.txt"
TEXT_CONTENT = b"Niche test content inside ZIP.\n"

# ✅ Step 1: Create a base file to zip
def create_sample():
    with open(SAMPLE_FILE, "wb") as f:
        f.write(TEXT_CONTENT)

# 📦 Step 2: Create ZIP archive
def make_zip(zip_name):
    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(SAMPLE_FILE)

# 🧪 Step 3: Rename ZIP file with niche extensions
def generate_niche_extensions():
    print("🔍 Generating niche extension ZIPs...")

    # Some niche, strange, or unexpected extensions
    niche_exts = [
        ".cbr",  # Comic Book RAR, often ZIP inside
        ".cbz",  # Comic Book ZIP
        ".epub", # eBook (actually a ZIP container)
        ".apk",  # Android app package (ZIP with specific structure)
        ".jar",  # Java archive (ZIP-based)
        ".war",  # Java web app archive
        ".ear",  # Enterprise archive
        ".odt",  # OpenDocument Text (ZIP-based)
        ".ods",  # OpenDocument Spreadsheet
        ".ott",  # ODT template
        ".xpi",  # Firefox plugin (ZIP format)
        ".appx", # Windows Store app (ZIP under the hood)
        ".kmz",  # Google Earth file (ZIP with KML inside)
        ".ipa",  # iOS app package (ZIP container)
        ".zargo", # ArgoUML ZIP project
        ".xap",  # Old Windows Phone apps
        ".oxt",  # OpenOffice Extension
        ".wsz",  # Winamp skin (ZIP archive)
        ".gdoc", # Google Docs shortcut (non-ZIP but testable)
        ".szip", # Made-up or spoof extension
    ]

    for ext in niche_exts:
        make_zip("base.zip")
        renamed = f"{CORPUS_DIR}/zip_as{ext}.zip"
        os.rename("base.zip", renamed)

    print(f"✅ Done! Niche-extension ZIPs are in ./{CORPUS_DIR}/")

def cleanup():
    if os.path.exists(SAMPLE_FILE):
        os.remove(SAMPLE_FILE)
    if os.path.exists("base.zip"):
        os.remove("base.zip")

if __name__ == "__main__":
    create_sample()
    generate_niche_extensions()
    cleanup()

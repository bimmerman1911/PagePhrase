# PagePhrase Offline PDF Translator

A cross-platform Python desktop app (Windows + Linux) to translate **PDF to PDF** from the terminal.

It uses:
- **PyMuPDF** for PDF parsing/writing.
- **Argos Translate** for offline translation models.
- **Tkinter** for a simple modern desktop GUI.

> The app is designed to preserve original layout/images as much as possible by editing text spans in-place.

---

## Quick Start (Copy/Paste)

If you just want commands you can paste directly, use one of these blocks.

### Linux (bash)

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt

# Install one Argos model pair (example: English -> French)
python3 - <<'PY'
from argostranslate import package

FROM_CODE = "en"
TO_CODE = "fr"

package.update_package_index()
available = package.get_available_packages()
match = next((p for p in available if p.from_code == FROM_CODE and p.to_code == TO_CODE), None)
if not match:
    raise SystemExit(f"No package found for {FROM_CODE}->{TO_CODE}")
path = match.download()
package.install_from_path(path)
print(f"Installed Argos model: {FROM_CODE}->{TO_CODE}")
PY

python3 app.py
```

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

# Install one Argos model pair (example: English -> French)
python -c "from argostranslate import package; FROM='en'; TO='fr'; package.update_package_index(); pkg=next((p for p in package.get_available_packages() if p.from_code==FROM and p.to_code==TO), None); path=pkg.download() if pkg else (_ for _ in ()).throw(SystemExit(f'No package found for {FROM}->{TO}')); package.install_from_path(path); print(f'Installed Argos model: {FROM}->{TO}')"

python app.py
```

> Want a different language pair? Change `FROM_CODE` / `TO_CODE` (Linux block) or `FROM` / `TO` (Windows block), e.g. `en` -> `es`, `de` -> `en`, etc.

---

## 1) Prerequisites

- Windows 10/11 **or** Linux (Ubuntu/Debian/Fedora/Arch should all work)
- Python 3.10+ installed and available in terminal (`python` or `python3`)
- Tkinter available in your Python install (usually included on Windows, may need package install on Linux)

Check:

**Windows (PowerShell)**
```powershell
python --version
```

**Linux (bash)**
```bash
python3 --version
```

### Linux package notes (Tkinter + venv)

If needed, install prerequisites first:

**Ubuntu / Debian**
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-tk
```

**Fedora**
```bash
sudo dnf install -y python3 python3-tkinter
```

**Arch Linux**
```bash
sudo pacman -S --needed python tk
```

---

## 2) Get the project

If you already have this folder, open terminal in it. Otherwise:

**Windows (PowerShell)**
```powershell
git clone <your-repo-url>
cd PagePhrase
```

**Linux (bash)**
```bash
git clone <your-repo-url>
cd PagePhrase
```

---

## 3) Create and activate a virtual environment

**Windows (PowerShell)**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux (bash)**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 4) Install dependencies

**Windows (PowerShell)**
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Linux (bash)**
```bash
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 5) Install offline Argos language models

Argos needs local language model files (`.argosmodel`) installed.

### Option A: You already have `.argosmodel` files (fully offline)

Install each model file:

**Windows example**
```powershell
python -m argostranslate.package install C:\path\to\translate-en_fr.argosmodel
```

**Linux example**
```bash
python3 -m argostranslate.package install /path/to/translate-en_fr.argosmodel
```

### Option B: Download + install from terminal

Use the copy/paste blocks in **Quick Start (Copy/Paste)** above.

---

## 6) Run the app from terminal

**Windows (PowerShell)**
```powershell
python app.py
```

**Linux (bash)**
```bash
python3 app.py
```

---

## 7) Use the GUI

1. Click **Browse** and select input `.pdf`.
2. Click **Save As** and choose output `.pdf` path.
3. Select **From Language** and **To Language**.
4. Click **Translate PDF**.

---

## Notes / limitations

- Best results come from machine-readable PDFs (not scanned images).
- Complex layouts are preserved as much as possible, but no tool can guarantee perfect typography parity in every PDF.
- The app only uses installed offline translation models.
- If a PDF has only images (for example, scanner output), the app now reports:
  "No machine-readable text was found... Use OCR first, then run translation again."

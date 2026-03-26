# PagePhrase Offline PDF Translator

A Windows-friendly Python desktop app to translate **PDF to PDF** from the terminal.

It uses:
- **PyMuPDF** for PDF parsing/writing.
- **Argos Translate** for offline translation models.
- **Tkinter** for a simple modern desktop GUI.

> The app is designed to preserve original layout/images as much as possible by editing text spans in-place.

---

## 1) Prerequisites

- Windows 10/11
- Python 3.10+ installed and available in terminal as `python`

Check:

```powershell
python --version
```

---

## 2) Get the project

If you already have this folder, open terminal in it. Otherwise:

```powershell
git clone <your-repo-url>
cd PagePhrase
```

---

## 3) Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

---

## 4) Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 5) Install offline Argos language models

Argos needs local language model files (`.argosmodel`) installed.

### Option A: You already have `.argosmodel` files (fully offline)

Install each model file:

```powershell
python -m argostranslate.package install C:\path\to\translate-en_fr.argosmodel
```

### Option B: Download model files first, then install locally

If your machine has internet once, download the model file(s), move them to your offline machine, then run the same install command above.

---

## 6) Run the app from terminal

```powershell
python app.py
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

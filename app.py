import os
import threading
import platform
import logging
import traceback
from pathlib import Path
import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, messagebox
from tkinter import ttk

import fitz  # PyMuPDF
from argostranslate import translate


class PDFTranslatorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("PagePhrase Offline PDF Translator")
        self.root.geometry("860x560")
        self.root.minsize(760, 500)
        self.ui_font = self._pick_font_family()

        self.style = ttk.Style()
        if "vista" in self.style.theme_names():
            self.style.theme_use("vista")
        elif "clam" in self.style.theme_names():
            self.style.theme_use("clam")

        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.status = tk.StringVar(value="Ready")
        self.progress = tk.DoubleVar(value=0)

        self.language_map = self._load_installed_languages()
        self.from_lang = tk.StringVar()
        self.to_lang = tk.StringVar()

        if self.language_map:
            first = next(iter(self.language_map.keys()))
            self.from_lang.set(first)
            self.to_lang.set(first)

        self.run_logger = None
        self.run_log_handler = None
        self.run_log_path = None

        self._build_ui()

    def _start_verbose_log(self, output_pdf_path: str):
        output_path = Path(output_pdf_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        log_path = output_path.with_suffix(".log")
        logger_name = f"PagePhraseRun-{id(self)}"
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        logger.handlers.clear()
        logger.propagate = False

        handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(handler)

        self.run_logger = logger
        self.run_log_handler = handler
        self.run_log_path = str(log_path)
        logger.info("Verbose translation log started.")
        logger.info("Input PDF: %s", self.input_file.get().strip())
        logger.info("Output PDF: %s", output_pdf_path)
        logger.info("From language: %s", self.from_lang.get())
        logger.info("To language: %s", self.to_lang.get())

    def _stop_verbose_log(self):
        if self.run_log_handler and self.run_logger:
            self.run_logger.info("Verbose translation log finished.")
            self.run_logger.removeHandler(self.run_log_handler)
            self.run_log_handler.close()
        self.run_log_handler = None
        self.run_logger = None

    def _load_installed_languages(self):
        langs = {}
        for lang in translate.get_installed_languages():
            name = f"{lang.name} ({lang.code})"
            langs[name] = lang
        return dict(sorted(langs.items()))

    def _pick_font_family(self):
        system = platform.system().lower()
        available = set(tkfont.families(self.root))

        if system == "windows":
            preferred = ["Segoe UI", "Arial", "TkDefaultFont"]
        elif system == "linux":
            preferred = ["Noto Sans", "Ubuntu", "DejaVu Sans", "Liberation Sans", "TkDefaultFont"]
        else:
            preferred = ["Arial", "Helvetica", "TkDefaultFont"]

        for family in preferred:
            if family in available:
                return family
        return "TkDefaultFont"

    def _build_ui(self):
        container = ttk.Frame(self.root, padding=24)
        container.pack(fill="both", expand=True)

        title = ttk.Label(
            container,
            text="Offline PDF Translator",
            font=(self.ui_font, 22, "bold"),
        )
        title.pack(anchor="w")

        subtitle = ttk.Label(
            container,
            text="Translate PDF text offline while preserving layout and images as much as possible.",
            font=(self.ui_font, 10),
        )
        subtitle.pack(anchor="w", pady=(4, 20))

        card = ttk.Frame(container, padding=18)
        card.pack(fill="both", expand=True)

        # Input PDF
        ttk.Label(card, text="Input PDF", font=(self.ui_font, 10, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Entry(card, textvariable=self.input_file).grid(row=1, column=0, sticky="ew", padx=(0, 10))
        ttk.Button(card, text="Browse", command=self.pick_input).grid(row=1, column=1, sticky="ew")

        # Output PDF
        ttk.Label(card, text="Output PDF", font=(self.ui_font, 10, "bold")).grid(row=2, column=0, sticky="w", pady=(20, 0))
        ttk.Entry(card, textvariable=self.output_file).grid(row=3, column=0, sticky="ew", padx=(0, 10))
        ttk.Button(card, text="Save As", command=self.pick_output).grid(row=3, column=1, sticky="ew")

        # Languages
        ttk.Label(card, text="From Language", font=(self.ui_font, 10, "bold")).grid(row=4, column=0, sticky="w", pady=(20, 0))
        self.from_combo = ttk.Combobox(card, textvariable=self.from_lang, state="readonly")
        self.from_combo["values"] = list(self.language_map.keys())
        self.from_combo.grid(row=5, column=0, sticky="ew", padx=(0, 10))

        ttk.Label(card, text="To Language", font=(self.ui_font, 10, "bold")).grid(row=4, column=1, sticky="w", pady=(20, 0))
        self.to_combo = ttk.Combobox(card, textvariable=self.to_lang, state="readonly")
        self.to_combo["values"] = list(self.language_map.keys())
        self.to_combo.grid(row=5, column=1, sticky="ew")

        # Controls
        controls = ttk.Frame(card)
        controls.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(24, 0))
        controls.columnconfigure(0, weight=1)

        self.translate_btn = ttk.Button(controls, text="Translate PDF", command=self.start_translate)
        self.translate_btn.grid(row=0, column=0, sticky="ew")

        self.progress_bar = ttk.Progressbar(card, variable=self.progress, maximum=100)
        self.progress_bar.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(18, 8))

        self.status_label = ttk.Label(card, textvariable=self.status)
        self.status_label.grid(row=8, column=0, columnspan=2, sticky="w")

        tip = ttk.Label(
            card,
            text=(
                "Tip: Install Argos language models first (offline .argosmodel files supported). "
                "The app uses only installed/offline models."
            ),
            foreground="#555555",
        )
        tip.grid(row=9, column=0, columnspan=2, sticky="w", pady=(18, 0))

        card.columnconfigure(0, weight=1)
        card.columnconfigure(1, weight=1)

    def pick_input(self):
        path = filedialog.askopenfilename(
            title="Select input PDF",
            filetypes=[("PDF files", "*.pdf")],
        )
        if path:
            self.input_file.set(path)
            default_output = str(Path(path).with_name(f"{Path(path).stem}_translated.pdf"))
            self.output_file.set(default_output)

    def pick_output(self):
        path = filedialog.asksaveasfilename(
            title="Select output PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
        )
        if path:
            self.output_file.set(path)

    def validate(self):
        if not self.language_map:
            messagebox.showerror(
                "No offline language models",
                "No Argos Translate languages are installed. Install language models first.",
            )
            return False

        source = self.input_file.get().strip()
        target = self.output_file.get().strip()

        if not source or not os.path.isfile(source):
            messagebox.showerror("Invalid input", "Please select a valid input PDF file.")
            return False

        if not target:
            messagebox.showerror("Invalid output", "Please select an output PDF file.")
            return False

        if self.from_lang.get() == self.to_lang.get():
            messagebox.showerror("Invalid language pair", "From and To languages must be different.")
            return False

        return True

    def start_translate(self):
        if not self.validate():
            return

        self.translate_btn.configure(state="disabled")
        self.progress.set(0)
        self.status.set("Starting translation...")

        worker = threading.Thread(target=self.translate_pdf, daemon=True)
        worker.start()

    def translate_pdf(self):
        try:
            in_path = self.input_file.get().strip()
            out_path = self.output_file.get().strip()
            self._start_verbose_log(out_path)

            from_language = self.language_map[self.from_lang.get()]
            to_language = self.language_map[self.to_lang.get()]
            translator = from_language.get_translation(to_language)
            if translator is None:
                raise RuntimeError(
                    "No installed offline model for this language pair. "
                    "Install a matching Argos model."
                )

            self.run_logger.info("Translator initialized successfully.")

            doc = fitz.open(in_path)
            total_pages = len(doc)
            translation_cache = {}
            translated_span_count = 0
            total_span_count = 0
            cache_hits = 0
            cache_misses = 0
            self.run_logger.info("Loaded PDF with %s page(s).", total_pages)

            for p_index, page in enumerate(doc):
                blocks = page.get_text("dict").get("blocks", [])
                page_span_count = 0
                page_translated_count = 0
                page_redaction_count = 0
                page_insert_fail_count = 0
                page_insert_retry_count = 0
                translated_items = []

                for block in blocks:
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            text = span.get("text", "")
                            if not text.strip():
                                continue

                            total_span_count += 1
                            page_span_count += 1

                            if text in translation_cache:
                                translated = translation_cache[text]
                                cache_hits += 1
                            else:
                                translated = translator.translate(text)
                                translation_cache[text] = translated
                                cache_misses += 1

                            bbox = fitz.Rect(span["bbox"])
                            font_size = max(6, float(span.get("size", 10)))

                            page.add_redact_annot(bbox, fill=False)
                            page_redaction_count += 1
                            translated_items.append(
                                {
                                    "bbox": bbox,
                                    "translated": translated,
                                    "font_size": font_size,
                                    "original_text": text,
                                }
                            )
                            translated_span_count += 1
                            page_translated_count += 1

                if page_redaction_count:
                    page.apply_redactions()

                for item in translated_items:
                    bbox = item["bbox"]
                    translated = item["translated"]
                    font_size = item["font_size"]
                    original_text = item["original_text"]
                    insert_result = -1
                    retry_sizes = [font_size, max(4, font_size - 1), max(4, font_size - 2)]
                    for idx, retry_size in enumerate(retry_sizes):
                        insert_result = page.insert_textbox(
                            bbox,
                            translated,
                            fontsize=retry_size,
                            color=(0, 0, 0),
                            align=fitz.TEXT_ALIGN_LEFT,
                        )
                        if insert_result >= 0:
                            break
                        if idx > 0:
                            page_insert_retry_count += 1

                    if insert_result < 0:
                        fallback_point = fitz.Point(bbox.x0, bbox.y1 - 1)
                        fallback_size = max(4, font_size - 2)
                        try:
                            page.insert_text(
                                fallback_point,
                                translated,
                                fontsize=fallback_size,
                                color=(0, 0, 0),
                            )
                            page_insert_retry_count += 1
                        except Exception:
                            page_insert_fail_count += 1
                            self.run_logger.warning(
                                "Textbox insert failed on page %s | bbox=%s | font=%.2f | text=%r | translated=%r",
                                p_index + 1,
                                tuple(round(v, 2) for v in bbox),
                                font_size,
                                original_text[:120],
                                translated[:120],
                            )

                percent = ((p_index + 1) / total_pages) * 100
                self.run_logger.info(
                    "Page %s/%s complete | text spans seen: %s | translated spans: %s | redactions: %s | insert retries: %s | insert failures: %s",
                    p_index + 1,
                    total_pages,
                    page_span_count,
                    page_translated_count,
                    page_redaction_count,
                    page_insert_retry_count,
                    page_insert_fail_count,
                )
                self.root.after(0, self.progress.set, percent)
                self.root.after(
                    0,
                    self.status.set,
                    f"Translated page {p_index + 1}/{total_pages}",
                )

            if translated_span_count == 0:
                raise RuntimeError(
                    "No machine-readable text was found in this PDF. "
                    "This file is likely image-only/scanned, so there is nothing to translate. "
                    "Use OCR first, then run translation again."
                )

            doc.save(out_path)
            doc.close()
            self.run_logger.info(
                "Saved translated PDF. Totals | spans seen: %s | translated: %s | cache hits: %s | cache misses: %s",
                total_span_count,
                translated_span_count,
                cache_hits,
                cache_misses,
            )

            self.root.after(0, self.status.set, f"Done: {out_path}")
            self.root.after(
                0,
                messagebox.showinfo,
                "Translation complete",
                f"PDF translation completed successfully.\nVerbose log: {self.run_log_path}",
            )
        except Exception as exc:
            if self.run_logger:
                self.run_logger.error("Translation failed: %s", exc)
                self.run_logger.error(traceback.format_exc())
            self.root.after(0, self.status.set, "Translation failed")
            if self.run_log_path:
                error_message = f"{exc}\n\nVerbose log: {self.run_log_path}"
            else:
                error_message = str(exc)
            self.root.after(0, messagebox.showerror, "Error", error_message)
        finally:
            self._stop_verbose_log()
            self.root.after(0, self.translate_btn.configure, {"state": "normal"})


def main():
    root = tk.Tk()
    app = PDFTranslatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

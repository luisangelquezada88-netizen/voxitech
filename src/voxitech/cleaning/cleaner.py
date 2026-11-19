"""Limpieza de texto crudo: eliminación de boilerplate, scripts, menús, publicidad y artefactos de scraping."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

from voxitech.cleaning.language import detect_language, is_supported_language
from voxitech.cleaning.normalizers import normalize_text
from voxitech.utils.hashing import sha256_text
from voxitech.utils.logging import get_logger

logger = get_logger()


@dataclass
class CleaningResult:
    """Resultado del proceso de limpieza de un documento."""

    document_id: str
    source_id: str
    url: str
    raw_file_path: str
    raw_hash: str
    clean_file_path: str
    clean_hash: str
    clean_text: str
    language: str
    language_supported: bool
    word_count: int
    sentence_count: int
    paragraph_count: int
    boilerplate_ratio: float
    cleaning_log: list[str]
    quality_flags: list[str]


class Cleaner:
    """Limpia texto crudo HTML/PDF/TXT/Markdown/JSON y calcula métricas básicas."""

    # Selectores de elementos que suelen contener boilerplate (menús, anuncios, scripts, etc.)
    BOILERPLATE_SELECTORS = [
        "script",
        "style",
        "nav",
        "header",
        "footer",
        "aside",
        ".menu",
        ".navigation",
        ".nav",
        ".advertisement",
        ".ad",
        ".ads",
        ".sidebar",
        ".widget",
        ".social-share",
        ".cookie-banner",
        ".newsletter",
        ".related-articles",
        ".comments",
        "#comments",
        ".search",
        "#search",
    ]

    def __init__(self, interim_root: str | Path = "data/interim") -> None:
        self.interim_root = Path(interim_root)

    def _extract_text_from_html(self, html: str) -> tuple[str, list[str]]:
        """Extrae texto principal de HTML eliminando boilerplate.

        Returns:
            Texto limpio y lista de entradas de log.
        """
        log: list[str] = []
        soup = BeautifulSoup(html, "lxml")

        # Eliminar elementos de boilerplate por selector
        removed_count = 0
        for selector in self.BOILERPLATE_SELECTORS:
            elements = soup.select(selector)
            for el in elements:
                el.decompose()
                removed_count += 1
        log.append(f"Elementos de boilerplate eliminados: {removed_count}")

        # Intentar extraer el contenido principal (main, article, o body como fallback)
        main = soup.find("main") or soup.find("article") or soup.find("body")
        if main is None:
            log.append("No se encontró elemento <main>, <article> ni <body>; usando todo el documento")
            text = soup.get_text(separator="\n")
        else:
            text = main.get_text(separator="\n")

        log.append(f"Texto extraído de HTML: {len(text)} caracteres antes de normalización")
        return text, log

    def _extract_text_from_pdf(self, pdf_bytes: bytes) -> tuple[str, list[str]]:
        """Extrae texto de PDF usando pdfplumber con fallback a PyMuPDF."""
        log: list[str] = []
        text = ""

        try:
            import pdfplumber

            from io import BytesIO

            with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
                pages = []
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text() or ""
                    pages.append(page_text)
                text = "\n".join(pages)
            log.append(f"PDF extraído con pdfplumber: {len(pdf.pages)} páginas")
        except Exception as exc:  # noqa: BLE001
            log.append(f"pdfplumber falló: {exc}; intentando PyMuPDF")
            try:
                import fitz  # PyMuPDF

                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                pages = [page.get_text() for page in doc]
                text = "\n".join(pages)
                log.append(f"PDF extraído con PyMuPDF: {doc.page_count} páginas")
            except Exception as exc2:  # noqa: BLE001
                log.append(f"PyMuPDF también falló: {exc2}")
                text = ""

        return text, log

    def _extract_text_from_raw(self, content: bytes, content_type: str | None) -> tuple[str, list[str]]:
        """Extrae texto según el tipo de contenido."""
        log: list[str] = []

        if content_type and "application/pdf" in content_type.lower():
            text, pdf_log = self._extract_text_from_pdf(content)
            log.extend(pdf_log)
            return text, log

        # Por defecto, tratar como HTML (el caso más común en whitehouse.gov)
        html = content.decode("utf-8", errors="replace")
        log.append(f"Contenido decodido como HTML/texto: {len(html)} caracteres")
        text, html_log = self._extract_text_from_html(html)
        log.extend(html_log)
        return text, log

    def _count_sentences(self, text: str) -> int:
        """Cuenta oraciones aproximadas dividiendo por . ! ? seguidas de espacio o fin."""
        if not text:
            return 0
        parts = re.split(r"[.!?]+[\s\n]+", text)
        return len([p for p in parts if p.strip()])

    def _count_paragraphs(self, text: str) -> int:
        """Cuenta párrafos no vacíos."""
        return len([p for p in text.split("\n") if p.strip()])

    def clean(
        self,
        document_id: str,
        source_id: str,
        url: str,
        raw_file_path: str,
        raw_hash: str,
        content: bytes,
        content_type: str | None = None,
    ) -> CleaningResult:
        """Limpia un documento crudo y devuelve el resultado completo.

        Guarda el texto limpio en data/interim/{document_id}_clean.txt.
        """
        log: list[str] = []
        quality_flags: list[str] = []

        # 1. Extraer texto según tipo de contenido
        extracted_text, extraction_log = self._extract_text_from_raw(content, content_type)
        log.extend(extraction_log)

        if not extracted_text or not extracted_text.strip():
            log.append("ADVERTENCIA: No se pudo extraer texto del documento")
            quality_flags.append("no_text_extracted")
            clean_text = ""
        else:
            # 2. Normalizar texto
            clean_text = normalize_text(extracted_text)
            log.append(f"Texto después de normalización: {len(clean_text)} caracteres")

        # 3. Detectar idioma
        language = detect_language(clean_text)
        language_supported = is_supported_language(language)
        log.append(f"Idioma detectado: {language} (soportado: {language_supported})")

        if not language_supported:
            quality_flags.append("unsupported_language")

        # 4. Métricas básicas
        word_count = len(clean_text.split()) if clean_text else 0
        sentence_count = self._count_sentences(clean_text) if clean_text else 0
        paragraph_count = self._count_paragraphs(clean_text) if clean_text else 0
        log.append(f"Palabras: {word_count}, Oraciones: {sentence_count}, Párrafos: {paragraph_count}")

        if word_count == 0:
            quality_flags.append("zero_word_count")

        # 5. Calcular ratio de boilerplate aproximado
        # Si el texto crudo era HTML, comparamos longitudes como indicador aproximado
        boilerplate_ratio = 0.0
        if content_type and "text/html" in str(content_type).lower():
            raw_len = len(content.decode("utf-8", errors="replace"))
            clean_len = len(clean_text)
            if raw_len > 0:
                boilerplate_ratio = max(0.0, 1.0 - (clean_len / raw_len))
            log.append(f"Ratio aproximado de boilerplate: {boilerplate_ratio:.2f}")
            if boilerplate_ratio > 0.70:
                quality_flags.append("high_boilerplate_ratio")

        # 6. Guardar texto limpio
        self.interim_root.mkdir(parents=True, exist_ok=True)
        clean_file_name = f"{document_id}_clean.txt"
        clean_file_path = self.interim_root / clean_file_name
        clean_file_path.write_text(clean_text, encoding="utf-8")
        clean_hash = sha256_text(clean_text)
        log.append(f"Texto limpio guardado en: {clean_file_path} (hash={clean_hash})")

        # 7. Validación de calidad mínima
        if word_count < 100:
            quality_flags.append("low_word_count")

        return CleaningResult(
            document_id=document_id,
            source_id=source_id,
            url=url,
            raw_file_path=raw_file_path,
            raw_hash=raw_hash,
            clean_file_path=str(clean_file_path),
            clean_hash=clean_hash,
            clean_text=clean_text,
            language=language,
            language_supported=language_supported,
            word_count=word_count,
            sentence_count=sentence_count,
            paragraph_count=paragraph_count,
            boilerplate_ratio=boilerplate_ratio,
            cleaning_log=log,
            quality_flags=quality_flags,
        )
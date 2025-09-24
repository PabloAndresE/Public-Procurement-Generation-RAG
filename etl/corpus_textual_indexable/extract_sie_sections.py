import zipfile
import io
import fitz  # PyMuPDF
import re
import csv
from datetime import datetime
from pathlib import Path

# Ruta base donde están los .ushay
BASE_DIR = Path("./data_raw/ushay")
OUTPUT_PATH = Path("./data_curated/corpus_textual_indexable/corpus_indexable.csv")
INDEX_PATH = Path("./data_curated/corpus_textual_indexable/ushay_contents_index.csv")
EXTRACTION_DIR = Path("./data_extracted")
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
EXTRACTION_DIR.mkdir(parents=True, exist_ok=True)

# Patrones basados en el modelo oficial SIE
SECTION_PATTERNS = {
    "CONVOCATORIA": re.compile(r"(SECCION\s+I|1\.|I\.)\s*(CONVOCATORIA)", re.IGNORECASE),
    "OBJETO_CONTRATACION": re.compile(r"(SECCION\s+II|2\.|II\.)\s*(OBJETO)", re.IGNORECASE),
    "CONDICIONES_PROCEDIMIENTO": re.compile(r"(SECCION\s+III|3\.|III\.)\s*(CONDICIONES)", re.IGNORECASE),
    "VERIFICACION_EVALUACION": re.compile(r"(SECCION\s+IV|4\.|IV\.)\s*(VERIFICACION|EVALUACION)", re.IGNORECASE),
    "PUJA": re.compile(r"(SECCION\s+V|5\.|V\.)\s*PUJA", re.IGNORECASE),
    "OBLIGACIONES_PARTES": re.compile(r"(SECCION\s+VI|6\.|VI\.)\s*OBLIGACIONES", re.IGNORECASE),
    "FORMULARIOS": re.compile(r"FORMULARIO(S)?", re.IGNORECASE),
}

def extract_pdf_from_ushay(ushay_path: Path, index_list: list):
    ushay_bytes = ushay_path.read_bytes()
    zip_offset = ushay_bytes.find(b"PK\x03\x04")
    if zip_offset == -1:
        return [], None
    zip_bytes = ushay_bytes[zip_offset:]
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        nombres = zf.namelist()
        print(f"\nARCHIVO: {ushay_path.name}")
        
        # Crear carpeta para este ushay
        folder_name = EXTRACTION_DIR / ushay_path.stem.replace(" ", "_")
        folder_name.mkdir(parents=True, exist_ok=True)
        
        for name in nombres:
            print(f" └── {name}")
            index_list.append({
                "archivo_ushay": ushay_path.name,
                "archivo_interno": name
            })
            # Extraer archivo a carpeta correspondiente
            extracted_path = folder_name / Path(name).name
            with open(extracted_path, "wb") as f_out:
                f_out.write(zf.read(name))
        
        # Buscar PDF relevante
        for name in nombres:
            if ("pli" in name.lower() or "tecnicas" in name.lower()) and (name.lower().endswith(".pdf") or name.lower().endswith(".doc")) :
                return zf.read(name), name
    return [], None

def extract_sections_from_pdf(pdf_bytes, proceso_id, archivo_pdf):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    secciones = []
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text()
        for seccion, pattern in SECTION_PATTERNS.items():
            if pattern.search(text):
                secciones.append({
                    "proceso_id": proceso_id,
                    "seccion": seccion,
                    "texto_original": text.strip().replace("\n", " "),
                    "pagina": page_num,
                    "archivo_pdf": archivo_pdf,
                    "fecha_extraccion": datetime.today().strftime("%Y-%m-%d")
                })
    return secciones

def main():
    corpus = []
    index = []

    for ushay_path in BASE_DIR.glob("*.ushay"):
        proceso_id = ushay_path.stem.replace(".ushay", "")
        pdf_bytes, archivo_pdf = extract_pdf_from_ushay(ushay_path, index)
        print(f"\nPDF: {archivo_pdf}")
        if not pdf_bytes:
            continue
        secciones = extract_sections_from_pdf(pdf_bytes, proceso_id, archivo_pdf)
        corpus.extend(secciones)

    # Guardar corpus principal
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["proceso_id", "seccion", "texto_original", "pagina", "archivo_pdf", "fecha_extraccion"])
        writer.writeheader()
        writer.writerows(corpus)
    print(f"\n * Corpus SIE guardado en: {OUTPUT_PATH}")

    # Guardar índice auxiliar
    with open(INDEX_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["archivo_ushay", "archivo_interno"])
        writer.writeheader()
        writer.writerows(index)
    print(f" * Índice de contenidos guardado en: {INDEX_PATH}")

if __name__ == "__main__":
    main()

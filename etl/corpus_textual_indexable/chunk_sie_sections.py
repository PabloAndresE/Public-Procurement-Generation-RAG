import pandas as pd
from pathlib import Path
from uuid import uuid4
import spacy
import subprocess
from spacy.util import is_package

# Configuración del modelo SpaCy
model_name = "es_core_news_sm"

if not is_package(model_name):
    print(f" * Modelo '{model_name}' no encontrado. Instalando...")
    subprocess.run(["python", "-m", "spacy", "download", model_name], check=True)

nlp = spacy.load(model_name)

# Paths de entrada/salida
INPUT_PATH = Path("./data_curated/corpus_textual_indexable/corpus_indexable_clean.csv")
OUTPUT_PATH = Path("./data_curated/corpus_textual_indexable/corpus_indexable_chunks_tokens.csv")

# Parámetros de chunking
MAX_TOKENS = 80
OVERLAP = 10


# Función para dividir por tokens
def split_by_tokens(text, max_tokens=MAX_TOKENS, overlap=OVERLAP):
    doc = nlp(text)
    tokens = [t.text for t in doc]  # lista de tokens
    chunks = []
    i = 0

    while i < len(tokens):
        window = tokens[i:i + max_tokens]
        chunks.append(" ".join(window))
        i += max_tokens - overlap  # ventana deslizante con solapamiento
    return chunks


# 🔹 Pipeline principal
def main():
    df = pd.read_csv(INPUT_PATH)
    records = []

    for _, row in df.iterrows():
        texto = row.get("texto_original", "")
        print(f" * Procesando fila {row.get('proceso_id')}")
        print(f" * Texto: {texto}")
        if not isinstance(texto, str) or not texto.strip():
            continue

        try:
            chunks = split_by_tokens(texto)
        except Exception as e:
            print(f" * Error procesando fila {row.get('proceso_id')}: {e}")
            continue

        for ix, chunk in enumerate(chunks):
            records.append({
                "chunk_id": str(uuid4()),
                "proceso_id": row.get("proceso_id", ""),
                "seccion": row.get("seccion", ""),
                "chunk_index": ix,
                "texto_chunk": chunk,
                "tokens_count": len(chunk.split()),
                "archivo_pdf": row.get("archivo_pdf", ""),
                "archivo_ushay": row.get("archivo_ushay", ""),
                "pagina": row.get("pagina", ""),
                "fecha_extraccion": row.get("fecha_extraccion", "")
            })

    pd.DataFrame(records).to_csv(OUTPUT_PATH, index=False)
    print(f" *  Corpus segmentado por tokens guardado en: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

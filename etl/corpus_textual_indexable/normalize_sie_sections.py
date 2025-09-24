import pandas as pd
import re
from pathlib import Path

INPUT_PATH = Path("./data_curated/corpus_textual_indexable/corpus_indexable.csv")
OUTPUT_PATH = Path("./data_curated/corpus_textual_indexable/corpus_indexable_clean.csv")

def limpiar_texto(texto):
    if pd.isna(texto):
        return ""
    texto = texto.replace("\n", " ").replace("\r", " ").strip()
    texto = re.sub(r"\s{2,}", " ", texto)  # reducir espacios múltiples
    texto = re.sub(r"(firma(\s+electr[oó]nica)?)+.*", "", texto, flags=re.IGNORECASE)  # remover firma
    texto = re.sub(r"Página\s*\d+(\s+de\s+\d+)?", "", texto, flags=re.IGNORECASE)  # remover paginación
    texto = re.sub(r"[•·◆►▶]", "-", texto)  # bullets decorativos
    return texto.strip()

def main():
    df = pd.read_csv(INPUT_PATH)
    if "texto_original" in df.columns:
        df["texto_original"] = df["texto_original"].apply(limpiar_texto)
    else:
        print(" * No se encontró la columna 'texto_original'")
        return
    df.to_csv(OUTPUT_PATH, index=False)
    print(f" * Corpus limpio guardado en: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
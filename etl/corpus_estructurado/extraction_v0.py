#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETL v0 — .ushay → Corpus Mínimo Viable (CMV)
- Detecta ZIP embebido dentro de archivos .ushay (firma 'PK\x03\x04')
- Extrae 'proceso.xml'
- Decodifica campos Base64 (cuando aplica)
- Exporta CSV con subconjunto de campos clave (CMV)
"""

import io, zipfile, xml.etree.ElementTree as ET, base64, re
import argparse, pandas as pd, json
from pathlib import Path

KEYS_WANTED = [
    "COD_PROC","IDENTIFICADOR","CAT_PLIEGO_ID","CAT_PLIEGO_NOMBRE","FECHA","DESCRIPCION",
    "RUC","NOMBRE_ENTID_CONTRAT","PROVINCIA_COD","CANTON_COD","PARROQUIA_COD",
    "CALLE_PRINCIPAL","CALLE_SECUNDARIA","REFERENCIA","CORREO","TELEFONO","SITIO_WEB",
    "OBJETO","OBJETO_CONTRATO","PRESUPUESTO","PRESUPUESTO_REFERENCIAL","PLAZO","PLAZO_EJECUCION"
]

def try_b64_decode(s: str):
    """Heurística simple para decodificar Base64 (incluye variante con '_')."""
    if s is None:
        return None
    s = s.strip()
    if re.fullmatch(r'[A-Za-z0-9+/=\s\-_]+', s) and len(s.replace(" ", "").replace("\n","")) % 4 == 0:
        try:
            raw = base64.b64decode(s.replace("_","/"))
            for enc in ("utf-8","latin-1"):
                try:
                    return raw.decode(enc)
                except Exception:
                    pass
            return raw
        except Exception:
            return s
    return s

def extract_fields_from_xml(xml_bytes: bytes, keys=KEYS_WANTED):
    """Parsea XML y devuelve dict con los campos de interés (decodificados cuando corresponda)."""
    root = ET.fromstring(xml_bytes)
    fields = {}
    for el in root.iter():
        tag = el.tag.strip()
        txt = el.text.strip() if el.text else ""
        val = try_b64_decode(txt) if txt else ""
        if isinstance(val, (bytes, bytearray)):
            continue
        if val:
            fields[tag] = val
    return {k: fields.get(k, "") for k in fields}

def parse_ushay(ushay_path: Path):
    """Devuelve (meta, fields) a partir de un archivo .ushay."""
    data = ushay_path.read_bytes()
    idx = data.find(b"PK\x03\x04")
    result = {
        "file": ushay_path.name,
        "size_bytes": len(data),
        "pk_offset": idx,
        "zip_ok": False,
        "n_adjuntos": 0,
        "has_proceso_xml": False,
        "error": ""
    }
    if idx == -1:
        result["error"] = "No ZIP signature found"
        return result, {}
    zdata = data[idx:]
    try:
        with zipfile.ZipFile(io.BytesIO(zdata)) as zf:
            names = zf.namelist()
            result["zip_ok"] = True
            adjuntos = [n for n in names if n.lower() not in ("proceso.xml","zip.info","escudo.jpg")]
            result["n_adjuntos"] = len(adjuntos)
            if "proceso.xml" in names:
                result["has_proceso_xml"] = True
                xml_bytes = zf.read("proceso.xml")
                fields = extract_fields_from_xml(xml_bytes)
                return result, fields
            else:
                result["error"] = "proceso.xml not found"
                return result, {}
    except Exception as e:
        result["error"] = str(e)
        return result, {}

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="ETL v0 — .ushay → CSV (CMV)")
    ap.add_argument("--input_glob", required=True, help="Patrón glob de entrada, p.ej. 'data_raw/ushay/*.ushay'")
    ap.add_argument("--out_csv", required=True, help="Ruta del CSV de salida")
    args = ap.parse_args()
    from glob import glob
    rows = []
    metas = []
    for p in glob(args.input_glob):
        meta, fields = parse_ushay(Path(p))
        metas.append(meta)
        row = {"file": Path(p).name}
        row.update(fields)
        rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv(args.out_csv, index=False, encoding="utf-8")
    print(json.dumps({"processed": len(rows), "meta_sample": metas[:3]}, indent=2, ensure_ascii=False))

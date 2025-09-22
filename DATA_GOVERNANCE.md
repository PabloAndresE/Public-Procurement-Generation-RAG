# DATA_GOVERNANCE.md — Política de datos, manifiestos y snapshots

## 1. Estructura de datos
- `normativa/`: textos normativos y documentos regulatorios.
- `data_raw/ushay/`: archivos .ushay originales por proceso.
- `data_curated/`: salidas de ETL (CMV) y artefactos derivados.

## 2. Manifiestos (inventarios)
Mantener un **CSV** por origen con columnas mínimas:

### 2.1. `data_raw/ushay/manifest_ushay.csv`
`proceso_id, entidad, fecha_publicacion, modalidad, fuente_url, ruta_archivo, hash_sha256, downloaded_at`

### 2.2. `normativa/normativa_manifest.csv`
`id_norma, nombre, jurisdiccion, fecha_publicacion, version, fuente_url, ruta_archivo, hash_sha256`

> El `hash_sha256` permite validar integridad; `ruta_archivo` es relativa al repositorio.

## 3. Snapshots y releases
- No *commitear* archivos pesados al Git principal.
- Publicar **snapshots** (zips) como **releases** con el tag correspondiente (ver `VERSIONING.md`).
- Incluir un **dataset card** (`docs/dataset_card_cmv.md`) describiendo origen, cobertura temporal, variables, limitaciones y riesgos.

## 4. Calidad y cumplimiento
- Control de calidad (QC): reporte `docs/qc_corpus_cmv.md` con nulos, duplicados y consistencia.
- Reproducibilidad: scripts ETL versionados, semillas deterministas, parámetros registrados.
- Privacidad/compliance: usar **solo datos públicos**; evitar PII sensible; respetar licencias y términos de uso.

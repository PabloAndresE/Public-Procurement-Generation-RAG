# RAG para generación de pliegos SIE (Ecuador) 

Este repositorio aloja el proyecto de tesis para **generar borradores de pliegos de Subasta Inversa Electrónica (SIE)** mediante **Retrieval-Augmented Generation (RAG)**, usando **normativa vigente** y **archivos .ushay** como base de conocimiento. El sistema buscará **trazabilidad normativa** (citas) y validaciones automáticas y manuales (GUI). 

## Estructura mínima 

- `docs/` — planificación, estado del arte, informes, dataset cards y notas de release. 
- `normativa/` — textos normativos y su manifiesto (`normativa_manifest.csv`). 
- `data_raw/ushay/` — archivos `.ushay` y su manifiesto (`manifest_ushay.csv`). 
- `data_curated/` — **Corpus Mínimo Viable (CMV)** y artefactos derivados (parquet/csv). 
- `etl/` — scripts de **extracción/normalización** (ETL v0 y siguientes). 
- `notebooks/` — exploración y prototipos. 
- `app/` — GUI/servicios. 
- `eval/` — métricas, ablations y resultados. 

## Objetivo general 

Desarrollar un modelo **RAG** capaz de **generar pliegos SIE** condicionados por **evidencia normativa** y **datos de procesos (.ushay)**, con **citación automática** y **validación** (automática y vía GUI). 

## Entregables 

- **E1**: planificación v1.0; estructura del repo; Corpus minimo viable (CMV) desde `.ushay` (ETL v0); dataset card e informe técnico CMV. 

- **E2**: arquitectura RAG completa; recuperación híbrida + re-ranking; generación condicionada con citas; evaluación; GUI; documentación final. 

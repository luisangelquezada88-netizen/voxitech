# Plan de implementación — VoxiTech Lab AI

## Estado actual (Inmediato, < 3 h)
- [x] `plan.md` — hoja de ruta por fases y sprints
- [x] `notebooks/01_exploratorio_genero_trump.ipynb` — análisis exploratorio con datos de muestra (sintéticos), gráficas y exportación
- [ ] Reemplazar datos de muestra por corpus real extraído de fuentes oficiales (Fase 2)

## Fase 0: Fundación (Día 1)
- [x] Repositorio, `pyproject.toml`, `requirements*.txt`, `.env.example`, `.gitignore`, `LICENSE`
- [x] Paquete `voxitech` importable, `pytest`, `ruff`, `pre-commit`
- [x] `tests/` configurado con pruebas vacías/smoke
- [x] `config/projects/trump_gender_2025_2026.yaml` válido y cargable con Pydantic

## Fase 1: Configuración y esquemas (Día 2-3)
- [x] `config/dictionaries/en/genero_familia_v1.yaml`
- [x] `config/codebooks/trump_gender_v1.yaml`
- [ ] `config/schemas/` — esquemas de validación JSON Schema opcional
- [ ] Pruebas de carga y validación de configuración

## Fase 2: Extracción e ingesta (Día 4-6)
- [ ] `Fetcher` con reintentos, rate limit, user-agent con contacto
- [ ] Descarga de raw + sidecar JSON (URL, fecha, SHA-256, headers)
- [ ] Deduplicación por URL, hash de contenido, título+fecha+orador
- [ ] CLI `voxitech extract`

## Fase 3: Limpieza y normalización (Día 7-9)
- [ ] `Cleaner` para HTML/PDF/TXT/Markdown/JSON
- [ ] Normalizadores (espacios, comillas, guiones, UTF-8), detección de idioma
- [ ] Métricas básicas, log de limpieza por documento

## Fase 4: Segmentación y corpus maestro (Día 10-12)
- [ ] `Segmenter`: ventanas de 50-200 palabras o 1-3 párrafos
- [ ] Contexto previo/posterior, IDs determinísticos UUID5
- [ ] `corpus.parquet`, `units.parquet`

## Fase 5: Detección temática (Día 13-15)
- [ ] `DictionaryMatcher` por idioma/proyecto/tema
- [ ] Frecuencia, densidad por 1.000 palabras, contexto
- [ ] Lista priorizada de unidades para codificación humana

## Fase 6: Codificación cualitativa asistida (Día 16-18)
- [ ] Libro de códigos versionado, estados `proposed / under_review / approved / rejected`
- [ ] Revisión humana obligatoria antes de aplicar código
- [ ] Exportación matriz de codificación a CSV / Parquet / Excel

## Fase 7: Análisis cuantitativo y visualización (Día 19-21)
- [ ] Frecuencia, densidad, series temporales, coocurrencias
- [ ] Comparaciones por orador, idioma, tipo de documento, tema
- [ ] Figuras reproducibles con Matplotlib / Seaborn

## Fase 8: Reportes y dashboard (Día 22-24)
- [ ] Reportes Markdown / HTML / PDF con citas verificables
- [ ] App Streamlit para explorar corpus, filtrar y visualizar citas
- [ ] Cuadernos exploratorios en `notebooks/`

## Entregables finales
1. Repositorio técnico completo y versionado
2. Informe académico con trazabilidad de decisiones
3. Dashboard Streamlit para exploración conjunta del corpus
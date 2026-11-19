# VoxiTech Lab AI

Laboratorio reproducible de análisis de discurso asistido por IA. Permite analizar discursos públicos desde la extracción de fuentes primarias hasta la sistematización, codificación, análisis cualitativo, visualización y generación de evidencia académica.


## Estructura del repositorio

```
voxitech-lab-ai/
├── config/           # Configuraciones de proyectos, fuentes, diccionarios, libros de códigos, esquemas
├── data/             # Datos crudos, intermedios, procesados, externos y muestras
├── src/voxitech/     # Código fuente del paquete Python
├── notebooks/        # Análisis exploratorio (Jupyter)
├── tests/            # Pruebas unitarias e integración
├── docs/             # Documentación metodológica y de diseño
├── outputs/          # Figuras, reportes, exportaciones generadas
├── scripts/          # Scripts reproducibles de un solo uso
├── pyproject.toml    # Metadata y dependencias del proyecto
├── requirements.txt  # Dependencias de producción
├── requirements-dev.txt  # Dependencias de desarrollo (tests, lint, pre-commit)
├── .env.example      # Plantilla de variables de entorno (sin secretos)
├── .env              # Variables locales (gitignorado)
└── .gitignore
```

## Stack técnico

- Python 3.11+
- Pandas para manipulación de datos
- SQLite para metadatos operativos
- Parquet para corpus y tablas analíticas
- Pydantic para validación de esquemas y configuración
- Typer para CLI
- Requests, BeautifulSoup4 para extracción web
- PyMuPDF / pdfplumber para extracción de PDF
- spaCy / langdetect para idioma y NLP básico
- Matplotlib, Seaborn para visualización
- Pytest para pruebas
- Ruff para linting
- Pre-commit para calidad de código
- Streamlit opcional para exploración
- YAML para configuraciones, diccionarios y libros de códigos
- python-dotenv para variables de entorno
- Loguru para trazabilidad

## Inicio rápido

```bash
# 1. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows PowerShell

# 2. Instalar dependencias
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 3. Copiar variables de entorno
cp .env.example .env
# Editar .env con valores locales (nunca commitear .env)

# 4. Ejecutar pruebas
pytest

# 5. Abrir notebook exploratorio
jupyter notebook notebooks/01_exploratorio_genero_trump.ipynb
```

## Principios obligatorios

1. Reproducibilidad: cada transformación es rastreable a su fuente y parámetros de ejecución.
2. Trazabilidad: cada unidad textual conserva metadatos de fuente, fecha, URL, tipo de documento, orador, versión, hash de contenido y fecha de extracción.
3. Separación de responsabilidades: extracción, normalización, segmentación, detección temática, codificación, análisis, visualización y exportación están separadas.
4. Extensibilidad: múltiples oradores, organizaciones, idiomas, temas, fuentes y proyectos sin reescribir el núcleo.
5. Transparencia analítica: la IA asiste, no sustituye la lectura cualitativa humana. Toda codificación automática es revisable, corregible y exportable.
6. Ética y atribución: diferenciar discurso atribuido literalmente, comunicados institucionales, documentos firmados, transcripciones de terceros y material contextual.
7. Seguridad: ninguna clave API, token, contraseña o credencial en el repositorio.
8. Calidad de ingeniería: tests, validaciones de esquema, logs, manejo de errores, documentación y comandos reproducibles.
9. Datos como activo versionado: Parquet, CSV, JSON, SQLite o DuckDB.
10. Investigación rigurosa: libro de códigos, memorandos, evidencia textual y auditoría de decisiones.

## Licencia

MIT (por definir). Ver `LICENSE`.
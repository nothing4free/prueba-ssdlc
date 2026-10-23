# MiniBanco

MiniBanco es un banco pequeño escrito en Python. Permite crear cuentas, iniciar sesión, consultar el saldo y los movimientos, y hacer transferencias.

Todos los tests funcionales pasan. Tu trabajo es averiguar si eso basta.

## Qué necesitas

- Una cuenta de GitHub.
- Python 3.12 o superior.
- Git.

## Arranque

### 1. Crea tu copia del repositorio

> **Atención:** en el paso siguiente, marca la casilla **"Include all branches"**. Si no la marcas, tu copia no tendrá todas las ramas y no podrás hacer la segunda parte de la práctica.

1. Pulsa el botón verde **"Use this template"** y elige **"Create a new repository"**.
2. Marca **"Include all branches"**.
3. Elige tu cuenta como propietaria y deja el repositorio como **Public**.
4. Pulsa **"Create repository"**.

### 2. Clona tu copia y prepara el entorno

Sustituye `TU_USUARIO` y `TU_REPO` por los tuyos:

```bash
git clone https://github.com/TU_USUARIO/TU_REPO.git
cd TU_REPO
python -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
```

Un **entorno virtual** (`.venv`) es una carpeta con un Python propio para este proyecto. Así las librerías que instales no afectan al resto de tu equipo.

### 3. Comprueba que todo funciona

```bash
python -m minibanco               # demostración rápida
pytest tests/test_funcional.py    # todos en verde
pytest tests/test_seguridad.py    # este falla: es el punto de partida
```

## Estructura

| Ruta | Contenido |
|---|---|
| `minibanco/banco.py` | Lógica del banco. |
| `minibanco/config.py` | Configuración. |
| `tests/test_funcional.py` | Tests funcionales. |
| `tests/test_seguridad.py` | Tests de seguridad. Aquí añadirás los tuyos. |
| `REQUISITOS.md` | Qué debe hacer el banco y qué reglas de seguridad debe cumplir. |
| `HALLAZGOS.md` | Tabla para documentar los fallos que encuentres. |

## Comandos útiles

```bash
pytest -v                                     # todos los tests
pytest --cov=minibanco --cov-report=term-missing   # tests con cobertura
ruff check .                                  # estilo y errores comunes
bandit -c pyproject.toml -r minibanco         # análisis de seguridad del código
pip-audit -r requirements.txt                 # vulnerabilidades en dependencias
```

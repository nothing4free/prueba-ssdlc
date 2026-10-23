# Hallazgos

Anota aquí cada fallo que encuentres. Una fila por fallo.

| Nº | Descripción | CIA | Fase del SDLC | Test que lo demuestra | Corrección |
|---|---|---|---|---|---|
| 1 | | | | | |

## Cómo rellenar cada columna

- **Descripción:** qué ocurre y qué requisito incumple (por ejemplo, RS-01).
- **CIA:** qué propiedad se pierde. Usa una o varias de estas letras:
  - **C** (confidencialidad): alguien ve datos que no debería ver.
  - **I** (integridad): alguien cambia datos sin permiso, o los datos quedan mal.
  - **D** (disponibilidad): alguien no puede usar el sistema cuando lo necesita.
- **Fase del SDLC:** en qué fase se debió evitar el fallo: Análisis, Diseño, Codificación, Pruebas o Producción.
- **Test que lo demuestra:** nombre del test en `tests/test_seguridad.py`.
- **Corrección:** qué has cambiado en el código, en una frase.

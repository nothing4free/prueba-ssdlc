# Hallazgos

| Nº | Descripción | CIA | Fase del SDLC | Test que lo demuestra | Corrección |
|---|---|---|---|---|---|
| 1 | Se puede transferir más dinero del que hay en la cuenta. El saldo queda negativo. Incumple RS-01. | I | Codificación | `test_no_se_puede_transferir_mas_que_el_saldo` | Comprobar que el importe no supera el saldo antes de mover dinero. |
| 2 | Se aceptan importes negativos o cero. Transferir -100 € a otra cuenta le quita 100 € a esa cuenta. Incumple RS-02. | I | Codificación | `test_el_importe_debe_ser_positivo` | Rechazar importes menores o iguales que cero. |
| 3 | Si la cuenta destino no existe, el dinero sale de la cuenta origen y desaparece. Incumple RS-03. | I | Diseño | `test_transferir_a_una_cuenta_inexistente_no_pierde_dinero` | Comprobar que las dos cuentas existen antes de cambiar ningún saldo. |
| 4 | Los importes se guardan como `float`, que no representa bien los céntimos: 0,30 − 0,10 − 0,20 no da 0. Incumple RS-04. | I | Diseño | `test_los_importes_son_exactos_al_centimo` | Usar `decimal.Decimal` con dos decimales y rechazar `float`. |
| 5 | Cualquier cliente con sesión consulta el saldo y los movimientos de cualquier cuenta solo con saber su identificador (IDOR). Los identificadores son secuenciales y fáciles de adivinar. Incumple RS-07. | C | Diseño | `test_no_se_puede_consultar_el_saldo_de_otro_cliente`, `test_no_se_pueden_consultar_los_movimientos_de_otro_cliente` | Comprobar en cada operación que la cuenta pertenece al usuario de la sesión. |
| 6 | Las contraseñas se guardan y se comparan en claro. Quien acceda a los datos las lee todas. Incumple RS-10. | C | Diseño | `test_las_contrasenas_no_se_guardan_en_claro` | Guardar un hash `scrypt` con sal aleatoria y comparar con `hmac.compare_digest`. |
| 7 | El log registra la contraseña en cada login y los importes y saldos. Incumple RS-11 y el principio de minimización del RGPD. | C | Análisis | `test_los_logs_no_contienen_contrasenas_ni_importes` | Registrar solo qué ocurre y quién lo hace, sin contraseñas ni datos económicos. |
| 8 | El login no limita los intentos fallidos: se puede probar contraseñas sin fin (fuerza bruta). Incumple RS-09. | C / D | Análisis | `test_el_login_se_bloquea_tras_varios_fallos` | Bloquear el usuario 15 minutos tras 5 fallos seguidos. El bloqueo es temporal para no regalar a un atacante una forma de dejar sin acceso a un cliente. |
| 9 | La clave que firma las sesiones está escrita en `config.py`. Cualquiera que lea el repositorio puede fabricar una sesión válida de cualquier usuario. Incumple RS-12. Lo detecta bandit (B105). | C / I | Codificación | `test_la_clave_secreta_no_esta_en_el_codigo` | Leer la clave de la variable de entorno `MINIBANCO_SECRET_KEY`. Sin ella, el banco no arranca. |

## Cómo rellenar cada columna

- **Descripción:** qué ocurre y qué requisito incumple (por ejemplo, RS-01).
- **CIA:** qué propiedad se pierde. Usa una o varias de estas letras:
  - **C** (confidencialidad): alguien ve datos que no debería ver.
  - **I** (integridad): alguien cambia datos sin permiso, o los datos quedan mal.
  - **D** (disponibilidad): alguien no puede usar el sistema cuando lo necesita.
- **Fase del SDLC:** en qué fase se debió evitar el fallo: Análisis, Diseño, Codificación, Pruebas o Producción.
- **Test que lo demuestra:** nombre del test en `tests/test_seguridad.py`.
- **Corrección:** qué has cambiado en el código, en una frase.

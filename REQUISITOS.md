# Requisitos de MiniBanco

MiniBanco es un banco sencillo. Guarda los datos en memoria: no usa base de datos ni web.

## Requisitos funcionales

| Id | Requisito |
|---|---|
| RF-01 | Un cliente se registra al crear su primera cuenta, con un nombre de usuario y una contraseña. |
| RF-02 | Un cliente puede tener varias cuentas. Cada cuenta tiene un identificador único (por ejemplo, `ES0001`). |
| RF-03 | Un cliente inicia sesión con su usuario y contraseña. El banco le devuelve un token de sesión. |
| RF-04 | Con una sesión válida, un cliente puede consultar el saldo de una cuenta. |
| RF-05 | Con una sesión válida, un cliente puede consultar los movimientos de una cuenta. |
| RF-06 | Con una sesión válida, un cliente puede transferir dinero desde una de sus cuentas a otra cuenta del banco, suya o de otro cliente. |
| RF-07 | Cada transferencia queda registrada en los movimientos de las dos cuentas. |

## Requisitos de seguridad

### Operaciones con dinero

| Id | Requisito |
|---|---|
| RS-01 | Una transferencia solo se realiza si la cuenta de origen tiene saldo suficiente. |
| RS-02 | El importe de una transferencia es siempre una cantidad positiva. |
| RS-03 | Una transferencia se hace completa o no se hace. Nunca puede salir dinero de una cuenta sin entrar en otra. |
| RS-04 | Los importes se calculan con exactitud al céntimo. |

### Acceso

| Id | Requisito |
|---|---|
| RS-05 | Toda operación sobre una cuenta exige una sesión válida. |
| RS-06 | Una sesión caduca a los 30 minutos. |
| RS-07 | Un cliente solo puede consultar el saldo y los movimientos de sus propias cuentas. |
| RS-08 | Un cliente solo puede ordenar transferencias desde sus propias cuentas. |
| RS-09 | El sistema limita los intentos fallidos de inicio de sesión, para frenar los ataques de fuerza bruta. Un cliente legítimo no debe perder el acceso de forma permanente. |

### Datos y configuración

| Id | Requisito |
|---|---|
| RS-10 | El banco no guarda las contraseñas de forma que se puedan recuperar. Si alguien obtiene los datos guardados, no debe poder leer las contraseñas. |
| RS-11 | Los registros (logs) no contienen contraseñas ni datos económicos de los clientes. Así lo exige el principio de minimización de datos del RGPD. |
| RS-12 | Las claves y secretos no se guardan en el código fuente. Se configuran en el entorno donde se ejecuta la aplicación. |

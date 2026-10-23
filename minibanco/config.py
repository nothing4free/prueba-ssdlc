"""Configuración general de MiniBanco."""

import os

# Duración de una sesión, en segundos.
DURACION_SESION = 30 * 60

# Intentos de login fallidos seguidos antes de bloquear al usuario.
MAX_INTENTOS_LOGIN = 5

# Duración del bloqueo tras demasiados intentos fallidos, en segundos.
DURACION_BLOQUEO = 15 * 60


def obtener_secret_key():
    """Devuelve la clave para firmar los tokens de sesión.

    La clave se configura en la variable de entorno MINIBANCO_SECRET_KEY,
    nunca en el código.
    """
    clave = os.environ.get("MINIBANCO_SECRET_KEY")
    if not clave:
        raise RuntimeError("Falta la variable de entorno MINIBANCO_SECRET_KEY")
    return clave

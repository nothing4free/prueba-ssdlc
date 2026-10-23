"""Lógica de MiniBanco: usuarios, cuentas, sesiones y transferencias."""

import hashlib
import hmac
import logging
import os
import time
from decimal import Decimal, InvalidOperation

from minibanco.config import (
    DURACION_BLOQUEO,
    DURACION_SESION,
    MAX_INTENTOS_LOGIN,
    obtener_secret_key,
)

logger = logging.getLogger(__name__)

CENTIMO = Decimal("0.01")


class ErrorBanco(Exception):
    """Error en una operación del banco."""


class ErrorAutenticacion(ErrorBanco):
    """Credenciales o sesión no válidas."""


class ErrorAutorizacion(ErrorBanco):
    """El usuario no puede operar sobre esa cuenta."""


def _importe(valor):
    """Convierte `valor` en un Decimal con, como mucho, dos decimales.

    Acepta int, str o Decimal. Rechaza float porque ya puede venir redondeado.
    """
    if isinstance(valor, (float, bool)):
        raise ErrorBanco("Importe no válido: usa int, str o Decimal")
    try:
        importe = Decimal(valor)
    except (InvalidOperation, TypeError, ValueError):
        raise ErrorBanco("Importe no válido") from None
    if not importe.is_finite() or importe != importe.quantize(CENTIMO):
        raise ErrorBanco("Importe no válido")
    return importe


def _hash_password(password, sal):
    return hashlib.scrypt(password.encode(), salt=sal, n=2**14, r=8, p=1)


class Banco:
    """Banco en memoria.

    `reloj` es la función que devuelve la hora actual en segundos.
    Se puede sustituir en los tests para simular el paso del tiempo.
    """

    def __init__(self, reloj=time.time):
        self._reloj = reloj
        self._secret_key = obtener_secret_key().encode()
        # usuario -> {"sal": ..., "hash": ..., "cuentas": [cuenta_id, ...]}
        self._usuarios = {}
        # cuenta_id -> {"titular": ..., "saldo": ..., "movimientos": [...]}
        self._cuentas = {}
        # usuario -> {"fallos": ..., "bloqueado_hasta": ...}
        self._intentos = {}

    # ---------------------------------------------------------------- cuentas

    def crear_cuenta(self, usuario, password, saldo_inicial=0):
        """Crea una cuenta y devuelve su identificador (por ejemplo, "ES0001").

        Si el usuario no existe, se registra con esa contraseña.
        Si ya existe, la contraseña debe coincidir.
        """
        saldo_inicial = _importe(saldo_inicial)
        if saldo_inicial < 0:
            raise ErrorBanco("El saldo inicial no puede ser negativo")

        datos = self._usuarios.get(usuario)
        if datos is None:
            sal = os.urandom(16)
            datos = {"sal": sal, "hash": _hash_password(password, sal), "cuentas": []}
            self._usuarios[usuario] = datos
        elif not self._password_correcta(datos, password):
            raise ErrorAutenticacion("Usuario o contraseña incorrectos")

        cuenta_id = f"ES{len(self._cuentas) + 1:04d}"
        self._cuentas[cuenta_id] = {
            "titular": usuario,
            "saldo": saldo_inicial,
            "movimientos": [],
        }
        datos["cuentas"].append(cuenta_id)
        logger.info("Cuenta %s creada para %s", cuenta_id, usuario)
        return cuenta_id

    def _password_correcta(self, datos, password):
        return hmac.compare_digest(_hash_password(password, datos["sal"]), datos["hash"])

    # --------------------------------------------------------------- sesiones

    def login(self, usuario, password):
        """Comprueba las credenciales y devuelve un token de sesión.

        Tras MAX_INTENTOS_LOGIN fallos seguidos, el usuario queda bloqueado
        durante DURACION_BLOQUEO segundos. El bloqueo es temporal para que un
        atacante no pueda dejar sin acceso, para siempre, a un cliente legítimo.
        """
        ahora = self._reloj()
        intentos = self._intentos.get(usuario, {"fallos": 0, "bloqueado_hasta": 0})
        if ahora < intentos["bloqueado_hasta"]:
            logger.warning("Login de %s rechazado: usuario bloqueado temporalmente", usuario)
            raise ErrorAutenticacion("Demasiados intentos fallidos. Inténtalo más tarde")

        datos = self._usuarios.get(usuario)
        if datos is None or not self._password_correcta(datos, password):
            intentos["fallos"] += 1
            if intentos["fallos"] >= MAX_INTENTOS_LOGIN:
                intentos = {"fallos": 0, "bloqueado_hasta": ahora + DURACION_BLOQUEO}
            self._intentos[usuario] = intentos
            logger.info("Login fallido de %s", usuario)
            raise ErrorAutenticacion("Usuario o contraseña incorrectos")

        self._intentos.pop(usuario, None)
        logger.info("Login correcto de %s", usuario)
        contenido = f"{usuario}:{int(ahora)}"
        return f"{contenido}:{self._firmar(contenido)}"

    def _firmar(self, contenido):
        return hmac.new(self._secret_key, contenido.encode(), hashlib.sha256).hexdigest()

    def _usuario_de_sesion(self, sesion):
        """Valida el token de sesión y devuelve el usuario al que pertenece."""
        try:
            usuario, emitido, firma = sesion.rsplit(":", 2)
            emitido = int(emitido)
        except (AttributeError, ValueError):
            raise ErrorAutenticacion("Sesión no válida") from None

        if not hmac.compare_digest(firma, self._firmar(f"{usuario}:{emitido}")):
            raise ErrorAutenticacion("Sesión no válida")
        if self._reloj() - emitido > DURACION_SESION:
            raise ErrorAutenticacion("Sesión caducada")
        return usuario

    # ------------------------------------------------------------ operaciones

    def _cuenta(self, cuenta_id):
        cuenta = self._cuentas.get(cuenta_id)
        if cuenta is None:
            raise ErrorBanco(f"La cuenta {cuenta_id} no existe")
        return cuenta

    def _cuenta_propia(self, usuario, cuenta_id):
        """Devuelve la cuenta si existe y pertenece a `usuario`."""
        cuenta = self._cuenta(cuenta_id)
        if cuenta["titular"] != usuario:
            raise ErrorAutorizacion("La cuenta no pertenece al usuario")
        return cuenta

    def consultar_saldo(self, sesion, cuenta_id):
        """Devuelve el saldo de una cuenta del usuario en sesión."""
        usuario = self._usuario_de_sesion(sesion)
        return self._cuenta_propia(usuario, cuenta_id)["saldo"]

    def movimientos(self, sesion, cuenta_id):
        """Devuelve los movimientos de una cuenta del usuario en sesión.

        Van del más antiguo al más reciente.
        """
        usuario = self._usuario_de_sesion(sesion)
        return list(self._cuenta_propia(usuario, cuenta_id)["movimientos"])

    def transferir(self, sesion, origen, destino, importe):
        """Transfiere `importe` euros de la cuenta `origen` a la cuenta `destino`.

        Antes de mover dinero se comprueba todo. Si algo falla, no cambia nada.
        """
        usuario = self._usuario_de_sesion(sesion)
        cuenta_origen = self._cuenta_propia(usuario, origen)
        cuenta_destino = self._cuenta(destino)

        importe = _importe(importe)
        if importe <= 0:
            raise ErrorBanco("El importe debe ser mayor que cero")
        if importe > cuenta_origen["saldo"]:
            raise ErrorBanco("Saldo insuficiente")

        cuenta_origen["saldo"] -= importe
        cuenta_destino["saldo"] += importe
        cuenta_origen["movimientos"].append(
            {"tipo": "salida", "cuenta": destino, "importe": importe}
        )
        cuenta_destino["movimientos"].append(
            {"tipo": "entrada", "cuenta": origen, "importe": importe}
        )
        logger.info("Transferencia de %s a %s realizada por %s", origen, destino, usuario)

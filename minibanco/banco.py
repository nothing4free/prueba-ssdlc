"""Lógica de MiniBanco: usuarios, cuentas, sesiones y transferencias."""

import hashlib
import hmac
import logging
import time

from minibanco.config import DURACION_SESION, SECRET_KEY

logger = logging.getLogger(__name__)


class ErrorBanco(Exception):
    """Error en una operación del banco."""


class ErrorAutenticacion(ErrorBanco):
    """Credenciales o sesión no válidas."""


class ErrorAutorizacion(ErrorBanco):
    """El usuario no puede operar sobre esa cuenta."""


class Banco:
    """Banco en memoria.

    `reloj` es la función que devuelve la hora actual en segundos.
    Se puede sustituir en los tests para simular el paso del tiempo.
    """

    def __init__(self, reloj=time.time):
        self._reloj = reloj
        # usuario -> {"password": ..., "cuentas": [cuenta_id, ...]}
        self._usuarios = {}
        # cuenta_id -> {"titular": ..., "saldo": ..., "movimientos": [...]}
        self._cuentas = {}

    # ---------------------------------------------------------------- cuentas

    def crear_cuenta(self, usuario, password, saldo_inicial=0):
        """Crea una cuenta y devuelve su identificador (por ejemplo, "ES0001").

        Si el usuario no existe, se registra con esa contraseña.
        Si ya existe, la contraseña debe coincidir.
        """
        datos = self._usuarios.get(usuario)
        if datos is None:
            datos = {"password": password, "cuentas": []}
            self._usuarios[usuario] = datos
        elif datos["password"] != password:
            raise ErrorAutenticacion("Usuario o contraseña incorrectos")

        cuenta_id = f"ES{len(self._cuentas) + 1:04d}"
        self._cuentas[cuenta_id] = {
            "titular": usuario,
            "saldo": float(saldo_inicial),
            "movimientos": [],
        }
        datos["cuentas"].append(cuenta_id)
        logger.info("Cuenta %s creada para %s", cuenta_id, usuario)
        return cuenta_id

    # --------------------------------------------------------------- sesiones

    def login(self, usuario, password):
        """Comprueba las credenciales y devuelve un token de sesión."""
        logger.info("Login: usuario=%s password=%s", usuario, password)
        datos = self._usuarios.get(usuario)
        if datos is None or datos["password"] != password:
            raise ErrorAutenticacion("Usuario o contraseña incorrectos")

        contenido = f"{usuario}:{int(self._reloj())}"
        return f"{contenido}:{self._firmar(contenido)}"

    def _firmar(self, contenido):
        return hmac.new(SECRET_KEY.encode(), contenido.encode(), hashlib.sha256).hexdigest()

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

    def consultar_saldo(self, sesion, cuenta_id):
        """Devuelve el saldo de una cuenta."""
        usuario = self._usuario_de_sesion(sesion)
        cuenta = self._cuenta(cuenta_id)
        logger.info("%s consulta %s: saldo %s", usuario, cuenta_id, cuenta["saldo"])
        return cuenta["saldo"]

    def movimientos(self, sesion, cuenta_id):
        """Devuelve la lista de movimientos de una cuenta, del más antiguo al más reciente."""
        self._usuario_de_sesion(sesion)
        return list(self._cuenta(cuenta_id)["movimientos"])

    def transferir(self, sesion, origen, destino, importe):
        """Transfiere `importe` euros de la cuenta `origen` a la cuenta `destino`."""
        usuario = self._usuario_de_sesion(sesion)
        cuenta_origen = self._cuenta(origen)
        if cuenta_origen["titular"] != usuario:
            raise ErrorAutorizacion("La cuenta de origen no pertenece al usuario")

        importe = float(importe)
        cuenta_origen["saldo"] -= importe
        cuenta_origen["movimientos"].append(
            {"tipo": "salida", "cuenta": destino, "importe": importe}
        )

        cuenta_destino = self._cuentas.get(destino)
        if cuenta_destino is not None:
            cuenta_destino["saldo"] += importe
            cuenta_destino["movimientos"].append(
                {"tipo": "entrada", "cuenta": origen, "importe": importe}
            )

        logger.info(
            "Transferencia %s -> %s de %s €. Saldo de %s: %s",
            origen, destino, importe, origen, cuenta_origen["saldo"],
        )

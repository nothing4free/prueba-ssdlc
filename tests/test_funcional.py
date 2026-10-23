"""Tests funcionales de MiniBanco: comprueban que cada operación hace lo que debe."""

import pytest

from minibanco.banco import Banco, ErrorAutenticacion, ErrorAutorizacion


def test_crear_cuenta_devuelve_identificador(banco):
    cuenta = banco.crear_cuenta("ana", "ana-clave", 100)
    assert cuenta.startswith("ES")


def test_un_usuario_puede_tener_varias_cuentas(banco):
    primera = banco.crear_cuenta("ana", "ana-clave", 100)
    segunda = banco.crear_cuenta("ana", "ana-clave", 50)
    assert primera != segunda


def test_login_correcto_devuelve_sesion(banco):
    banco.crear_cuenta("ana", "ana-clave", 100)
    sesion = banco.login("ana", "ana-clave")
    assert sesion


def test_login_con_contrasena_incorrecta_falla(banco):
    banco.crear_cuenta("ana", "ana-clave", 100)
    with pytest.raises(ErrorAutenticacion):
        banco.login("ana", "otra-clave")


def test_login_de_usuario_inexistente_falla(banco):
    with pytest.raises(ErrorAutenticacion):
        banco.login("nadie", "da-igual")


def test_consultar_saldo_inicial(banco):
    cuenta = banco.crear_cuenta("ana", "ana-clave", 1000)
    sesion = banco.login("ana", "ana-clave")
    assert banco.consultar_saldo(sesion, cuenta) == 1000


def test_sesion_inventada_es_rechazada(banco):
    cuenta = banco.crear_cuenta("ana", "ana-clave", 1000)
    with pytest.raises(ErrorAutenticacion):
        banco.consultar_saldo("ana:0:firma-inventada", cuenta)


def test_la_sesion_caduca_a_los_30_minutos():
    ahora = [1_000_000]
    banco = Banco(reloj=lambda: ahora[0])
    cuenta = banco.crear_cuenta("ana", "ana-clave", 1000)
    sesion = banco.login("ana", "ana-clave")

    ahora[0] += 31 * 60
    with pytest.raises(ErrorAutenticacion):
        banco.consultar_saldo(sesion, cuenta)


def test_transferencia_entre_usuarios(banco):
    ana = banco.crear_cuenta("ana", "ana-clave", 1000)
    luis = banco.crear_cuenta("luis", "luis-clave", 0)
    sesion_ana = banco.login("ana", "ana-clave")
    sesion_luis = banco.login("luis", "luis-clave")

    banco.transferir(sesion_ana, ana, luis, 200)

    assert banco.consultar_saldo(sesion_ana, ana) == 800
    assert banco.consultar_saldo(sesion_luis, luis) == 200


def test_transferencia_entre_cuentas_propias(banco):
    corriente = banco.crear_cuenta("ana", "ana-clave", 1000)
    ahorro = banco.crear_cuenta("ana", "ana-clave", 0)
    sesion = banco.login("ana", "ana-clave")

    banco.transferir(sesion, corriente, ahorro, 300)

    assert banco.consultar_saldo(sesion, corriente) == 700
    assert banco.consultar_saldo(sesion, ahorro) == 300


def test_no_se_puede_transferir_desde_una_cuenta_ajena(banco):
    ana = banco.crear_cuenta("ana", "ana-clave", 1000)
    luis = banco.crear_cuenta("luis", "luis-clave", 1000)
    sesion_luis = banco.login("luis", "luis-clave")

    with pytest.raises(ErrorAutorizacion):
        banco.transferir(sesion_luis, ana, luis, 100)


def test_movimientos_registra_la_transferencia(banco):
    ana = banco.crear_cuenta("ana", "ana-clave", 1000)
    luis = banco.crear_cuenta("luis", "luis-clave", 0)
    sesion_ana = banco.login("ana", "ana-clave")
    sesion_luis = banco.login("luis", "luis-clave")

    banco.transferir(sesion_ana, ana, luis, 200)

    salida = banco.movimientos(sesion_ana, ana)
    entrada = banco.movimientos(sesion_luis, luis)
    assert len(salida) == 1
    assert salida[0]["tipo"] == "salida"
    assert salida[0]["cuenta"] == luis
    assert salida[0]["importe"] == 200
    assert entrada[0]["tipo"] == "entrada"
    assert entrada[0]["cuenta"] == ana

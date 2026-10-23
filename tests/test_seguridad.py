"""Tests de seguridad de MiniBanco.

Cada test demuestra un fallo. Al escribirlo, debe fallar (rojo).
Cuando corrijas el código, debe pasar (verde).
"""

import logging

import pytest

from minibanco.banco import Banco, ErrorAutenticacion, ErrorAutorizacion, ErrorBanco


@pytest.fixture
def ana_y_luis(banco):
    """Ana con 500 € y Luis con 0 €. Devuelve las cuentas y la sesión de Ana."""
    ana = banco.crear_cuenta("ana", "ana-clave", 500)
    luis = banco.crear_cuenta("luis", "luis-clave", 0)
    sesion = banco.login("ana", "ana-clave")
    return ana, luis, sesion


# Fallo 1: RS-01
def test_no_se_puede_transferir_mas_que_el_saldo(banco):
    ana = banco.crear_cuenta("ana", "ana-clave", 500)
    luis = banco.crear_cuenta("luis", "luis-clave", 0)
    sesion = banco.login("ana", "ana-clave")

    # Ana tiene 500 € e intenta transferir 1.000 €: el banco debe rechazarlo.
    with pytest.raises(ErrorBanco):
        banco.transferir(sesion, ana, luis, 1000)

    # Y su saldo no debe cambiar.
    assert banco.consultar_saldo(sesion, ana) == 500


# Fallo 2: RS-02
@pytest.mark.parametrize("importe", [-100, 0])
def test_el_importe_debe_ser_positivo(banco, ana_y_luis, importe):
    ana, luis, sesion = ana_y_luis

    with pytest.raises(ErrorBanco):
        banco.transferir(sesion, ana, luis, importe)

    assert banco.consultar_saldo(sesion, ana) == 500


# Fallo 3: RS-03
def test_transferir_a_una_cuenta_inexistente_no_pierde_dinero(banco, ana_y_luis):
    ana, _, sesion = ana_y_luis

    with pytest.raises(ErrorBanco):
        banco.transferir(sesion, ana, "ES9999", 100)

    assert banco.consultar_saldo(sesion, ana) == 500
    assert banco.movimientos(sesion, ana) == []


# Fallo 4: RS-04
def test_los_importes_son_exactos_al_centimo(banco):
    ana = banco.crear_cuenta("ana", "ana-clave", "0.30")
    luis = banco.crear_cuenta("luis", "luis-clave", 0)
    sesion = banco.login("ana", "ana-clave")

    banco.transferir(sesion, ana, luis, "0.10")
    banco.transferir(sesion, ana, luis, "0.20")

    assert banco.consultar_saldo(sesion, ana) == 0


# Fallo 5: RS-07
def test_no_se_puede_consultar_el_saldo_de_otro_cliente(banco, ana_y_luis):
    ana, _, _ = ana_y_luis
    sesion_luis = banco.login("luis", "luis-clave")

    with pytest.raises(ErrorAutorizacion):
        banco.consultar_saldo(sesion_luis, ana)


def test_no_se_pueden_consultar_los_movimientos_de_otro_cliente(banco, ana_y_luis):
    ana, _, _ = ana_y_luis
    sesion_luis = banco.login("luis", "luis-clave")

    with pytest.raises(ErrorAutorizacion):
        banco.movimientos(sesion_luis, ana)


# Fallo 6: RS-10
def test_las_contrasenas_no_se_guardan_en_claro(banco, ana_y_luis):
    datos_guardados = repr(banco._usuarios)

    assert "ana-clave" not in datos_guardados
    assert "luis-clave" not in datos_guardados


# Fallo 7: RS-11
def test_los_logs_no_contienen_contrasenas_ni_importes(banco, caplog):
    caplog.set_level(logging.INFO)

    ana = banco.crear_cuenta("ana", "ana-clave", 5000)
    luis = banco.crear_cuenta("luis", "luis-clave", 0)
    sesion = banco.login("ana", "ana-clave")
    banco.transferir(sesion, ana, luis, "1234.56")
    banco.consultar_saldo(sesion, ana)

    assert "ana-clave" not in caplog.text
    assert "1234.56" not in caplog.text  # importe
    assert "3765.44" not in caplog.text  # saldo final


# Fallo 8: RS-09
def test_el_login_se_bloquea_tras_varios_fallos():
    ahora = [1_000_000]
    banco = Banco(reloj=lambda: ahora[0])
    banco.crear_cuenta("ana", "ana-clave", 100)

    for _ in range(5):
        with pytest.raises(ErrorAutenticacion):
            banco.login("ana", "intento-de-atacante")

    # Bloqueado: ni siquiera la contraseña correcta funciona.
    with pytest.raises(ErrorAutenticacion):
        banco.login("ana", "ana-clave")

    # El bloqueo es temporal: pasado un rato, Ana vuelve a entrar.
    ahora[0] += 16 * 60
    assert banco.login("ana", "ana-clave")


# Fallo 9: RS-12
def test_la_clave_secreta_no_esta_en_el_codigo(monkeypatch):
    monkeypatch.delenv("MINIBANCO_SECRET_KEY", raising=False)

    with pytest.raises(RuntimeError):
        Banco()

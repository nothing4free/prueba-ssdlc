"""Tests de seguridad de MiniBanco.

Cada test demuestra un fallo. Al escribirlo, debe fallar (rojo).
Cuando corrijas el código, debe pasar (verde).
"""

import pytest

from minibanco.banco import ErrorBanco


def test_no_se_puede_transferir_mas_que_el_saldo(banco):
    ana = banco.crear_cuenta("ana", "ana-clave", 500)
    luis = banco.crear_cuenta("luis", "luis-clave", 0)
    sesion = banco.login("ana", "ana-clave")

    # Ana tiene 500 € e intenta transferir 1.000 €: el banco debe rechazarlo.
    with pytest.raises(ErrorBanco):
        banco.transferir(sesion, ana, luis, 1000)

    # Y su saldo no debe cambiar.
    assert banco.consultar_saldo(sesion, ana) == 500

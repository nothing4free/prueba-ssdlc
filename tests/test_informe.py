"""Tests de la exportación de informes."""

from minibanco.informe import exportar_informe, importar_informe


def test_exportar_e_importar_informe(banco, tmp_path):
    ana = banco.crear_cuenta("ana", "ana-clave", 1000)
    luis = banco.crear_cuenta("luis", "luis-clave", 0)
    sesion = banco.login("ana", "ana-clave")
    banco.transferir(sesion, ana, luis, 200)

    ruta = tmp_path / "informe.yaml"
    exportar_informe(ana, banco.movimientos(sesion, ana), ruta)
    informe = importar_informe(ruta)

    assert informe["cuenta"] == ana
    assert informe["movimientos"] == [{"tipo": "salida", "cuenta": luis, "importe": "200.00"}]

"""Demostración de MiniBanco. Ejecútala con: python -m minibanco"""

import logging

from minibanco.banco import Banco


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    banco = Banco()
    cuenta_ana = banco.crear_cuenta("ana", "ana-1234", 1000)
    cuenta_luis = banco.crear_cuenta("luis", "luis-1234", 250)

    sesion = banco.login("ana", "ana-1234")
    banco.transferir(sesion, cuenta_ana, cuenta_luis, 200)

    print()
    print(f"Saldo de {cuenta_ana}: {banco.consultar_saldo(sesion, cuenta_ana)} €")
    print(f"Movimientos de {cuenta_ana}:")
    for movimiento in banco.movimientos(sesion, cuenta_ana):
        print(f"  {movimiento['tipo']:8} {movimiento['cuenta']}  {movimiento['importe']} €")


if __name__ == "__main__":
    main()

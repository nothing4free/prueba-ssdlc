"""Exportar e importar informes de movimientos en formato YAML."""

import yaml


def exportar_informe(cuenta_id, movimientos, ruta):
    """Guarda en `ruta` un informe con los movimientos de una cuenta."""
    informe = {
        "cuenta": cuenta_id,
        "movimientos": [
            {"tipo": m["tipo"], "cuenta": m["cuenta"], "importe": f"{m['importe']:.2f}"}
            for m in movimientos
        ],
    }
    with open(ruta, "w", encoding="utf-8") as fichero:
        yaml.dump(informe, fichero, allow_unicode=True, sort_keys=False)


def importar_informe(ruta):
    """Lee un informe guardado con `exportar_informe` y lo devuelve como diccionario."""
    with open(ruta, encoding="utf-8") as fichero:
        return yaml.load(fichero, Loader=yaml.FullLoader)

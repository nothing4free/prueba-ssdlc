import pytest

from minibanco.banco import Banco


@pytest.fixture(autouse=True)
def clave_secreta(monkeypatch):
    """Clave de pruebas. En producción se configura en el entorno."""
    monkeypatch.setenv("MINIBANCO_SECRET_KEY", "clave-solo-para-tests")


@pytest.fixture
def banco():
    """Un banco nuevo y vacío para cada test."""
    return Banco()

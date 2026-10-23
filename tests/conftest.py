import pytest

from minibanco.banco import Banco


@pytest.fixture
def banco():
    """Un banco nuevo y vacío para cada test."""
    return Banco()

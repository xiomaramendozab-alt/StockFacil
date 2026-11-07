import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import app as flask_app, init_db  # noqa: E402


@pytest.fixture
def cliente():
    fd, ruta = tempfile.mkstemp(suffix=".db")
    flask_app.config.update(TESTING=True, DATABASE=ruta)
    with flask_app.app_context():
        init_db()
    with flask_app.test_client() as c:
        yield c
    os.close(fd)
    os.remove(ruta)


def iniciar_sesion(cliente, usuario="admin", clave="Admin2026*"):
    return cliente.post("/login", data={"usuario": usuario, "clave": clave}, follow_redirects=True)

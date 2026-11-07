"""Prueba 2 - Prueba de seguridad de StockFácil."""
from conftest import iniciar_sesion


def test_CPS01_inyeccion_sql_en_login(cliente):
    for carga in ("' OR '1'='1", "admin' --", "' OR 1=1 --"):
        r = iniciar_sesion(cliente, usuario=carga, clave=carga)
        texto = r.get_data(as_text=True)
        assert "Usuario o contraseña incorrectos." in texto
        assert "Hola," not in texto


def test_CPS01b_inyeccion_sql_en_busqueda(cliente):
    iniciar_sesion(cliente)
    cliente.post("/productos/nuevo", data={"nombre": "Azúcar", "precio": "3000", "cantidad": "8"})
    r = cliente.get("/productos?q=' OR '1'='1")
    assert r.status_code == 200
    assert "Azúcar" not in r.get_data(as_text=True)


def test_CPS02_xss_almacenado_en_nombre(cliente):
    iniciar_sesion(cliente)
    carga = "<script>alert('XSS')</script>"
    cliente.post("/productos/nuevo", data={"nombre": carga, "precio": "1000", "cantidad": "1"})
    texto = cliente.get("/productos").get_data(as_text=True)
    assert carga not in texto
    assert "&lt;script&gt;" in texto


def test_CPS03_acceso_sin_sesion_redirige(cliente):
    for ruta in ("/productos", "/productos/nuevo"):
        r = cliente.get(ruta)
        assert r.status_code == 302
        assert "/login" in r.headers["Location"]


def test_CPS04_contrasena_guardada_con_hash(cliente):
    from app import app, get_db
    with app.app_context():
        clave = get_db().execute("SELECT clave FROM usuarios WHERE usuario='admin'").fetchone()[0]
    assert clave != "Admin2026*"
    assert clave.startswith(("scrypt:", "pbkdf2:"))


def test_CPS05_cookie_de_sesion_httponly(cliente):
    r = cliente.post("/login", data={"usuario": "admin", "clave": "Admin2026*"})
    cookie = r.headers.get("Set-Cookie", "")
    assert "HttpOnly" in cookie


def test_CPS06_bloqueo_por_intentos_fallidos(cliente):
    """Requerimiento RNF-03: bloquear la cuenta tras 5 intentos fallidos."""
    for _ in range(5):
        iniciar_sesion(cliente, clave="mala")
    r = iniciar_sesion(cliente)  # sexto intento con la clave correcta
    assert "Hola, admin" not in r.get_data(as_text=True), \
        "No hay bloqueo: se aceptan intentos ilimitados (riesgo de fuerza bruta)"

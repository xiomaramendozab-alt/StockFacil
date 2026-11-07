"""Prueba 1 - Prueba funcional (caja negra) de StockFácil."""
from conftest import iniciar_sesion


def test_CPF01_login_credenciales_validas(cliente):
    r = iniciar_sesion(cliente)
    assert r.status_code == 200
    assert "Inventario" in r.get_data(as_text=True)
    assert "Hola, admin" in r.get_data(as_text=True)


def test_CPF01b_login_credenciales_invalidas(cliente):
    r = iniciar_sesion(cliente, clave="claveErronea")
    texto = r.get_data(as_text=True)
    assert "Usuario o contraseña incorrectos." in texto
    assert "Hola, admin" not in texto


def test_CPF02_registro_producto_valido(cliente):
    iniciar_sesion(cliente)
    r = cliente.post(
        "/productos/nuevo",
        data={"nombre": "Arroz Diana 500 g", "precio": "3200", "cantidad": "40"},
        follow_redirects=True,
    )
    texto = r.get_data(as_text=True)
    assert "Producto registrado correctamente." in texto
    assert "Arroz Diana 500 g" in texto


def test_CPF02b_rechaza_precio_negativo(cliente):
    iniciar_sesion(cliente)
    r = cliente.post(
        "/productos/nuevo", data={"nombre": "Aceite 1 L", "precio": "-5000", "cantidad": "10"}
    )
    assert r.status_code == 400
    assert "El precio debe ser mayor que cero." in r.get_data(as_text=True)


def test_CPF02c_rechaza_campos_vacios(cliente):
    iniciar_sesion(cliente)
    r = cliente.post("/productos/nuevo", data={"nombre": "", "precio": "", "cantidad": ""})
    texto = r.get_data(as_text=True)
    assert r.status_code == 400
    assert "El nombre es obligatorio." in texto


def test_CPF02d_rechaza_producto_duplicado(cliente):
    """Requerimiento RF-04: no se deben registrar dos productos con el mismo nombre."""
    iniciar_sesion(cliente)
    datos = {"nombre": "Panela 1 kg", "precio": "4500", "cantidad": "20"}
    cliente.post("/productos/nuevo", data=datos)
    r = cliente.post("/productos/nuevo", data=datos)
    assert r.status_code == 400, "El sistema permitió registrar un producto duplicado"


def test_CPF03_busqueda_por_nombre(cliente):
    iniciar_sesion(cliente)
    for n in ("Leche entera", "Café molido", "Leche deslactosada"):
        cliente.post("/productos/nuevo", data={"nombre": n, "precio": "5000", "cantidad": "5"})
    texto = cliente.get("/productos?q=Leche").get_data(as_text=True)
    assert "Leche entera" in texto and "Leche deslactosada" in texto
    assert "Café molido" not in texto

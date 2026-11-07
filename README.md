# StockFácil

Sistema web sencillo para llevar el inventario de una tienda de barrio. Lo construí para la actividad final del curso de Calidad de Software (CUN), donde le apliqué una prueba funcional y una prueba de seguridad, y medí tres métricas de calidad.

## Qué hace

- Inicio de sesión con usuario y contraseña (la contraseña se guarda cifrada con hash).
- Registro de productos con nombre, precio y cantidad, con validación de los datos.
- Listado del inventario y búsqueda por nombre.

Tecnologías: Python 3, Flask, SQLite, pytest, pytest-cov y radon.

## Cómo ejecutarlo

```bash
pip install -r requirements.txt
python app.py
```

Luego abrir `http://127.0.0.1:5000` en el navegador.
Usuario de prueba: `admin` / contraseña: `Admin2026*`

## Cómo correr las pruebas

```bash
python -m pytest -v --cov=app --cov-report=term-missing
```

- `tests/test_funcional.py`: prueba funcional (login, registro de productos, validaciones, búsqueda).
- `tests/test_seguridad.py`: prueba de seguridad (inyección SQL, XSS, acceso sin sesión, hash de contraseñas, cookie de sesión, bloqueo por intentos fallidos).

## Métricas

```bash
radon cc app.py -s -a   # complejidad ciclomática
radon raw app.py        # líneas de código
```

## Resultados

14 casos ejecutados: 12 aprobados y 2 fallidos. Los dos fallos son defectos reales del sistema y quedan abiertos a propósito para documentarlos en el informe:

1. **CPF02d**: el sistema deja registrar dos productos con el mismo nombre.
2. **CPS06**: no hay bloqueo después de varios intentos fallidos de inicio de sesión (riesgo de fuerza bruta).

Las capturas de pantalla de la ejecución están en la carpeta `evidencias/`.

"""StockFácil - Sistema web sencillo para el control de inventario de una tienda pequeña."""
import os
import sqlite3
from functools import wraps

from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "cambiar-en-produccion")
app.config["DATABASE"] = os.environ.get("DATABASE", "stockfacil.db")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            clave TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            cantidad INTEGER NOT NULL
        );
        """
    )
    if db.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] == 0:
        db.execute(
            "INSERT INTO usuarios (usuario, clave) VALUES (?, ?)",
            ("admin", generate_password_hash("Admin2026*")),
        )
    db.commit()


def login_requerido(vista):
    @wraps(vista)
    def envoltura(*args, **kwargs):
        if "usuario" not in session:
            flash("Debe iniciar sesión para continuar.", "error")
            return redirect(url_for("login"))
        return vista(*args, **kwargs)

    return envoltura


@app.route("/")
def inicio():
    return redirect(url_for("productos"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        clave = request.form.get("clave", "")
        fila = get_db().execute(
            "SELECT * FROM usuarios WHERE usuario = ?", (usuario,)
        ).fetchone()
        if fila and check_password_hash(fila["clave"], clave):
            session.clear()
            session["usuario"] = fila["usuario"]
            return redirect(url_for("productos"))
        flash("Usuario o contraseña incorrectos.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


def validar_producto(nombre, precio, cantidad):
    errores = []
    if not nombre:
        errores.append("El nombre es obligatorio.")
    elif len(nombre) > 80:
        errores.append("El nombre no puede superar 80 caracteres.")
    try:
        precio = float(precio)
        if precio <= 0:
            errores.append("El precio debe ser mayor que cero.")
    except ValueError:
        errores.append("El precio debe ser un número.")
    try:
        cantidad = int(cantidad)
        if cantidad < 0:
            errores.append("La cantidad no puede ser negativa.")
    except ValueError:
        errores.append("La cantidad debe ser un número entero.")
    return errores, precio, cantidad


@app.route("/productos")
@login_requerido
def productos():
    q = request.args.get("q", "").strip()
    db = get_db()
    if q:
        filas = db.execute(
            "SELECT * FROM productos WHERE nombre LIKE ? ORDER BY nombre", (f"%{q}%",)
        ).fetchall()
    else:
        filas = db.execute("SELECT * FROM productos ORDER BY nombre").fetchall()
    return render_template("productos.html", productos=filas, q=q)


@app.route("/productos/nuevo", methods=["GET", "POST"])
@login_requerido
def nuevo_producto():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        errores, precio, cantidad = validar_producto(
            nombre, request.form.get("precio", ""), request.form.get("cantidad", "")
        )
        if errores:
            for e in errores:
                flash(e, "error")
            return render_template("nuevo.html", datos=request.form), 400
        db = get_db()
        db.execute(
            "INSERT INTO productos (nombre, precio, cantidad) VALUES (?, ?, ?)",
            (nombre, precio, cantidad),
        )
        db.commit()
        flash("Producto registrado correctamente.", "ok")
        return redirect(url_for("productos"))
    return render_template("nuevo.html", datos={})


if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=False)

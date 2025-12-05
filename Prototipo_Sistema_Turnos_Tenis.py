from flask import Flask, request, redirect, session, render_template_string
from datetime import datetime, timedelta
import random
import string


#LINEA OFICIAL DEL SPRINT(MAIN9)

app = Flask(__name__)
app.secret_key = "clave_secreta_demo"

# --- BASE DE DATOS EN MEMORIA ---
usuarios = {}
turnos = []

# --- FUNCIONES ---
def generar_password():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))


# --- PLANTILLA HTML BASE ---
def html_base(contenido):
    return f"""
    <html>
    <head>
        <title>Turnos Tenis</title>
        <style>
            body {{ font-family: Arial; margin: 40px; }}
            .box {{ border: 1px solid #ccc; padding: 20px; width: 350px; }}
            input {{ width: 100%; margin: 5px 0; padding: 6px; }}
            .btn {{ background: #0066ff; color: white; padding: 8px; border: none; cursor: pointer; width: 100%; }}
        </style>
    </head>
    <body>
        {contenido}
    </body>
    </html>
    """


# --- RUTAS ---
@app.route("/")
def index():
    html = """
<style>
    body {
        margin: 0;
        padding: 0;
        font-family: Arial, sans-serif;
        background: linear-gradient(135deg, #1e90ff, #00bfff);
        height: 100vh;
        display: flex;
        justify-content: center;
        align-items: center;
        color: white;
        text-align: center;
    }

    .container {
        background: rgba(0, 0, 0, 0.25);
        padding: 40px;
        border-radius: 15px;
        width: 350px;
        box-shadow: 0px 0px 15px rgba(0,0,0,0.3);
        backdrop-filter: blur(5px);
    }

    h2 {
        margin-bottom: 30px;
        font-size: 28px;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    a {
        display: block;
        background: white;
        color: #1e90ff;
        padding: 12px;
        margin: 15px 0;
        text-decoration: none;
        border-radius: 8px;
        font-size: 18px;
        font-weight: bold;
        transition: 0.3s;
    }

    a:hover {
        background: #f0f8ff;
        transform: scale(1.05);
    }

</style>

<div class="container">
    <h2>Sistema de Turnos - Tenis</h2>
    <a href="/register">Registrarse</a>
    <a href="/login">Iniciar Sesión</a>
</div>
"""

    return render_template_string(html_base(html))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nombre = request.form["nombre"]
        apellido = request.form["apellido"]
        email = request.form["email"]
        edad = int(request.form["edad"])
        domicilio = request.form["domicilio"]

        if edad < 18:
            return render_template_string(html_base("<h3>Debe ser mayor de 18 años</h3><a href='/register'>Volver</a>"))

        if email in usuarios:
            return render_template_string(html_base("<h3>Ese email ya está registrado</h3><a href='/register'>Volver</a>"))

        password = generar_password()

        usuarios[email] = {
            "nombre": nombre,
            "apellido": apellido,
            "email": email,
            "edad": edad,
            "domicilio": domicilio,
            "password": password,
            "intentos": 0,
            "bloqueado": False,
        }

        msg = f"<h3>Registro exitoso</h3>Contraseña generada (demo): <b>{password}</b><br><a href='/login'>Iniciar sesión</a>"
        return render_template_string(html_base(msg))

    form = """
<style>
    body {
        margin: 0;
        padding: 0;
        font-family: Arial, sans-serif;
        background: linear-gradient(135deg, #1e90ff, #00bfff);
        height: 100vh;
        display: flex;
        justify-content: center;
        align-items: center;
        color: white;
        text-align: center;
    }

    .box {
        background: rgba(0, 0, 0, 0.25);
        padding: 40px;
        border-radius: 15px;
        width: 380px;
        box-shadow: 0px 0px 15px rgba(0,0,0,0.3);
        backdrop-filter: blur(5px);
    }

    h3 {
        margin-bottom: 20px;
        font-size: 26px;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    input {
        width: 90%;
        padding: 12px;
        margin: 10px 0;
        border-radius: 8px;
        border: none;
        font-size: 16px;
    }

    input:focus {
        outline: none;
        box-shadow: 0 0 10px rgba(255,255,255,0.6);
    }

    .btn {
        width: 95%;
        padding: 12px;
        background: white;
        color: #1e90ff;
        border: none;
        border-radius: 8px;
        font-size: 18px;
        margin-top: 15px;
        font-weight: bold;
        cursor: pointer;
        transition: 0.3s;
    }

    .btn:hover {
        background: #f0f8ff;
        transform: scale(1.05);
    }
</style>

<div class='box'>
    <h3>Registro</h3>
    <form method='POST'>
        <input name='nombre' placeholder='Nombre' required>
        <input name='apellido' placeholder='Apellido' required>
        <input name='email' placeholder='Email' required>
        <input name='edad' type='number' placeholder='Edad' required>
        <input name='domicilio' placeholder='Domicilio' required>
        <button class='btn'>Registrarse</button>
    </form>
</div>
"""

    return render_template_string(html_base(form))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if email not in usuarios:
            return render_template_string(html_base("Usuario no existe<br><a href='/login'>Volver</a>"))

        user = usuarios[email]

        if user["bloqueado"]:
            return render_template_string(html_base("<h3>Cuenta bloqueada</h3><a href='/login'>Volver</a>"))

        if password != user["password"]:
            user["intentos"] += 1
            if user["intentos"] >= 3:
                user["bloqueado"] = True
                return render_template_string(html_base("<h3>Cuenta bloqueada por 3 intentos fallidos</h3>"))
            return render_template_string(html_base("<h3>Contraseña incorrecta</h3><a href='/login'>Volver</a>"))

        user["intentos"] = 0
        session["email"] = email
        return redirect("/reservar")

    form = """
<style>
    body {
        font-family: Arial, sans-serif;
        background: #f2f4f8;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        margin: 0;
    }

    .box {
        background: white;
        padding: 35px;
        width: 340px;
        border-radius: 12px;
        box-shadow: 0 4px 18px rgba(0,0,0,0.15);
        text-align: center;
    }

    h3 {
        margin-bottom: 20px;
        font-size: 22px;
        color: #333;
    }

    input {
        width: 90%;
        padding: 12px;
        margin: 10px 0;
        border-radius: 6px;
        border: 1px solid #ccc;
        font-size: 16px;
    }

    input:focus {
        outline: none;
        border-color: #1e90ff;
        box-shadow: 0 0 5px rgba(30,144,255,0.4);
    }

    .btn {
        width: 95%;
        padding: 12px;
        background: #1e90ff;
        color: white;
        border: none;
        border-radius: 6px;
        font-size: 17px;
        margin-top: 15px;
        cursor: pointer;
        transition: 0.3s;
    }

    .btn:hover {
        background: #0b70d0;
    }
</style>

<div class='box'>
    <h3>Iniciar Sesión</h3>
    <form method='POST'>
        <input name='email' placeholder='Email' required>
        <input type='password' name='password' placeholder='Contraseña' required>
        <button class='btn'>Entrar</button>
    </form>
</div>
"""

    return render_template_string(html_base(form))


@app.route("/reservar", methods=["GET", "POST"])
def reservar():
    if "email" not in session:
        return redirect("/login")

    if request.method == "POST":
        cancha = request.form["cancha"]
        fecha = request.form["fecha"]
        hora = request.form["hora"]

        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
        hoy = datetime.now()

        if fecha_dt < hoy + timedelta(days=2):
            return render_template_string(html_base("Debe reservar con 2 días de anticipación<br><a href='/reservar'>Volver</a>"))

        for t in turnos:
            if t["cancha"] == cancha and t["fecha"] == fecha and t["hora"] == hora:
                return render_template_string(html_base("Cancha ocupada, seleccione otro horario<br><a href='/reservar'>Volver</a>"))

        turnos.append({
            "usuario": session["email"],
            "cancha": cancha,
            "fecha": fecha,
            "hora": hora
        })

        return render_template_string(html_base("<h3>Turno registrado con éxito</h3><a href='/reservar'>Volver</a>"))

    form = """
    <div class='box'>
    <h3>Reservar turno</h3>
    <form method='POST'>
        <input name='cancha' placeholder='Cancha (1,2,3...)' required>
        <input name='fecha' type='date' required>
        <input name='hora' placeholder='Hora (ej: 15:00)' required>
        <button class='btn'>Reservar</button>
    </form>
    </div>
    """
    return render_template_string(html_base(form))


# --- RUN SERVER ---
if __name__ == "__main__":
    app.run(debug=True)


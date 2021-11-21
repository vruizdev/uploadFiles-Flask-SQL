import os

from flask import Flask, request, render_template, redirect, flash
from werkzeug.utils import secure_filename # simplifica la codificacion de la imagen y nos devuleve el nombre del archivo
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash

app = Flask(__name__)

# Configure secret key for session
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY") or '6HnUF1dhfjRwjQQnZc5LiLtfz25rvwhr'

DATABASE_URL = os.getenv('DATABASE_URL') or "agregar la URI de tu data base de prueba"


# Check for environment variable
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(DATABASE_URL)
db = scoped_session(sessionmaker(bind=engine))


# CONFIGURACION DE FOLDERS PARA SUBIR ARCHIVOS
# UPLOAD_FOLDER = os.path.abspath('./static/imgDB/')
UPLOAD_FOLDER = './static/imgDB/'
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Tabla que se utilizo para el ejemplo
# CREATE TABLE users (
#     id_user SERIAL NOT NULL,
#     username VARCHAR(50) NOT NULL,
#     password_hash VARCHAR(500) NOT NULL,
#     image VARCHAR(50),

#     PRIMARY KEY (id_user)
# );


@app.route("/")
def index():
    
    sQuery = db.execute("SELECT * FROM users").fetchall()

    return render_template("form.html", sQuery=sQuery)

# Función para verificar si el archivo tiene una extension permitida
def allowed_file(filename):
    # Devuelve True dependiedo las siguientes dos sentencias
        # 1 - El nombre del archivo tiene un punto
        # 2 - El nombre del archivo tiene una extension permitida segun la variable ALLOWED_EXTENSIONS
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
           # rsplit es para dividir el nombre del archivo para poder recuperar la extension
              # rsplit('.', 1)[1] el primer parametro indica donde se va a dividir, el segundo parametro indica cuantas veces se va a dividir
              # [1] recuperamos la extension del archivo, ya que se dividio en dos y en la posicion 1 se encuentra la extension


# upload image
@app.route("/uploader", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        # Obtengo los datos del formulario
        username = request.form.get('username')
        password = request.form.get('password1')
        password_encriptado = generate_password_hash(password)

        # Comprueba si la solicitud mediante POST tiene la parte del archivo
        if 'file' not in request.files:
            flash('The form has no file part', 'alert-danger')
            return redirect('/')

        file = request.files['file']
        # si el usuario no selecciona el archivo, el navegador también y enviar una parte vacía sin nombre de archivo
        if file.filename == '':
            flash('No selected file', 'alert-danger')
            return redirect('/')

        # Si existe el archivo y ademas el nombre del archivo tiene una extension de archivo permitida
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            dirFile = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            print(f"\n\n{dirFile}\n\n")

            db.execute("INSERT INTO users(username, password_hash, image) VALUES(:name, :pass_hash, :img)", {"name": username, "pass_hash": password_encriptado, "img": dirFile})
            db.commit()

            flash('File uploaded successfully', 'alert-success')
            return redirect('/')

        else:
            flash('File extension not allowed', 'alert-warning')
            return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
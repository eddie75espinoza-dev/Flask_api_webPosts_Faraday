'''
Ejercicio
Desarrollar una aplicación WEB, que cumpla con lo siguiente:
1. Que permita registrar y iniciar sesión a "Usuarios".
2. Que contenga una ruta (/members_only), solo accesible por usuarios validos.
3. Que la ruta mencionada en el punto 2, te permita seleccionar un entero, y te muestre la información del post correspondiente a ese ID.
API para extraer la información: https://jsonplaceholder.typicode.com/posts
4. La aplicación tiene que estar desarrollada usando Python y Flask, se puede utilizar extensiones.

__author__ = 'eddie75espinoza'
__date__ = '29/08/2021'

A considerar: se debe encriptar el password que se envía a la DB, puede usarse:
werkzeug.security, passlib o cryptography

'''
import requests
import crypt
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, session, redirect, url_for, flash
from urls import _URL_API
from config import _SECRET_KEY, _SALT

app = Flask(__name__)
app.secret_key = _SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))
    is_active = db.Column(db.Boolean) # Por si es requerido a futuro para depurar
    comfirmed_at = db.Column(db.DateTime) # Por si es requerida una fecha de alta
    
    def __init__(self, id, email, password, is_active, confirmed_at):
        self.id = id
        self.email = email
        self.password = password
        self.is_active = is_active
        self.confirmed_at = confirmed_at

def get_data(url: str, *arg):
    '''Obtiene la data desde la API
        Params: string de la url
    '''
    try:        
        data = requests.get(url % arg).json()
    except Exception as e:
        print('Error getting information. %s' % str(e))
        return None
    return data

def get_user(emailForm):
    # Se obtiene al usuario de la DB
    user = User.query.filter_by(email=emailForm).first_or_404()
    return user    


@app.route('/')
def index():
    
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.post('/register')
def register_post():
    if not request.form['Username'] or not request.form['Password']:
        flash('Please enter all the fields', 'error')
    else:
        #password = crypt.crypt(request.form['Password'], _SALT) # encriptado de clave
        user = User(None, request.form['Username'], request.form['Password'], None, None)
        print(user)
        db.session.add(user)
        db.session.commit()
            
        flash('Record was successfully added')

        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login')
def login():
    
    return render_template('login.html')

@app.post('/login')
def loginPost():
    try:
        session.pop('user_id', None) #Elimina las cookies en caso de existir
        usernameForm = request.form['Username']
        password = request.form['Password']
        
        userDb = get_user(usernameForm) # Se obtiene el usuario de la DB
        
        if userDb.email and password == userDb.password: # Valida usuario y contraseña
            session['username'] = userDb.email    # Crea la sesion (cookie)         
            return redirect(url_for('members_only'))
        else:
            return render_template('login.html')
    except Exception as e:
        return f'error: {e}'

@app.route('/members_only')
def members_only():
    if 'username' in session:    # Si existe la sesion permite el ingreso   
        return render_template('members_only.html')
    else:
        return 'No session, please you must be Logged'

@app.post('/members_only')
def members_only_post():
    try:
        id_post = int(request.form['numPost'])
        posts = get_data(_URL_API) # Obtencion de registros
        for post in posts: # Por hacer: llevar a funcion de get_data, esto no es propio de esta funcion
            if id_post == post.get('id'): 
                return post
        return 'No data'   
    except Exception as e:
        return f'No Data: {e}'

@app.route('/logout')
def logout():
    # Cierra la sesion
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='localhost', port = 5000, threaded=True, debug=True)
import pymysql
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_marshmallow import Marshmallow

# Konfigurasi dasar aplikasi
app = Flask(__name__)
app.config['SECRET_KEY'] = 'd18596dc242fc3ff4e18e842a7ad7072'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/rumah_bumn'

# Koneksi ke database
db = SQLAlchemy(app)

# Konversi SQLAlchemy ke JSON
ma = Marshmallow(app) 

# Enkripsi password
bcrypt = Bcrypt(app)

# Sistem login
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'danger'
login_manager.login_message = ''

import script.routes
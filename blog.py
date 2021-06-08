from flask import Flask, render_template,flash,redirect,url_for,session,logging,request
#from pony.flask import Pony
from pony.orm import *
#from pony.orm import Database, Required, Optional,Session
from datetime import datetime
from wtforms import Form,StringField,TextAreaField,PasswordField, form,validators
from passlib.hash import sha256_crypt

class RegistrationForm(Form):
    name = StringField("İsim Soyisim",validators=[validators.Length(min=4, max=25)])
    email = StringField("Eposta Adresi",validators=[validators.Email(message="Lütfen Geçerli bir email adresi girin!")])
    username = StringField("Kullanıcı Adı",validators=[validators.Length(min=4, max=10)])
    password = PasswordField("Parola",validators=[validators.DataRequired(message="lütfen bir parola belirleyin."),
    validators.EqualTo(fieldname="confirm",message="Parolanız uyuşmuyor!")
    ])
    confirm = PasswordField("Parola Doğrula")


app = Flask(__name__)
app.config.update(dict(
    DEBUG = False,
    #SECRET_KEY = 'secret_xxx',
    PONY = {
        'provider': 'sqlite',
        'filename': 'db.db3',
        'create_db': True
    }
))

db = Database()
db.bind(**app.config['PONY'])

class User(db.Entity):
    name = Required(str)
    email = Required(str)
    username = Required(str,unique=True)
    password = Required(str)


#db.commit()

db.generate_mapping(create_tables=True)

@app.route('/')
def index():
    my_list = []
    return render_template('index.html', my_list = my_list)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=['GET','POST'])
def register():
    form = RegistrationForm(request.form)
    
    if request.method == 'POST' and form.validate():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(form.password.data)
        
        with db_session:
            User(name=name, username=username, email=email, password=password)

        return redirect(url_for('index'))
    else: 
        return render_template('register.html',form=form)

if __name__ == '__main__':
    app.run(debug=True)
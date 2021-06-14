from flask import Flask, render_template,flash,redirect,url_for,session,logging,request
from pony.orm import *
from datetime import datetime
from wtforms import Form,StringField,TextAreaField,PasswordField, form,validators
from passlib.hash import sha256_crypt
from functools import wraps
import time, datetime


# kullanıcı giriş decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Login olun","danger")
            return redirect(url_for('login'))
    return decorated_function

class RegistrationForm(Form):
    name = StringField("İsim Soyisim",validators=[validators.Length(min=4, max=25)])
    email = StringField("Eposta Adresi",validators=[validators.Email(message="Lütfen Geçerli bir email adresi girin!")])
    username = StringField("Kullanıcı Adı",validators=[validators.Length(min=4, max=10)])
    password = PasswordField("Parola",validators=[validators.DataRequired(message="lütfen bir parola belirleyin."),
    validators.EqualTo(fieldname="confirm",message="Parolanız uyuşmuyor!")
    ])
    confirm = PasswordField("Parola Doğrula")


class LoginForm(Form):
    username = StringField("Kullanıcı Adı")
    password = PasswordField("Parola")

class ArticleForm(Form):
    title = StringField("Başık",validators=[validators.Length(min=5),validators.DataRequired(message="Başlık girmek gerek!")])
    content = TextAreaField("İçerik")

app = Flask(__name__)
app.config.update(dict(
    DEBUG = False,
    SECRET_KEY = 'secret_xxxx',
    PONY = {
        'provider': 'sqlite',
        'filename': 'dbname.db', 
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

class Article(db.Entity):
    title = Required(str,unique=True)
    author = Required(str)
    content = Optional(str)
    created_date = Required(datetime.datetime,
                          default=datetime.datetime.now)


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
        password = sha256_crypt.hash(form.password.data)
        
        with db_session:
            User(name=name, username=username, email=email, password=password)
        
        flash("Başarılı bir şekilde kayıt oldunuz.","success")

        return redirect(url_for('login'))
    else: 
        return render_template('register.html',form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        username = form.username.data
        password_entered = form.password.data
        
        with db_session:
            user = User.get(username=username)
        if user is not None:
            hashed_password = user.password
            if sha256_crypt.verify(password_entered, hashed_password):
                flash("Başarılı bir şekilde giriş yaptınız.","success")

                session["logged_in"] = True
                session["username"] = user.username
                return redirect(url_for('index'))
            else: 
                flash("parola yanlış.","danger")    
                return redirect(url_for('login'))
        else: 
            flash("Yanlışlık var.","danger")
            return redirect(url_for('login'))
    else: 
        return render_template('login.html',form = form)

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash("Başarılı bir şekilde çıkış yaptınız.","success")
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    with db_session:
        articles = list(Article.select(lambda a: a.author == session["username"]))    
    return render_template('dashboard.html', articles = articles)

@app.route('/article/add', methods=['GET','POST'])
@login_required
def article_add():
    form = ArticleAddForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        author = session["username"]
        content = form.content.data
        
        with db_session:
            Article(title=title, author=author,content=content)
        
        flash("Makale eklendi.","success")
        return redirect(url_for('dashboard'))
    
    return render_template('article/form.html',form = form, form_task="Makale Ekle")

@app.route('/article/list')
@login_required
def article_list():
    with db_session:
        articles = list(Article.select())
    return render_template('article/list.html',articles = articles)

@app.route('/article/detail/<string:id>')
@login_required
def article_detail(id):
    with db_session:
        article = Article.get(id=id)
    return render_template('article/detail.html',article = article)


@app.route('/article/delete/<string:id>')
@login_required
def article_delete(id):
    with db_session:
        Article[id].delete()
    
    flash("Makale silindi.","success")
    return redirect(url_for('dashboard'))

@app.route('/article/edit/<string:id>', methods=['GET','POST'])
@login_required
def article_edit(id):
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        with db_session:
            article = Article[id]
            title = form.title.data
            content = form.content.data
            article.set(title=title, content=content)
        flash("Makale silindi.","success")
        return redirect(url_for('dashboard'))
    else: 
        with db_session:
            article = Article.get(id=id)
        
        form = ArticleForm()
        form.title.data = article.title
        form.content.data = article.content
        return render_template('article/form.html',form = form, form_task="Makale Düzenle")
        
if __name__ == '__main__':
    app.run(debug=True)
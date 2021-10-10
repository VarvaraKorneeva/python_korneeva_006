import datetime
import os
import sqlite3

from flask import Flask, render_template, url_for, request, flash, get_flashed_messages, g, abort, make_response, \
    session, redirect
from werkzeug.security import generate_password_hash, check_password_hash

from flask_006.flask_database import FlaskDataBase
from flask_006.helpers import check_ext, valid_email, password_complexity

DATABASE = 'flaskapp.db'
DEBUG = True
SECRET_KEY = 'aksj5fksafj23kd23f'
MAX_CONTENT_LENGTH = 3 * 1024 * 1024  # 3 MB

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flaskapp.db')))

app.permanent_session_lifetime = datetime.timedelta(days=1)


def create_db():
    """Creates new database from sql file."""
    db = connect_db()
    with app.open_resource('db_schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def connect_db():
    """Returns connection to apps database."""
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


url_menu_items = {
    'index': 'Главная',
    'second': 'Вторая страница'
}

fdb = None
user = None


# @app.before_first_request
# def before_first_request_func():
#     print('BEFORE_FIRST_REQUEST')


@app.before_request
def before_request_func():
    global fdb
    global user
    fdb = FlaskDataBase(get_db())
    user = session.get('email', None)


# @app.after_request
# def after_request_func(response):
#     print('AFTER_REQUEST')
#     return response


# @app.teardown_request
# def teardown_request_func(response):
#     print('TEARDOWN_REQUEST')
#     return response


@app.route('/')
def index():
    if user:
        return render_template('index.html',
                               menu_url=fdb.get_menu(),
                               posts=fdb.get_posts(),
                               user=user
                               )
    else:
        flash('Авторизуйтесь, чтобы зайти на страницу', 'error')
        return redirect(url_for('login'))


@app.route('/second')
def second():
    if user:
        print(url_for('second'))

        return render_template('second.html',
                               phone="+79542132454",
                               email='user@mail.ru',
                               current_date=datetime.date.today().strftime('%d.%m.%y'),
                               menu_url=fdb.get_menu(),
                               user=user
                               )
    else:
        flash('Авторизуйтесь, чтобы зайти на страницу', 'error')
        return redirect(url_for('login'))


# int, float, path
@app.route('/user/<username>')
def profile(username):
    url_for('profile')

    return f"<h1>Hello {username}!</h1>"


@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    if user:
        if request.method == 'POST':
            name = request.form['name']
            post_content = request.form['post']
            file = request.files.get('photo')
            if len(name) > 5 and len(post_content) > 10:
                if file and check_ext(file.filename):
                    try:
                        img = file.read()
                    except FileNotFoundError:
                        flash('Ошибка чтения файла', 'error')
                        img = None
                res = fdb.add_post(name, post_content, img)
                if not res:
                    flash('Post were not added. Unexpected error', category='error')
                else:
                    flash('Success', category='success')
            else:
                flash('Post name or content too small', category='error')
        return render_template('add_post.html', menu_url=fdb.get_menu(), user=user)
    else:
        flash('Авторизуйтесь, чтобы зайти на страницу', 'error')
        return redirect(url_for('login'))


@app.route('/post/<int:post_id>')
def post_content(post_id):
    if user:
        title, content = fdb.get_post_content(post_id)
        if not title:
            abort(404)

        return render_template('post.html', menu_url=fdb.get_menu(), title=title, content=content, user=user)
    else:
        flash('Авторизуйтесь, чтобы зайти на страницу', 'error')
        return redirect(url_for('login'))


@app.route('/post/<int:post_id>')
def post_photo(post_id):
    if user:
        photo = fdb.get_post_photo(post_id)
        response = make_response(photo)
        response.headers['Content-type'] = 'image/'

        return response
    else:
        flash('Авторизуйтесь, чтобы зайти на страницу', 'error')
        return redirect(url_for('login'))


@app.route('/login', methods=['POST', 'GET'])
def login():
    url_for('login')
    if request.method == 'GET':
        return render_template('login.html', menu_url=fdb.get_menu())
    elif request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if not password:
            flash('пароль не указан', category='unfilled_error')

        if valid_email(email):
            res = fdb.find_email(email)
            if not res:
                flash('Email или пароль неверный', 'error')
            elif check_password_hash(res['password'], password):
                session['email'] = email
                return redirect(url_for('index'))
            else:
                flash('Email или пароль неверный', 'error')

        return render_template('login.html', menu_url=fdb.get_menu())
    else:
        raise Exception(f'method {request.method} not allowed')


@app.route('/logout')
def logout():
    session['email'] = None
    return redirect(url_for('login'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    url_for('register')
    if request.method == 'GET':
        return render_template('register.html', menu_url=fdb.get_menu())
    elif request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if not password or not password2:
            flash('пароль не указан', category='unfilled_error')

        if valid_email(email):
            if fdb.find_email(email):
                flash('Пользователь уже существует', 'error')

            elif password == password2:
                if password_complexity(password):
                    hash = generate_password_hash(password)
                    fdb.add_user(email, hash)
                    flash('Registration successful', category='success')
                    return redirect(url_for('login'))
            else:
                flash('Пароли не совпадают', category='validation_error')

        print(get_flashed_messages(True))

    return render_template('register.html', menu_url=fdb.get_menu())


@app.errorhandler(404)
def page_not_found(error):
    return '<h1>This post does not exists</h1>'


@app.teardown_appcontext
def close_db(error):
    """Close database connection if it exists"""
    if hasattr(g, 'link_db'):
        g.link_db.close()


@app.route('/test_response')
def test_response():
    fdb = FlaskDataBase(get_db())
    content = render_template('index.html',
                              menu_url=fdb.get_menu(),
                              posts=fdb.get_posts()
                             )
    response_obj = make_response(content)
    response_obj.headers['content-type'] = 'text/plain'
    return response_obj


@app.route('/test_response2')
def test_response2():
    return '<h1>test_response</h1>', 404


@app.route('/test_login')
def test_login():
    log = ''
    if request.cookies.get('visited'):
        log = request.cookies.get('visited')

    response = make_response(f'<h1>visited cookie: {log}</h1>')
    response.set_cookie('visited', 'yes')
    return response


@app.route('/test_login1')
def test_login1():
    log = ''
    if request.cookies.get('visited'):
        log = request.cookies.get('visited')

    response = make_response(f'<h1>visited cookie: {log}</h1>')
    response.delete_cookie('visited')
    return response


@app.route('/session_example')
def session_example():
    counter = session.get('visits', 1)
    session['visits'] = counter + 1

    return f'<h1>Number of visits: {session["visits"]}</h1>'


data = [1, 2, 3]


@app.route('/session_example2')
def session_example2():
    session.permanent = True
    if data not in session:
        session['data'] = data
    else:
        session['data'][0] += 1
    session.modified = True

    return f'<h1>Number of visits:</h1>'


if __name__ == '__main__':
    app.run(debug=True)

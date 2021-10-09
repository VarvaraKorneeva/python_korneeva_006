import datetime
import os
import sqlite3

from flask import Flask, render_template, url_for, request, flash, get_flashed_messages, g, abort, make_response, \
    session

from flask_006.flask_database import FlaskDataBase
from flask_006.helpers import check_ext

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


@app.before_first_request
def before_first_request_func():
    print('BEFORE_FIRST_REQUEST')


@app.before_request
def before_request_func():
    global fdb
    fdb = FlaskDataBase(get_db())
    print('BEFORE_REQUEST')


@app.after_request
def after_request_func(response):
    print('AFTER_REQUEST')
    return response


@app.teardown_request
def teardown_request_func(response):
    print('TEARDOWN_REQUEST')
    return response


@app.route('/')
def index():
    return render_template('index.html',
                           menu_url=fdb.get_menu(),
                           posts=fdb.get_posts()
                           )


@app.route('/page2')
def second():
    menu_items = [
        'Главная',
        'Каталог',
        'Доставка',
        'О нас'
    ]

    print(url_for('second'))

    return render_template('second.html',
                           phone="+79542132454",
                           email='user@mail.ru',
                           current_date=datetime.date.today().strftime('%d.%m.%y'),
                           menu_url=fdb.get_menu()
                           )


# int, float, path
@app.route('/user/<username>')
def profile(username):
    url_for('profile')

    return f"<h1>Hello {username}!</h1>"


@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    fdb = FlaskDataBase(get_db())
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

    return render_template('add_post.html', menu_url=fdb.get_menu())


@app.route('/post/<int:post_id>')
def post_content(post_id):
    fdb = FlaskDataBase(get_db())
    title, content = fdb.get_post_content(post_id)
    if not title:
        abort(404)

    return render_template('post.html', menu_url=fdb.get_menu(), title=title, content=content)


@app.route('/post/<int:post_id>')
def post_photo(post_id):
    photo = fdb.get_post_photo(post_id)
    response = make_response(photo)
    response.headers['Content-type'] = 'image/'

    return response


@app.route('/login', methods=['POST', 'GET'])
def login():
    fdb = FlaskDataBase(get_db())
    url_for('login')
    print(request.method)
    if request.method == 'GET':
        return render_template('login.html', menu_url=fdb.get_menu())
    elif request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if not email:
            flash('Email не указан', category='unfilled_error')
        else:
            if '@' not in email or '.' not in email:
                flash('Некоректный email', category='validation_error')
        if not password:
            flash('пароль не указан', category='unfilled_error')

        print(request)
        print(get_flashed_messages(True))
        return render_template('login.html', menu_url=fdb.get_menu())
    else:
        raise Exception(f'method {request.method} not allowed')


@app.route('/register', methods=['POST', 'GET'])
def register():
    url_for('register')
    fdb = FlaskDataBase(get_db())
    if request.method == 'GET':
        return render_template('register.html', menu_url=fdb.get_menu())
    elif request.method == 'POST':
        # print(request)
        email = request.form.get('email')
        print(email)
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if password == password2:
            fdb.add_user(email, password)
            flash('Registration successful', category='success')
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

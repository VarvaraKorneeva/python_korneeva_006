from flask import Blueprint, request, redirect, session, url_for, flash, render_template, g

admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')


def login_admin():
    session['admin_logged'] = 1


def is_logged():
    return bool(session.get('admin_logged', None))


def logout_admin():
    session.pop('admin_logged', None)


db = None


@admin.before_request
def before_request():
    global db
    db = g.get('link_db')


@admin.teardown_request
def teardown_request():
    global db
    db = None
    return request


@admin.route('/')
def index():
    if is_logged():
        return render_template('admin/index.html')
    else:
        return redirect(url_for('.login'))


@admin.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        if request.form['user'] == 'admin' and request.form['passsword'] == '123':
            login_admin()
            return redirect(url_for('.index'))
        else:
            flash('неверный логин или пароль', 'error')


@admin.route('/logout')
def logout():
    logout_admin()
    return redirect(url_for('.index'))


@admin.route('/posts')
def posts():
    if not is_logged():
        return redirect(url_for('.login'))

    posts = []
    if db:
        try:
            cur = db.cursor()
            cur.execute('SELECT title, content FROM Posts')
        except:
            pass

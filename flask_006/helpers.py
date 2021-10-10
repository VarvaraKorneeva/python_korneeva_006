from flask import flash

ALLOWED_EXTENSIONS = ['png']
SPECIAL_CHARACTERS = ['!', '#', '$', '%', '&', '?', '/']
NUMBERS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']


def check_ext(filename):
    ext = filename.rsplit('.', 1)[1]
    return ext.lower() in ALLOWED_EXTENSIONS


def valid_email(email):
    if not email:
        flash('Email не указан', category='unfilled_error')
        return False
    elif '@' not in email or '.' not in email:
        flash('Некоректный email', category='validation_error')
        return False

    return True


def password_complexity(password):
    if len(password) < 8:
        flash('Пароль должен содержать минимум 8 символов', 'error')
        return False
    counter = 0
    for character in SPECIAL_CHARACTERS:
        if character in password:
            counter += 1
    if counter == 0:
        flash(f'Пароль должен содержать минимум один символ из: {SPECIAL_CHARACTERS}', 'error')
        return False
    if password == password.lower():
        flash('Пароль должен содержать минимум один прописной символ', 'error')
        return False
    counter_2 = 0
    for number in NUMBERS:
        if number in password:
            counter_2 += 1
    if counter_2 == 0:
        flash('Пароль должен содержать минимум одну цифру', 'error')
        return False

    return True

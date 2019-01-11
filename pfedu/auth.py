from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from flask_login import LoginManager, logout_user, login_user, \
        login_required, current_user

from pfedu.models import User
from pfedu.forms import LoginForm

bp = Blueprint('auth', __name__, url_prefix='/auth')
login_mgr = LoginManager()
login_mgr.login_view = 'auth.login'

#@bp.route('/register', methods=('GET', 'POST'))
#def register():
#    if request.method == 'POST':
#        username = request.form['username']
#        password = request.form['password']
#        error = None
#
#        if not username:
#            error = 'Username is required.'
#        elif not password:
#            error = 'Password is required.'
#        elif user:
#            error = 'User {} is already registered.'.format(username)
#
#        if error is None:
#            db.execute(
#                'INSERT INTO user (username, password) VALUES (?, ?)',
#                (username, generate_password_hash(password))
#            )
#            db.commit()
#            return redirect(url_for('auth.login'))
#
#        flash(error)
#
#    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        passwd = form.passwd.data
        user = User.query.filter_by(username=username).first()
        error = None

        if user is None:
            error = 'Incorrect username.'
        elif not user.check_password(passwd):
            error = 'Incorrect password.'

        if error is None:
            login_user(user)
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You logged out')

    return redirect(url_for('auth.login'))

@login_mgr.user_loader
def load_user(id):
    return User.query.get(int(id))

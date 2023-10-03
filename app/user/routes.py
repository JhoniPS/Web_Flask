from app.extensions import db
from app.user import user
from app.user.models import User
from app.user.forms import SignupForm, LoginForm, ResetForm, PasswordResetForm
from app.helper.mail import send_email
from flask import render_template, redirect, url_for
from flask_login import login_user, logout_user, current_user


@user.route('/signup', methods=['get', 'post'])
def signup():
    if current_user.is_authenticated:
        return 'You need to logout to access this page!'
    form = SignupForm()
    if form.validate_on_submit():
        user = User(name=form.name.data, username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return "<h1>User Added</h1>"
    return render_template('signup.html', form=form)


@user.route('/login', methods=['get', 'post'])
def login():
    if current_user.is_authenticated:
        return 'You need to logout to access this page!'
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return "User Logged In"
    return render_template('login.html', form=form)


@user.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('user.login'))


# ------------------------------------------------------------------------------------------------------------------- #
# -- ERROR HERE (ABOUT THE expires_sec) IN LINE 46
@user.route('/reset', methods=['get', 'post'])
def reset():
    if current_user.is_authenticated:
        return 'You need to logout to access this page!'
    form = ResetForm()
    if form.validate_on_submit():
        # -- HERE U CHANGE 'USER' WITH 'EMAIL' ON PASSWORD RESETTING
        user = User.query.filter_by(username=form.username.data).first_or_404()
        if user:
            token = user.get_reset_token()
            # -- EMAIL SENDER HERE!!
            send_email(subject='Password Reset', to=user.email,
                       text_body='If your are getting this, it means you are unable to see HTML page. Please contact Admin.',
                       template='reset', token=token)
            return '<h1>Mail has been send. Check your Inbox.</h1>'
    return render_template('reset.html', form=form)


@user.route('reset/<token>', methods=['get', 'post'])
def reset_request(token):
    if current_user.is_authenticated:
        return 'You need to logout to access this page!'
    form = PasswordResetForm()
    user = User.verify_reset_token(token)
    if user:
        if form.validate_on_submit():
            user.set_password(form.password.data)
            db.session.commit()
            return 'User Logged In'
        return render_template('password_reset.html', form=form)
    else:
        return redirect(url_for('user.reset'))
# ------------------------------------------------------------------------------------------------------------------- #

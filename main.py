from flask import Flask, render_template, url_for, redirect, flash, session
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from authlib.integrations.flask_client import OAuth
import os
from forms import RegisterForm, LoginForm
from bet import bet
from models import app, db, User 
from datetime import timedelta


app.register_blueprint(bet, url_prefix="/dashboard")
@app.before_request
def make_session_permanent():
    session.permanent = True
    


SECRET_KEY = os.urandom(50)
app.config['SECRET_KEY'] = SECRET_KEY


bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

  
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id='391311853445-mop2sp2grm183f9f5a29drdj0gv3qh9a.apps.googleusercontent.com',
    client_secret='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',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    authorize_redirect_uri='https://flask-app-6qzw.onrender.com/auth/callback',
    base_url='https://www.googleapis.com/oauth2/v1/',
    jwks_uri='https://www.googleapis.com/oauth2/v3/certs',
    client_kwargs={'scope': 'openid profile email'}
)

@app.route("/")
def index():
    
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if 'user' in session:
        # Automatically log in the user if they are in the session
        user = User.query.get(session['user']['id'])
        if user:
            login_user(user)
            return redirect(url_for('bet.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            flash('You were successfully logged in', 'success')
            login_user(user)
            session['user'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'pfp_image': user.pfp_image          
}  
            return redirect(url_for('bet.dashboard'))
        else:
            flash("Wrong password or email", 'error')
    return render_template('login.html', form=form)

@app.route('/login/google')
def login_google():
    redirect_uri = url_for('auth_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/auth/callback')
def auth_callback():
    token = google.authorize_access_token()
    resp = google.get('https://www.googleapis.com/oauth2/v1/userinfo')
    user_info = resp.json()
    user_email = user_info['email']
    user = User.query.filter_by(email=user_email).first()
    
    if user is None:
        # Create a new user if it doesn't exist
        default_password = bcrypt.generate_password_hash(os.urandom(24)).decode('utf-8')
        user = User(email=user_email, username=user_info['name'], password=default_password)
     
        db.session.add(user)
        db.session.commit()

    session['user'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'pfp_image': user.pfp_image         
        }
      
    login_user(user)
    
    return redirect(url_for('bet.dashboard'))


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    flash('You were successfully logged out', 'success')
    logout_user()
    session.pop('user', None)  # Remove the user from the session
    return redirect(url_for('login'))

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if not User.query.filter_by(username=form.username.data).first() and not User.query.filter_by(email=form.email.data).first():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('You successfully created an account', 'success')
            return redirect(url_for('login'))
        
    return render_template('register.html', form=form)


if __name__ == "__main__":
    with app.app_context():
        #db.drop_all()
        db.create_all()
    app.run(debug=True)
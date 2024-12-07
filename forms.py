from flask import Flask, render_template, flash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, EmailField, IntegerField, FormField
from wtforms.validators import InputRequired, Length, ValidationError, NumberRange, Optional
from models import User, Team # Import from models.py


class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    email = EmailField(validators=[InputRequired(), Length(min=4, max=30)], render_kw={"placeholder": "Email"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user = User.query.filter_by(username=username.data).first()
        if existing_user:
            flash("That username already exists. Please choose a different one.")
            raise ValidationError("That username already exists. Please choose a different one.")

    def validate_email(self, email):
        existing_email = User.query.filter_by(email=email.data).first()
        if existing_email:
            flash("That email already exists. Please choose a different one.")
            raise ValidationError("That email already exists. Please choose a different one.")
        
class LoginForm(FlaskForm):
    email = EmailField(validators=[InputRequired(), Length(min=4, max=30)], render_kw={"placeholder": "Email"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")

class CreateGameForm(FlaskForm):
    name = StringField(validators=[InputRequired(), Length(min=4, max=30)], render_kw={"placeholder": "Name"})
    type_of_game = SelectField('Game type',choices=[('Football', 'Football'), ('Basketball', 'Basketball')], validators=[InputRequired()])
    submit = SubmitField("Create")

class JoinGameForm(FlaskForm):
    invite = IntegerField(validators=[InputRequired()], render_kw={"placeholder": "Invite code"})
    submit = SubmitField("Submit")

class Teams(FlaskForm):
    team_one = StringField(validators=[InputRequired(), Length(min=1, max=30)], render_kw={"placeholder": "Team 1"})
    team_two = StringField(validators=[InputRequired(), Length(min=1, max=30)], render_kw={"placeholder": "Team 2"})
    
    bet_amount = IntegerField(validators=[InputRequired(), NumberRange(min=1, max=999)], render_kw={"placeholder": "Default Bet"})
    submit = SubmitField("Submit")

class Results(FlaskForm):
    result_one = IntegerField(validators=[InputRequired(), NumberRange(min=0, max=999)], render_kw={"placeholder": "Result 1"})
    result_two = IntegerField(validators=[InputRequired(), NumberRange(min=0, max=999)], render_kw={"placeholder": "Result 2"})
    submit = SubmitField("Submit")
    
class CreateBets(FlaskForm):
    result_1 = IntegerField('Result 1', validators=[Optional(), NumberRange(min=0, max=999)], render_kw={"placeholder": "Result 1"})
    result_2 = IntegerField('Result 2', validators=[Optional(), NumberRange(min=0, max=999)], render_kw={"placeholder": "Result 2"})
    result_3 = IntegerField('Distance', validators=[Optional(), NumberRange(min=0, max=999)], render_kw={"placeholder": "Distance"})
    submit = SubmitField("Submit")

    def __init__(self, *args, game_type=None, **kwargs):
        super(CreateBets, self).__init__(*args, **kwargs)
        if game_type == "Football":
            self.result_1.validators = [InputRequired(), NumberRange(min=0, max=999)]
            self.result_2.validators = [InputRequired(), NumberRange(min=0, max=999)]
            del self.result_3
        elif game_type == "Basketball":
            self.result_3.validators = [InputRequired(), NumberRange(min=0, max=999)]
            del self.result_1
            del self.result_2
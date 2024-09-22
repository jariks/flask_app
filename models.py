from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_migrate import Migrate


app = Flask(__name__)
#Local host: "postgresql://postgres:1234@localhost:5432/master"

#Production: "postgresql://user:vBZETgPrFK60qZLscLn0CMUMR3edaHtd@dpg-cro4kli3esus73buhllg-a.frankfurt-postgres.render.com/master_zh4r"

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://user:vBZETgPrFK60qZLscLn0CMUMR3edaHtd@dpg-cro4kli3esus73buhllg-a.frankfurt-postgres.render.com/master_zh4r"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

migrate = Migrate(app, db)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    pfp_image =  db.Column(db.String(150), nullable=False, default='images/default_pfp.webp')
    created_games = db.relationship('Game', backref='creator', lazy=True)
    joined_games = db.relationship('Player', backref='user', lazy=True)
    

    def __repr__(self):
        return f'<User {self.username}>'


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_key = db.Column(db.Integer, unique=True, nullable=False)
    type_of_game = db.Column(db.String(100))

    teams = db.relationship('Team', backref='game', lazy=True)
    players = db.relationship('Player', backref='game', lazy=True)

    def __repr__(self):
        return f'<Game {self.name}>'


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    score = db.Column(db.String(20), nullable=True, default=None)
    status = db.Column(db.Boolean, unique=False, default=False)
    default_bet = db.Column(db.Integer, unique=False, nullable=False)

    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    bets = db.relationship('Bet', backref='team', lazy=True)

    def __repr__(self):
        return f'<Team {self.name}>'


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    bets = db.relationship('Bet', backref='player', lazy=True)

    def __repr__(self):
        return f'<Player User ID {self.user_id} Game ID {self.game_id}>'


class Bet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    bet = db.Column(db.String(5), nullable=False)

    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    
    

    def __repr__(self):
        return f'<Bet {self.amount} on Team {self.team_id} by Player {self.player_id}>'

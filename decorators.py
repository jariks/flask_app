from functools import wraps
from flask import abort, request, current_app, g
from flask_login import current_user
from models import Game, Player

def game_access_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        game_key = kwargs.get('game_key')
        
        if not game_key:
            current_app.logger.error("Game key not provided")
            abort(400, description="Game key is required")

        game = Game.query.filter_by(game_key=game_key).first()
        if not game:
            current_app.logger.error(f"Game with key {game_key} not found")
            abort(404, description="Game not found")

        is_creator = game.creator_id == current_user.id
        is_player = Player.query.filter_by(user_id=current_user.id, game_id=game.id).first() is not None

        if not (is_creator or is_player):
            current_app.logger.warning(f"User {current_user.id} attempted to access game {game_key} without permission")
            abort(403, description="You don't have access to this game")

        # If we've made it this far, the user has access. Store game in flask.g for access in the view
        g.game = game
        return f(*args, **kwargs)
    return decorated_function
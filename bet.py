from flask import Flask, render_template, url_for, redirect, session, Blueprint, flash, request
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from models import db, Game, Player, User, Team, Bet
from forms import CreateGameForm, JoinGameForm, Teams, Results, CreateBets
import random
from calc import gather_speculation_data_for_team, determine_winners

# Define the blueprint for the bet module
bet = Blueprint("bet", __name__, static_folder="static", template_folder="templates")

# Dashboard route to display created and joined games
@bet.route('/', methods=['GET', 'POST'])
@login_required
def dashboard():
    current_created_games = Game.query.filter_by(creator_id=current_user.id).all()
    current_joined_games = [player.game for player in Player.query.filter_by(user_id=current_user.id).all()]
    return render_template('dashboard.html', created_games=current_created_games, joined_games=current_joined_games)

@bet.route('/profile/<int:user_id>', methods=['GET'])
@login_required
def profile(user_id):
    user = User.query.get_or_404(user_id)
    created_games = Game.query.filter_by(creator_id=user_id).all()

    joined_games = [player.game for player in user.joined_games]
    

    bets = Bet.query.filter_by(player_id=user_id).all()
    
    return render_template('profile.html', user=user, created_games=created_games, joined_games=joined_games, bets=bets, current_user=current_user)


@bet.route('/game/<int:game_key>', methods=["GET", "POST"])
@login_required
def game_details(game_key):
    form = Teams()

    game = Game.query.filter_by(game_key=game_key).first_or_404()
    players = Player.query.filter_by(game_id=game.id).all()

    if form.validate_on_submit():
        team_string = f"{form.team_one.data}/{form.team_two.data}"
        team_defautl_bet = form.bet_amount.data
        new_team = Team(name=team_string,default_bet=team_defautl_bet, game_id=game.id)
        db.session.add(new_team)
        db.session.commit()

    player_details = []
    for player in players:
        user = User.query.get(player.user_id)
        if user:
            player_details.append({
                'player_id': player.id,  
                'player': player,
                'username': user.username
            })

    
    teams = Team.query.filter_by(game_id=game.id).all()

    # Render a template with the game details
    return render_template('game_details.html',form=form, teams=teams, game=game, players=player_details, current_user=current_user, game_key=game_key)

@bet.route('/team/<int:team_id>', methods=["GET", "POST"])
@login_required
def team_details(team_id):
    team = Team.query.get_or_404(team_id)

    if team.status == False:

        form = Results()
        form_bets = CreateBets()
        game = team.game
        current_bets = Bet.query.filter_by(team_id=team.id).all()
        
        bets = []
        for bet in current_bets:
            user = bet.player.user
            if user:
                bets.append({
                    'amount': bet.amount,
                    'bet': bet.bet,
                    'username': user.username
                })
        current_player = Player.query.filter_by(user_id=current_user.id, game_id=game.id).first()
        if form_bets.validate_on_submit():
            # Check if a bet has already been placed for this user and team
            existing_bet = Bet.query.filter_by(team_id=team.id, player_id=current_player.id).first()
            if existing_bet:
                flash("You have already placed a bet for this team.", "warning")
            else:
                results = f"{form_bets.result_1.data}/{form_bets.result_2.data}"
                bet = Bet(
                        amount=team.default_bet,
                        bet=results,
                        team_id=team.id,
                        player_id=current_player.id,
                        
                        )
                
                db.session.add(bet)
                db.session.commit()
                flash("You have successfully placed a bet", "success")

        if form.validate_on_submit():
           
            results = f"{form.result_one.data}/{form.result_two.data}"
            team.score = results

            db.session.commit()
            if team.score == results:  # Confirm the update was successful
                flash("You have successfully updated the results", "success")
            else:
                flash("Failed to update results", "danger")

        return render_template("team_details.html",
                                form=form,
                                form_bets=form_bets,
                                game=game,
                                team=team,
                                current_user=current_user,
                                bets=bets
                                )
    else:
        return redirect(url_for("bet.team_results", team_id=team.id))

@bet.route('/team/results/<int:team_id>', methods=['GET', 'POST'])
@login_required
def team_results(team_id):
    team = Team.query.filter_by(id=team_id).first()
    bet = Bet.query.filter_by(team_id=team_id).all()
    if team.score:
        if bet:
            
            team.status = True
            db.session.commit()
            players_speculations = gather_speculation_data_for_team(team_id)
            results = determine_winners(team.score, players_speculations)
            return render_template("results.html", results=results, team=team)
        else:
            flash("No bets on team")
            return redirect(url_for("bet.team_details", team_id=team_id))
    else:
        flash("No team score")
        return redirect(url_for("bet.team_details", team_id=team_id))

# Route to create a new game
@bet.route('/create_game', methods=['GET', 'POST'])
@login_required
def create_game():
    form = CreateGameForm()
    # Assign a unique game invite key
    if 'game_key' not in session:
        key_of_game = random.randint(10000, 99999)
        while Game.query.filter_by(game_key=key_of_game).first():
            key_of_game = random.randint(10000, 99999)
        session['game_key'] = key_of_game
    else:
        key_of_game = session['game_key']

    if form.validate_on_submit():
        game_name = form.name.data
        
        # Create and add the new game to the database
        new_game = Game(name=game_name, creator_id=current_user.id, game_key=key_of_game)
        
        db.session.add(new_game)
        db.session.commit()
        
        # Redirect to the dashboard after creating the game
        flash("Game created succesfuly", "success")
        session.pop('game_key', None)
        return redirect(url_for("bet.dashboard"))
    
    
    # Render the create game template with the form
    return render_template("create_game.html", form=form, invite=key_of_game)

# Route to join an existing game
@bet.route('/join_game', methods=['GET', 'POST'])
@login_required
def join_game():
    form = JoinGameForm()
    
    if form.validate_on_submit():
        invite_code = form.invite.data
        current_game = Game.query.filter_by(game_key=invite_code).first()

        
        if current_game is None:
            # Flash a message if the game is not found
            flash("Game not found!", "danger")
            return redirect(url_for("bet.join_game"))
        
        if current_game.creator_id == current_user.id:
            flash("Can't join your own game", "error")
            return redirect(url_for("bet.join_game"))
        # Check if the user is already in the game
        existing_player = Player.query.filter_by(user_id=current_user.id, game_id=current_game.id).first()
        if existing_player:
            # Flash a message if the user is already in the game
            flash("You are already in this game!", "warning")
            return redirect(url_for("bet.dashboard"))
        
        # Add the user as a new player in the game
        new_player = Player(user_id=current_user.id, game_id=current_game.id)
        db.session.add(new_player)
        db.session.commit()
        
        # Redirect to the dashboard after joining the game
        return redirect(url_for("bet.dashboard"))
    
    # Render the join game template with the form
    return render_template("join_game.html", form=form)

@bet.route('/delete_game/<int:game_id>')
@login_required
def delete_game(game_id):
    try:
        game_to_delete = Game.query.filter_by(id=game_id).first_or_404()
        players_to_delete = Player.query.filter_by(game_id=game_id).all()
        teams_to_delete = Team.query.filter_by(game_id=game_id).all()
        
        # Delete all associated bets first to avoid integrity errors
        for team in teams_to_delete:
            bets_to_delete = Bet.query.filter_by(team_id=team.id).all()
            for bet in bets_to_delete:
                db.session.delete(bet)
        db.session.commit()  # Commit after deleting bets
        
        # Delete teams
        for team in teams_to_delete:
            db.session.delete(team)
        db.session.commit()  # Commit after deleting teams
        
        # Delete players
        for player in players_to_delete:
            db.session.delete(player)
        db.session.commit()  # Commit after deleting players
        
        # Finally, delete the game itself
        db.session.delete(game_to_delete)
        db.session.commit()
        
        flash("Game Deleted Successfully")
    except Exception as e:
        db.session.rollback()
        flash(f"Something went wrong: {str(e)}")
    
    return redirect(url_for("bet.dashboard"))


@bet.route('/delete_team/<int:team_id>/<int:game_key>')
@login_required
def delete_team(team_id, game_key):
    try:
        team_to_delete = Team.query.filter_by(id=team_id).first_or_404()
        bets_to_delete = Bet.query.filter_by(team_id=team_id).all()
        
        # Delete associated bets first
        for bet in bets_to_delete:
            db.session.delete(bet)
        db.session.commit()  # Commit after deleting bets
        
        # Then delete the team
        db.session.delete(team_to_delete)
        db.session.commit()  # Commit after deleting the team
        
        flash("Team Deleted Successfully")
    except Exception as e:
        db.session.rollback()
        flash(f"Something went wrong: {str(e)}")
    
    return redirect(url_for("bet.game_details", game_key=game_key))


@bet.route('/delete_player/<int:player_id>/<int:game_key>')
@login_required
def delete_player(player_id, game_key):
    try:
        player_to_delete = Player.query.filter_by(id=player_id).first_or_404()
        bets_to_delete = Bet.query.filter_by(player_id=player_id).all()
        
        # Delete associated bets first
        for bet in bets_to_delete:
            db.session.delete(bet)
        db.session.commit()  # Commit after deleting bets
        
        # Then delete the player
        db.session.delete(player_to_delete)
        db.session.commit()  # Commit after deleting the player
        
        flash("Player Removed Successfully")
    except Exception as e:
        db.session.rollback()
        flash(f"Something went wrong: {str(e)}")
    
    return redirect(url_for("bet.game_details", game_key=game_key))

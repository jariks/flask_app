from models import app, db, User, Game, Team, Player, Bet
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

def create_test_data():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        # Create users
        user1 = User(username='testuser1', email='test1@example.com', password=bcrypt.generate_password_hash('password123').decode('utf-8'))
        user2 = User(username='testuser2', email='test2@example.com', password=bcrypt.generate_password_hash('password123').decode('utf-8'))
        user3 = User(username='testuser3', email='test3@example.com', password=bcrypt.generate_password_hash('password123').decode('utf-8'))
        db.session.add_all([user1, user2, user3])
        db.session.commit()

        # Create a game
        game = Game(name='Test Game', creator_id=user1.id, game_key=12345)
        db.session.add(game)
        db.session.commit()

        # Create teams
        team1 = Team(name='Team A/Team B', default_bet=5, game_id=game.id)
        team2 = Team(name='Team B/Team A', default_bet=10, game_id=game.id)
        db.session.add_all([team1, team2])
        db.session.commit()

        # Add players to the game
        
        player2 = Player(user_id=user2.id, game_id=game.id)
        player3 = Player(user_id=user3.id, game_id=game.id)
        db.session.add_all([player2, player3])
        db.session.commit()

        # Create bets
        bet1 = Bet(amount=team1.default_bet, bet='1/2', team_id=team1.id, player_id=player3.id)
        bet2 = Bet(amount=team1.default_bet, bet='1/3', team_id=team1.id, player_id=player2.id)
        bet3 = Bet(amount=team2.default_bet, bet='1/2', team_id=team2.id, player_id=player3.id)
        bet4 = Bet(amount=team2.default_bet, bet='1/3', team_id=team2.id, player_id=player2.id)
        
        db.session.add_all([bet1, bet2, bet3, bet4])
        db.session.commit()

def verify_data():
    with app.app_context():
        # Verify users
        users = User.query.all()
        print(f"Number of users: {len(users)}")
        for user in users:
            print(f"User: {user.username}, Email: {user.email}")

        # Verify games
        games = Game.query.all()
        print(f"\nNumber of games: {len(games)}")
        for game in games:
            print(f"Game: {game.name}, Creator: {game.creator.username}")

        # Verify teams
        teams = Team.query.all()
        print(f"\nNumber of teams: {len(teams)}")
        for team in teams:
            print(f"Team: {team.name}, Game: {team.game.name}")

        # Verify players
        players = Player.query.all()
        print(f"\nNumber of players: {len(players)}")
        for player in players:
            print(f"Player: {player.user.username}, Game: {player.game.name}")

        # Verify bets
        bets = Bet.query.all()
        print(f"\nNumber of bets: {len(bets)}")
        for bet in bets:
            print(f"Bet: {bet.amount} on {bet.team.name} by {bet.player.user.username}")

if __name__ == '__main__':
    create_test_data()
    verify_data()
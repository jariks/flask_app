from sqlalchemy.orm import joinedload
from models import User, Bet, Player
from flask import flash

def gather_speculation_data_for_team(team_id):
    players_speculations = []

    bets = Bet.query.options(
        joinedload(Bet.team),
        joinedload(Bet.player).joinedload(Player.user),
        joinedload(Bet.player).joinedload(Player.game)
    ).filter_by(team_id=team_id).all()

    for bet in bets:
        team = bet.team
        player = bet.player
        if player is None:
            print(f"Warning: Bet {bet.id} has no associated player")
            continue
        game = player.game
        user = player.user

        if None in (team, game, user):
            print(f"Warning: Incomplete data for bet {bet.id}")
            continue

        guessed_score = bet.bet

        speculation = {
            "username": user.username,
            "guessed_score": guessed_score,
            "bet_amount": bet.amount,
            "team_name": team.name,
            "team_score": team.score,
            "game_name": game.name,
            "game_key": game.game_key,
            "player_id": player.id,
            "team_id": team.id,
        }
        players_speculations.append(speculation)

    return players_speculations

def calculate_distance(actual_score, guessed_score):
    return abs(actual_score[0] - guessed_score[0]) + abs(actual_score[1] - guessed_score[1])

def determine_winners(actual_score_str, players_speculations):
    try: 
        actual_score = tuple(map(int, actual_score_str.split('/')))
    except:
        flash("No score added")
        return []

    total_bet = sum([d['bet_amount'] for d in players_speculations])
    
    min_distance = float('inf')
    winners = []
    
    for d in players_speculations:
        player_id = d["player_id"]
        player = d['username']
        guessed_score_str = d["guessed_score"]
        bet = d["bet_amount"]

        guessed_score = tuple(map(int, guessed_score_str.split('/')))
        distance = calculate_distance(actual_score, guessed_score)
        
        if distance < min_distance:
            min_distance = distance
            winners = [(player_id, player, bet)]
        elif distance == min_distance:
            winners.append((player_id, player, bet))
            
    if not winners:
        return [(d["player_id"], d['username'], d["guessed_score"], d["bet_amount"], -d["bet_amount"]) for d in players_speculations]
    
    prize_per_winner = total_bet / len(winners)
    
    results = []
    for d in players_speculations:
        player_id = d["player_id"]
        player = d['username']
        guessed_score_str = d["guessed_score"]
        bet = d["bet_amount"]

        if player_id in [winner[0] for winner in winners]:
            net_gain_or_loss = prize_per_winner - bet  # Winner gets prize share minus their bet
        else:
            net_gain_or_loss = -bet  # Loser loses their bet
        results.append((player_id, player, guessed_score_str, bet, net_gain_or_loss))
    
    return results

# Test function
def test_determine_winners():
    actual_score = "2/1"
    players_speculations = [
        {"player_id": 1, "username": "Alice", "guessed_score": "7/1", "bet_amount": 15},
        {"player_id": 2, "username": "Bob", "guessed_score": "6/1", "bet_amount": 15},
        {"player_id": 3, "username": "Charlie", "guessed_score": "3/0", "bet_amount": 15},
    ]

    results = determine_winners(actual_score, players_speculations)
    
    print("Test Results:")
    for result in results:
        print(f"Player ID: {result[0]}, Name: {result[1]}, Guess: {result[2]}, Bet: {result[3]}, Net Gain/Loss: {result[4]}")

# Run the test
if __name__ == "__main__":
    test_determine_winners()
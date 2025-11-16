import random
from collections import defaultdict

def play(player1, player2, num_games, verbose=False):
    p1_prev_play = ""
    p2_prev_play = ""
    results = {"p1": 0, "p2": 0, "tie": 0}
    
    for _ in range(num_games):
        p1_play = player1(p2_prev_play)
        p2_play = player2(p1_prev_play)
        
        if p1_play == p2_play:
            results["tie"] += 1
            winner = "Tie."
        elif (p1_play == "P" and p2_play == "R") or \
             (p1_play == "R" and p2_play == "S") or \
             (p1_play == "S" and p2_play == "P"):
            results["p1"] += 1
            winner = "Player 1 wins!"
        else:
            results["p2"] += 1
            winner = "Player 2 wins!"
            
        if verbose:
            print(f"Player 1: {p1_play}\tPlayer 2: {p2_play}\t{winner}")
            
        p1_prev_play = p1_play
        p2_prev_play = p2_play
    
    games_won = results['p2'] + results['p1']
    if games_won == 0:
        win_rate = 0
    else:
        win_rate = results['p1'] / games_won * 100
    
    print("Final results:", results)
    print(f"Player 1 win rate: {win_rate:.2f}%")
    
    return win_rate

def quincy(prev_play, counter=[0]):
    counter[0] += 1
    choices = ["R", "R", "P", "P", "S"]
    return choices[counter[0] % len(choices)]

def mrugesh(prev_opponent_play, opponent_history=[]):
    if not prev_opponent_play:
        prev_opponent_play = 'R'
    opponent_history.append(prev_opponent_play)
    
    last_ten = opponent_history[-10:]
    most_frequent = max(set(last_ten), key=last_ten.count) if last_ten else 'R'
    
    if most_frequent == 'R':
        return 'P'
    elif most_frequent == 'P':
        return 'S'
    else:
        return 'R'

def kris(prev_opponent_play):
    if prev_opponent_play == 'R':
        return 'P'
    elif prev_opponent_play == 'P':
        return 'S'
    else:
        return 'R'

def abbey(prev_opponent_play,
          opponent_history=[],
          play_order=[{"RR": 0, "RP": 0, "RS": 0,
                      "PR": 0, "PP": 0, "PS": 0,
                      "SR": 0, "SP": 0, "SS": 0}]):
    
    if not prev_opponent_play:
        prev_opponent_play = 'R'
    opponent_history.append(prev_opponent_play)
    
    last_two = "".join(opponent_history[-2:])
    if len(last_two) == 2:
        play_order[0][last_two] += 1
    
    potential_plays = [
        prev_opponent_play + "R",
        prev_opponent_play + "P",
        prev_opponent_play + "S",
    ]
    
    sub_order = {k: play_order[0][k] for k in potential_plays if k in play_order[0]}
    prediction = max(sub_order, key=sub_order.get)[-1:]
    
    return {'P': 'S', 'R': 'P', 'S': 'R'}[prediction]

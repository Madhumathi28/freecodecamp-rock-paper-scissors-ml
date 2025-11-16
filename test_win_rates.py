from RPS_game import play, quincy, abbey, kris, mrugesh
from RPS import player
import random

def test_bot(bot, bot_name, num_games=1000, required_win_rate=0.6):
    print(f"\nTesting against {bot_name}...")
    wins = 0
    
    for match in range(5):  # Run 5 matches to get a more reliable average
        # Reset the player's state for a new match
        player("", [])
        
        # Play the match
        win_rate = play(player, bot, num_games, verbose=False) / 100.0  # Convert percentage to decimal
        wins += 1 if win_rate >= required_win_rate else 0
        
        print(f"Match {match + 1}: {win_rate:.2%} win rate")
    
    # Calculate overall pass rate
    pass_rate = wins / 5
    print(f"{bot_name}: {'PASS' if pass_rate >= 0.6 else 'FAIL'} - {pass_rate:.0%} of matches achieved {required_win_rate:.0%}+ win rate")
    return pass_rate >= 0.6

if __name__ == "__main__":
    print("Testing player against all bots...")
    print("Each bot will be tested with 5 matches of 1000 games each.")
    print("To pass, the player must win at least 60% of games in at least 60% of the matches.\n")
    
    bots = [
        (quincy, "Quincy"),
        (abbey, "Abbey"),
        (kris, "Kris"),
        (mrugesh, "Mrugesh")
    ]
    
    results = []
    for bot, name in bots:
        results.append(test_bot(bot, name))
    
    # Final result
    if all(results):
        print("\nSUCCESS! Player achieved at least 60% win rate against all bots!")
    else:
        print("\nFAILED. Player did not achieve 60% win rate against all bots.")
        failed_bots = [name for (_, name), result in zip(bots, results) if not result]
        print(f"Consider improving the strategy for: {', '.join(failed_bots)}")

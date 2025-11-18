from RPS_game import play, mrugesh, abbey, quincy, kris
from RPS import player
from unittest import main

# Test against each bot
print("Testing against Quincy...")
play(player, quincy, 1000)

print("\nTesting against Abbey...")
play(player, abbey, 1000)

print("\nTesting against Kris...")
play(player, kris, 1000)

print("\nTesting against Mrugesh...")
play(player, mrugesh, 1000)

# Uncomment the line below to run the unit tests
 main(module='test_module', exit=False)

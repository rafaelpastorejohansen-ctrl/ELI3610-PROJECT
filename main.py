#Import necessary modules and classes
from blackjack import BlackJack
from robot_connection import RobotConnection
from card_reader import read_card
import position as ps

#Function to receive a card from the camera and return its rank
def receive_card_from_camera(robot):
    
    confirmation = robot.receive_message()
    if confirmation != "READY":
        raise ValueError(f"Expected READY, received {confirmation}")
    
    rank = read_card()
    
    if rank is None:
        robot.send_command("ERROR,NO_CARD")
        raise ValueError("No card detected!")
    
    robot.send_command("REGISTERED")
    
    confirmation = robot.receive_message()
    if confirmation != "DONE":
        raise ValueError(f"Expected DONE, received {confirmation}")

    return rank

#Take user input for the number of players, establish a connection with the robot, and initialize the blackjack game
number_of_players = int(input("\nHow many players are there: "))
robot = RobotConnection()
robot.connect()
print()

game = BlackJack(number_of_players)
game.game_state = "dealing"
"""
Deal two cards to each player and one card to the dealer, 
using the robot to pick up and place the cards, 
and receive the card ranks from the camera
"""
for i in range(number_of_players):
    pose = ps.card_position(i + 1, 1, 1)
    command = f"HIT,{pose}"
    robot.send_command(command)
    print(command)

    confirmation = robot.receive_message()
    if confirmation != "DONE":
        raise ValueError(f"Expected DONE, received {confirmation}")
        
    print()
    rank = receive_card_from_camera(robot)
    game.receive_card(rank, i)

command = "DEALER_HIT"
robot.send_command(command)

confirmation = robot.receive_message()
if confirmation != "DONE":
    raise ValueError(f"Expected DONE, received {confirmation}")

rank = receive_card_from_camera(robot)
game.receive_dealer_card(rank)

for i in range(number_of_players):
    pose = ps.card_position(i + 1, 1, 2)
    command = f"HIT,{pose}"
    robot.send_command(command)
    print(command)

    confirmation = robot.receive_message()
    if confirmation != "DONE":
        raise ValueError(f"Expected DONE, received {confirmation}")
        
    print()
    
    rank = receive_card_from_camera(robot)
    game.receive_card(rank, i)

print()

command = "DEALER_FACE_DOWN"
robot.send_command(command)

print("Dealer receives a face-down card")

confirmation = robot.receive_message()
if confirmation != "DONE":
    raise ValueError(f"Expected DONE, received {confirmation}")

#Set the game state to "playing" and enter the main game loop, where players can take actions (hit, stand, or split) until the game is finished
game.game_state = "playing"

while game.game_state == "playing":
    game.display_game()
    player = game.get_active_player()
    
    result = game.check_hand()
    
    if result == "BLACKJACK":
        print(f"{player.name} has BLACKJACK!")
        print()
        continue
    
    elif result == "21":
        print(f"{player.name}, Hand {player.active_hand + 1} reaches 21!")
        print()
        continue
    
    elif result == "BUST":
        print(f"{player.name}, Hand {player.active_hand + 1} busted!")
        print()
        continue
    
    print(player.name)
    print(f"Hand {player.active_hand + 1}")
    action = input("Hit(H), Stand(S) or Split(Sp): ").strip().upper()
    
    print()

    """
    Handles the player's action based on their input. 
    If the player chooses to hit, 
    the program sends a command to the robot to pick up and place a card, 
    receives the card rank from the camera,
    and checks the hand's status. 
    If the player chooses to stand, 
    it simply moves to the next hand or player. 
    If the player chooses to split, 
    it checks if the hand can be split, 
    sends a command to the robot to perform the split, 
    and handles any errors that may arise.
    """

    if action == "H":
        player_index = game.active_player
        hand_index = player.active_hand
        
        command = game.hit()
        robot.send_command(command)
        print(command)
        
        print()
        
        rank = receive_card_from_camera(robot)
        game.receive_card(rank, player_index, hand_index)
        
        result = game.check_hand()
        
        if result == "21":
            print(f"{player.name}, Hand {player.active_hand + 1} reaches 21!")
            print()
            continue
        
        elif result == "BUST":
            print(f"{player.name}, Hand {player.active_hand + 1} busted!")
            print()
            continue
    
    elif action == "S":
        game.stand()
    
    elif action == "SP":
        player_index = game.active_player
        hand_index = player.active_hand
        
        try:
            command = game.split()
            robot.send_command(command)
            print(command)
            
            confirmation = robot.receive_message()
            if confirmation != "DONE":
                raise ValueError(f"Expected DONE, received {confirmation}")
            
        except ValueError as error:
            print(error)
    
    else:
        print("Invalid action. Try again.")

"""
Once all players have completed their turns, 
the game state changes to "dealer".
The dealer reveals their face-down card, and the program receives the card rank from the camera.
The dealer then takes actions based on their hand value, 
hitting until they reach at least 17. 
The program checks if the dealer busts or stands, 
it then checks the results of each player's hands against the dealer's hand, 
displaying the outcome for each hand.
"""

if game.game_state == "dealer":
    command = "REVEAL,5,0,2"
    robot.send_command(command)
    
    rank = receive_card_from_camera(robot)
    game.receive_dealer_card(rank)
    
    game.display_game()
    
    while game.dealer_action() == "HIT":
        print("Dealer HIT!")
        
        print()
        card_count = len(game.dealer.cards) + 1
        command = "DEALER_HIT"
        robot.send_command(command)
        
        rank = receive_card_from_camera(robot)
        game.receive_dealer_card(rank)
        
        game.display_game()
    
    if game.dealer.is_bust():
        print("Dealer BUST")
        print()
    
    else:
        print("Dealer STAND")
        print()
    
    game.game_state = "finished"
    
    for player in game.players:
        print(player.name)
        
        for i, hand in enumerate(player.hands, start=1):
            result = game.check_winner(hand)
            print(f"Hand {i}: {result}")
        print()
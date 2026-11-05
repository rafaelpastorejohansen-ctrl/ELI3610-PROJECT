from blackjack import BlackJack
from robot_connection import RobotConnection
from card_reader import read_card

number_of_players = int(input("\nHow many players are there: "))
robot = RobotConnection()
robot.connect()
command = f"PLAYERS,{number_of_players}"
robot.send_command(command)
print()

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


game = BlackJack(number_of_players)
game.game_state = "dealing"

for i in range(number_of_players):
    message = robot.receive_message()
    message_type, rank = message.split(",")
    game.receive_card(rank, i)
    confirmation = robot.receive_message()
    if confirmation != "DONE":
        raise ValueError(f"Expected DONE, received {confirmation}")

message = robot.receive_message()
message_type, rank = message.split(",")
game.receive_dealer_card(rank)
confirmation = robot.receive_message()
if confirmation != "DONE":
    raise ValueError(f"Expected DONE, received {confirmation}")

for i in range(number_of_players):
    message = robot.receive_message()
    message_type, rank = message.split(",")
    game.receive_card(rank, i)
    confirmation = robot.receive_message()
    if confirmation != "DONE":
        raise ValueError(f"Expected DONE, received {confirmation}")

print()

print("Dealer recives a face-down card")

confirmation = robot.receive_message()
if confirmation != "DONE":
    raise ValueError(f"Expected DONE, received {confirmation}")

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
    
    if action == "H":
        player_index = game.active_player
        hand_index = player.active_hand
        
        command = game.hit()
        robot.send_command(command)
        print(command)
        
        print()
        
        message = robot.receive_message()
        message_type, rank = message.split(",")
        
        if message_type != "CARD":
            raise ValueError(f"Expected CARD, Recevied: {message}")
        
        game.receive_card(rank, player_index, hand_index)
        
        confirmation = robot.receive_message()
        if confirmation != "DONE":
            raise ValueError(f"Expected DONE, received {confirmation}")
        
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
            
            for i in range(2):
                current_hand_index = hand_index + i
                num_cards = player.hands[current_hand_index].num_cards + 1
                
                command = f"HIT,{player_index},{current_hand_index},{num_cards}"
                robot.send_command(command)
                message = robot.receive_message()
                message_type, rank = message.split(",")
                
                if message_type != "CARD":
                    raise ValueError(f"Expected CARD, Recevied: {message}")
                
                game.receive_card(rank, player_index, current_hand_index)
                
                confirmation = robot.receive_message()
                if confirmation != "DONE":
                    raise ValueError(f"Expected DONE, received {confirmation}")
        
        except ValueError as error:
            print(error)
    
    else:
        print("Invalid action. Try again.")
    
if game.game_state == "dealer":
    command = "REVEAL,5,0,2"
    robot.send_command(command)
    message = robot.receive_message()
    message_type, rank = message.split(",")
    if message_type != "CARD":
        raise ValueError(f"Expected CARD, received: {message}")
    game.receive_dealer_card(rank)
    confirmation = robot.receive_message()
    if confirmation != "DONE":
        raise ValueError(f"Expected DONE, received {confirmation}")
    
    game.display_game()
    
    while game.dealer_action() == "HIT":
        print("Dealer HIT!")
        
        print()
        card_count = len(game.dealer.cards) + 1
        command = f"HIT,5,0,{card_count}"
        robot.send_command(command)
        message = robot.receive_message()
        message_type, rank = message.split(",")
        if message_type != "CARD":
            raise ValueError(f"Expected CARD, received: {message}")
        try:
            game.receive_dealer_card(rank)
        except ValueError as error:
            raise error
        confirmation = robot.receive_message()
        if confirmation != "DONE":
            raise ValueError(f"Expected DONE, received {confirmation}")
            
        
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



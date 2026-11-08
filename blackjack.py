from cards import Card, Hand
from player import Player
import position as ps

#Class to represent a blackjack game
class BlackJack():
    def __init__(self, number_of_players):
        self.players = []
        
        for i in range(number_of_players):
            self.players.append(Player(f"Player {i+1}"))
        
        self.dealer = Hand()
        self.active_player = 0
        self.game_state = "waiting"
    
    #Method to get the active player of the game
    def get_active_player(self):
        return self.players[self.active_player]
    
    #Method to move to the next player of the game, if available
    def next_player(self):
        if self.active_player + 1 < len(self.players):
            self.active_player += 1
            return True
        
        self.game_state = "dealer"
        return False
    
    #Method to receive a card for a specific player and hand
    def receive_card(self, rank, player_index, hand_index=0):
        card = Card(rank)
        player = self.players[player_index]
        hand = player.hands[hand_index]
        hand.add_card(card)
        hand.num_cards += 1
    
    #Method to receive a card for the dealer
    def receive_dealer_card(self, rank):
        card = Card(rank)
        self.dealer.add_card(card)
    
    #Method to handle the stand action for the active player
    def stand(self):
        player = self.get_active_player()
        hand = player.get_active_hand()
        hand.status = "standing"
        
        if not player.next_hand():
            self.next_player()
    
    #Method to handle the hit action for the active player and return the position where the card should be placed
    def hit(self):
        player = self.get_active_player()
        pose = ps.card_position(self.active_player + 1, player.active_hand + 1, player.get_active_hand().num_cards + 1)
        return f"HIT,{pose}"
    
    #Method to check the status of the active player's hand and update the game state accordingly
    def check_hand(self):
        player = self.get_active_player()
        hand = player.get_active_hand()
        
        if hand.is_bust():
            hand.status = "bust"
            
            if not player.next_hand():
                self.next_player()
            
            return "BUST"
            
        elif hand.get_value() == 21:
            hand.status = "standing"
            
            if not player.next_hand():
                self.next_player()
            
            if hand.is_blackjack():
                return "BLACKJACK"
            
            return "21"
        
        return "PLAYING"
    
    #Method to handle the split action for the active player's hand and return the positions where the cards should be picked up and placed
    def split(self):
        player = self.get_active_player()
        hand = player.get_active_hand()
        pose_pickup = ps.card_position(self.active_player + 1, 1, 2)
        pose_place = ps.card_position(self.active_player + 1, 2, 1)
        
        if not hand.can_split():
            raise ValueError("This hand cannot be split")
        
        player.split_hand()
        
        
        return f"SPLIT,{pose_pickup},{pose_place}"
    
    #Method to handle the dealer's action based on the dealer's hand value
    def dealer_action(self):
        if self.dealer.get_value() < 17:
            return "HIT"
        return "STAND"
    
    #Method to check the winner of a specific hand against the dealer's hand and return the result
    def check_winner(self, hand):
        value = hand.get_value()
        dealer_value = self.dealer.get_value()
        
        if hand.is_blackjack() and self.dealer.is_blackjack():
            return "PUSH"
        
        elif hand.is_blackjack():
            return "BLACKJACK"
        
        elif hand.is_bust():
            return "LOSE"
        
        elif self.dealer.is_bust():
            return "WIN"
        
        elif value >  dealer_value:
            return "WIN"
        
        elif value < dealer_value:
            return "LOSE"
        
        else:
            return "PUSH"
    
    #Method to display the current state of the game, including the dealer's and players' hands and their values
    def display_game(self):
        print("\n=============BLACKJACK=============\n")
        
        if self.game_state in ["dealer", "finished"]:
            cards = [card.rank for card in self.dealer.cards]
            print(f"Dealer: {cards} ({self.dealer.get_value()})")
        else:
            if self.dealer.cards:
                print(f"Dealer: [{self.dealer.cards[0].rank}, ?]")
            else:
                print("Dealer: []")
        
        print()
        
        for player in self.players:
            print(player.name)
            for i, hand in enumerate(player.hands, start=1):
                cards = [card.rank for card in hand.cards]
                print(f"Hand {i}: {cards} ({hand.get_value()})")
        
        print()
        
        print("===================================\n")
from cards import Card, Hand
from player import Player
import position as ps

class BlackJack():
    def __init__(self, number_of_players):
        self.players = []
        
        for i in range(number_of_players):
            self.players.append(Player(f"Player {i+1}"))
        
        self.dealer = Hand()
        self.active_player = 0
        self.game_state = "waiting"
    
    def get_active_player(self):
        return self.players[self.active_player]
    
    def next_player(self):
        if self.active_player + 1 < len(self.players):
            self.active_player += 1
            return True
        
        self.game_state = "dealer"
        return False
    
    def receive_card(self, rank, player_index, hand_index=0):
        card = Card(rank)
        player = self.players[player_index]
        hand = player.hands[hand_index]
        hand.add_card(card)
        hand.num_cards += 1
    
    def receive_dealer_card(self, rank):
        card = Card(rank)
        self.dealer.add_card(card)
    
    def stand(self):
        player = self.get_active_player()
        hand = player.get_active_hand()
        hand.status = "standing"
        
        if not player.next_hand():
            self.next_player()
    
    def hit(self):
        player = self.get_active_player()
        pose = ps.card_position(self.active_player + 1, player.active_hand + 1, player.get_active_hand().num_cards + 1)
        return f"HIT,{pose}"
    
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
    
    def split(self):
        player = self.get_active_player()
        hand = player.get_active_hand()
        
        if not hand.can_split():
            raise ValueError("This hand cannot be split")
        
        player.split_hand()
        
        
        return f"SPLIT,{self.active_player},1,1"
        
    def dealer_action(self):
        if self.dealer.get_value() < 17:
            return "HIT"
        return "STAND"
    
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

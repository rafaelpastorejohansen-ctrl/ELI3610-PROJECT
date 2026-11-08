from cards import Hand

#Class to represent a player in a blackjack game
class Player():
    def __init__(self, name):
        self.name = name
        self.hands = [Hand()]
        self.active_hand = 0
        
    #Method to get the active hand of the player
    def get_active_hand(self):
        return self.hands[self.active_hand]
        
    #Mthod to split the active hand of the player into two hands
    def split_hand(self):
        current_hand = self.get_active_hand()
        
        if not current_hand.can_split():
            raise ValueError("This hand cannot be split")
        
        card1 = current_hand.cards[0]
        card2 = current_hand.cards[1]
        
        hand1 = Hand()
        hand1.num_cards = 1
        hand2 = Hand()
        hand2.num_cards = 1
        
        hand1.add_card(card1)
        hand2.add_card(card2)
        
        hand1.is_hand_split = True
        hand2.is_hand_split = True
        
        self.hands[self.active_hand:self.active_hand + 1] = [hand1, hand2]
    
    #Method to move to the next hand of the player, if available
    def next_hand(self):
        if self.active_hand + 1 < len(self.hands):
            self.active_hand += 1
            return True
        
        return False
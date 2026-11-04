class Card():
    def __init__(self, rank):
        self.rank = rank.upper()
        if self.rank in ["2", "3", "4", "5", "6", "7", "8", "9", "10"]:
            self.value = int(self.rank)
        
        elif self.rank in ["J", "Q", "K"]:
            self.value = 10
        
        elif self.rank == "A":
            self.value = 11
        
        else:
            raise ValueError("Invalid card rank")

class Hand():
    def __init__(self):
        self.cards = []
        self.status = "playing"
        self.is_hand_split = False
        self.num_cards = 0
    
    def add_card(self, card):
        self.cards.append(card)
    
    def get_value(self):
        total = 0
        aces = 0
    
        for card in self.cards:
            total += card.value
            
            if card.rank == "A":
                aces += 1
        
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1
        
        return total
    
    def is_bust(self):
        return self.get_value() > 21
    
    def is_blackjack(self):
        return len(self.cards) == 2 and self.get_value() == 21 and not self.is_hand_split
    
    def can_split(self):
        return(
            len(self.cards) == 2 
            and self.cards[0].value == self.cards[1].value
        )
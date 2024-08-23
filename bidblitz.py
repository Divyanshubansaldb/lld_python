"""
features:
1. lowest bid,
2. declare the winner,
3. view of winners of past events
4. special features for flipkart plus members

requirements:
1. add members
2. add event (unique id)
3. members registering for the event and only those can play
4. submits bids at a go and 5bids max (all unique bids, greater than 0)
6. max of 5bids amount should be there in wallet
7. admin declares the winner
8. winner delaration process -> member with the lowest bid and first one if not unique
9. list of past events, ordered

"""
from abc import ABC
from datetime import datetime

class User:
    def __init__(self, name):
        self.name = name

class Coordinators(User):
    def __init__(self, name, is_admin=False):
        self.is_admin = is_admin
        super().__init__(name)

class Player(User):
    def __init__(self, name, coins):
        if coins <= 0:
            raise Exception("Coins should be >0")
        self.coins = coins
        super().__init__(name)

# singleton class
class PlayerController:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(PlayerController, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.players = []

    def add(self, name, coins):
        player = Player(name, coins)
        self.players.append(player)
        print("Member added to the game")

    def get(self, id):
        if id >= len(self.players): return None
        return self.players[id]


class Event:
    MAX_ALLOWED_BIDS = 5

    def __init__(self, name, prize, date):
        self.name = name
        self.prize = prize
        self.date = datetime.strptime(date, "%y-%m-%d").date()
        self.participants = []
        self.bids = []

class WinningStrategy:
    def __init__(self, bids) -> None:
        self.bids = bids

    def compute(self):
        pass

# singleton class
class EventController:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(EventController, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, player_controller: PlayerController, Strategy: WinningStrategy):
        self.events = []
        self.Strategy = Strategy
        self.player_controller = player_controller
    
    def add(self, name, prize, date):
        new_event = Event(name, prize, date)
        for event in self.events:
            if event.date == new_event.date:
                del new_event
                raise Exception("Two events cannot be posted on same date.")
        self.events.append(new_event)
        print("New event added to the game")
    
    def get(self, id):
        return self.events[id]
    
    def register_player(self, player_id, event_id):
        player = self.player_controller.get(id=player_id)
        if player is None:
            raise Exception(f"No player exist with this player_id {player_id}")
        event = self.events[event_id]
        if player_id in event.participants:
            print(f"Player already registered for the event_id {event_id}")
            return
        event.participants.append(player_id)

    def submit_bid(self, player_id, event_id, *bids):
        if len(bids) > Event.MAX_ALLOWED_BIDS:
            raise Exception(f"Max {Event.MAX_ALLOWED_BIDS} can be posted!!")
        if min(bids) < 0:
            raise Exception("Bids should be >0")
        if len(set(bids)) != len(bids):
            raise Exception("Bids should be unique!!")
        event = self.events[event_id]
        if player_id not in event.participants:
            raise Exception("Player didn't register for the event!!")
        for bid in event.bids: 
            if bid[0] == player_id:
                raise Exception("Player already registered the bid!!")
        player = self.player_controller.get(id = player_id)
        if max(bids) > player.coins:
            raise Exception("Player does not have necessary coins!!")
        player.coins -= max(bids)
        event.bids.append((player_id, bids))
        print("bids added successfully")

    def get_winner(self, event_id):
        event = self.events[event_id]
        if len(event.participants) == 0:
            print("No one participated in the event")
            return
        winner_idx, min_bid = self.Strategy(event.bids).compute()
        player = self.player_controller.get(id = winner_idx)
        print(f"{player.name} won the game with {min_bid} and gets {event.prize}")


class MinBetStrategy(WinningStrategy):
    def __init__(self, bids) -> None:
        super().__init__(bids)

    def compute(self):
        winner, min_bid = None, None
        for bid in self.bids:
            for amount in bid[1]:
                if min_bid is None or amount < min_bid:
                    winner = bid[0]
                    min_bid = amount
        return winner, min_bid
    

if __name__ == "__main__":
    player_controller = PlayerController()
    event_controller = EventController(player_controller, MinBetStrategy)
    player_controller.add("Aman", 5000)
    player_controller.add("Divyanshu", 7000)
    player_controller.add("Keshav", 7000)

    event_controller.add("bbd", "iphone 14", "23-06-06")
    event_controller.add("bbd 24", "iphone 15", "23-06-06")
    event_controller.register_player(0, 0)
    event_controller.register_player(1, 0)
    event_controller.submit_bid(0, 0, 100, 200, 400, 500)
    event_controller.submit_bid(1, 0, 100, 200, 300, 400, 500)
    # event_controller.submit_bid(2, 0, 100, 200, 300, 400, 500)
    
    event_controller.get_winner(0)

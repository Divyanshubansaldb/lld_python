"""
Q. https://leetcode.com/discuss/interview-experience/3228851/Flipkart-SDE-2-Feb-2023

features:
1. resturants --> menu --> items, prices
2. resturant ratings
3. max orders at a time --> no more orders allowed 
4. order (accepted) --> completed  --> free up resturant capacity 
5. can't cancel an accepted order
6. order auto assigned based on a selection stretegy eg. Assign by lowest cost or best rating
7. all the items in order should be fulfilled

requirements:
1. onboard a new restaurant with menu
2. customer order (items, quantities, strategy)
3. restaurant update menu option but can't delete an item

expectations:
1. Make sure that you have working and demoable & functionally correct code. 
2. Use proper abstractions, separation of concerns, proper entity modeling 
3. Use appropriate design patterns wherever required.
4. The code should be modular, extensible, readable and unit-testable. 
5. Proper exception handling is required. 
6. Restaurant selection strategy must be pluggable 
7. Concurrency handling (BONUS / Good to have) 
8. Unit test cases (Bonus/ Good to have)

Assumptions:
1. Unique restaurant name
2. No need to create the user.
"""
from enum import Enum
from typing import Dict, List, Union

class Item:
    def __init__(self, name, price=None, quantity=None) -> None:
        self.name = name
        self.price = price
        self.quantity = quantity


class Resturant: 
    menu: Dict[str, Item]

    def __init__(self, name, rating, max_orders) -> None:
        self.name = name
        self.rating = rating
        self.max_orders = max_orders
        self.menu = {}

    def get_item(self, item_name):
        return self.menu.get(item_name)

    def update_item(self, item_name: str, new_price: int = None, add_quantity: int = None):
        item = self.get_item(item_name=item_name)
        if item == None: raise Exception("No item with this name exist in the resturant!")
        if new_price is not None:
            item.price = new_price
            print(f"price updated for the item {item_name}")
        if add_quantity is not None:
            item.quantity += add_quantity
            print(f"quantity updated for the item {item_name}")

    def add_item(self, item_name: str, price: int, quantity: int):
        self.menu[item_name] = Item(item_name, price, quantity)
        print("Item added to the resturant")
    

class Order:
    class STATUS(Enum):
        RECEIVED = 0
        ACCEPTED = 1
        COMPLTED = 2
        CANCELLED = 3

    user_name: str
    items: Dict[str, Item]
    resturant: Resturant

    def __init__(self, user_name:str, items_quan: list[(str, int)]) -> None:
        for item_name, quan in items_quan:
            self.items[item_name] = Item(name=item_name, quantity=quan)
        self.status = self.STATUS.RECEIVED
        self.user_name = user_name

    def accept_order(self, item_price: list[(str, int)], resturant: Resturant):
        for item_name, price in item_price:
            self.items[item_name].price = price
        self.status = self.STATUS.ACCEPTED
        self.resturant = resturant


class ResturantController:
    _instance = None
    resturants = list[Resturant]

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ResturantController, cls).__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        self.resturants = []

    def get(self, name) -> Resturant:
        for obj in self.resturants:
            if obj.name == name:
                return obj
        return None

    def add(self, name, rating, max_orders):
        self.resturants.append(
            Resturant(name, rating, max_orders)
        )


class ResturantSelectionStretegy:
    def __init__(self, order: Order, resturant_controller: ResturantController) -> None:
        self.order = order
        self.resturant_controller = resturant_controller

    def compute_cost(self, resturant:Resturant) -> int:
        price = 0
        for item_name, item in self.order.items.items():
            price += item.quantity * resturant.get_item(item_name).price
        return price

    def select_resturant(self):
        pass


class ResturantOrderManager:
    _instance = None
    resturant_controller: ResturantController
    resturant_orders_list = Dict[str, list[Order]]

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ResturantOrderManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, controller: ResturantController) -> None:
        self.resturant_controller = controller
    
    @classmethod
    def validate(cls, resturant: Resturant, order: Order):
        for item_name, item in order.items.items():
            if resturant.get_item(item_name).quantity >= item.quantity:
                return False
        if resturant.max_orders <= len(cls.resturant_orders_list[resturant.name]):
            return False
        return True

    def process_order(self, order: Order, resturant: Resturant):
        item_price = []
        for item_name, item in order.items.items():
            resturant.update_item(item_name=item_name, add_quantity=-1*item.quantity)
            item_price.append((item_name, item.price))
        order.accept_order(item_price=item_price, resturant=resturant)
        if self.resturant_orders_list.get(resturant.name) is None:
            self.resturant_orders_list[resturant.name] = []
        self.resturant_orders_list[resturant.name].append(order)

    def new_order(self, user_name: str, food_quan: list[(str, int)], strategy: ResturantSelectionStretegy):
        order = Order(user_name=user_name, items_quan=food_quan)
        resturant = strategy(order).select_resturant()
        if resturant is None:
            print("No resturant is available to serve the order!!")
        self.process_order(order, resturant)


class LowestCostSelectionStrategy(ResturantSelectionStretegy):
    def __init__(self, order: Order, resturant_controller: ResturantController) -> None:
        super().__init__(order, resturant_controller)

    def select_resturant(self):
        min_price = 0
        min_resturant = None
        for resturant in self.resturant_controller.resturants:
            if ResturantOrderManager.validate(resturant=resturant, order=self.order):
                price = self.compute_cost(resturant)
                if price < min_price:
                    min_price, min_resturant = price, resturant
        
        return min_resturant


if __name__ == "__main__":
    rc = ResturantController()
    rc.add(name="R1", rating=4.5, max_orders=5)
    rc.get("R1").add_item(item_name="veg biryani", price=100, quantity=30)
    rc.get("R1").add_item(item_name="Paneer Butter Masala", price=150, quantity=30)
    
    rc.add(name="R2", rating=4, max_orders=5)
    rc.get("R2").add_item(item_name="Paneer Butter Masala", price=175, quantity=30)
    rc.get("R2").add_item(item_name="Idli", price=10, quantity=30)
    rc.get("R2").add_item(item_name="Dosa", price=50, quantity=30)
    rc.get("R2").add_item(item_name="veg biryani", price=80, quantity=30)

    rc.add(name="R3", rating=4.9, max_orders=1)
    rc.get("R3").add_item(item_name="Gobi Manchurian", price=150, quantity=30)
    rc.get("R3").add_item(item_name="Idli", price=15, quantity=30)
    rc.get("R3").add_item(item_name="Paneer Butter Masala", price=175, quantity=30)
    rc.get("R3").add_item(item_name="Dosa", price=30, quantity=30)

    rc.get("R1").add_item(item_name="Chicken65", price=250, quantity=30)
    rc.get("R2").update_item(item_name="Paneer Butter Masala", new_price=150)

    rom = ResturantOrderManager(controller=rc)
    rom.new_order(user_name="Ashwin", food_quan=[("Idli", 3), ("Dosa", 1)], strategy=LowestCostSelectionStrategy)

    rom.new_order(user_name="Harish", food_quan=[("Idli", 3), ("Dosa", 1)], strategy=LowestCostSelectionStrategy)



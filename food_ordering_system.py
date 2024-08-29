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
import enum
from typing import Dict, List, Union

class Item:
    def __init__(self, name, price) -> None:
        self.name = name
        self.price = price


class Resturant: 
    menu: list[Item]
    available_quantity: Dict[Item, int]

    def __init__(self, name, rating, max_orders) -> None:
        self.name = name
        self.rating = rating
        self.max_orders = max_orders
        self.menu = []

    def get_item(self, item_name):
        for obj in self.items:
            if obj.name == item_name:
                return obj

        return None

    def item_price(self, item_name):
        item = self.get_item(item_name)
        return item.price if item else None
    
    def item_quantity(self, item_name):
        item = self.get_item(item_name)
        return self.available_quantity.get(item) if item else None


class Order:
    class STATUS(enum):
        RECEIVED = 0
        ACCEPTED = 1
        COMPLTED = 2
        CANCELLED = 3

    items_quan: list[(Item, int)]
    resturant: Resturant

    def __init__(self, items_quan: list[(Item, int)]) -> None:    
        self.items_quan = items_quan
        self.status = self.STATUS.RECEIVED


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
    
    def update_item(self, name: str, item_name: str, new_price: int = None, new_quantity: int = None):
        resturant = self.get(name=name)
        if resturant == None: raise Exception("Resturant with name does not exist")
        item = resturant.get_item(item_name=item_name)
        if item == None: raise Exception("No item with this name exist in the resturant!")
        if new_price is not None:
            item.price = new_price
            print(f"price updated for the item {item_name}")
        if new_quantity is not None:
            resturant.available_quantity[item] = new_quantity
            print(f"quantity updated for the item {item_name}")

    def add_item(self, name: str, item_name: str, price: int):
        resturant = self.get(name = name)
        if resturant == None: raise Exception("Resturant with name does not exist")
        item = Item(name, price)
        resturant.append(item)
        print("Item added to the resturant")
    

class ResturantSelectionStretegy:
    def __init__(self, order: Order, resturant_controller: ResturantController) -> None:
        self.order = order
        self.resturant_controller = resturant_controller

    def validate(self, resturant:Resturant):
        for item in self.order.items_quan:
            item_name, quan = item
            if resturant.item_quantity(item_name) >= quan:
                return False
        return True

    def compute_cost(self, resturant:Resturant) -> int:
        price = 0
        for item in self.order.items_quan:
            item_name, quan = item
            price += quan * resturant.item_price(item_name)
        return price

    def select_resturant(self):
        pass


class ResturantOrderManager:
    _instance = None
    resturant_controller: ResturantController
    orders_list = Dict[Resturant, list[Order]]

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ResturantOrderManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, controller: ResturantController) -> None:
        self.resturant_controller = controller
    
    def new_order(self, items_quan: list[(Item, int)], strategy: ResturantSelectionStretegy):
        order = Order(items_quan)
        order.resturant = strategy(order).select_resturant()


class LowestCostSelectionStrategy(ResturantSelectionStretegy):
    def __init__(self, order: Order, resturant_controller: ResturantController) -> None:
        super().__init__(order, resturant_controller)

    def select_resturant(self):
        min_price = 0
        min_resturant = None
        for resturant in self.resturant_controller.resturants:
            if self.validate(resturant):
                price = self.compute_cost(resturant)
                if price < min_price:
                    min_price, min_resturant = price, resturant
        
        return min_resturant


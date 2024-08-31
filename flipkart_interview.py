"""
q. fliptrip
make a flight booking searching app
city a --> city b
1. Every city has three letters and is unique
2. Airline names can be of any length and it is unique
3. total cost of trip is positive

to create functionality for:
1. minimum no. of hops (if the hops are same then give the minimum cost output)
2. cheapesh flight (if the cost is same for two flights, then prefer the minimum hops output)
3. There should be a filter on meal or excess bagage or it can be any other parameters (this should be extensible for any other params in future)
4. filter can be present on the sum of total duration of flight (ascending or descending)

to remember:
- Solving for the current day
- filter should be a (and) operation

input:
register flight --> JetAir --> DEL --> BLR --> 500
search flight --> DEL --> NYC

Expectations:
1. extensible and modular code
"""
from typing import List, Dict, Tuple, Set
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import heapq

class City:
    def __init__(self, code: str):
        if len(code) != 3:
            raise ValueError("City code must be exactly 3 letters")
        self.code = code.upper()

    def __eq__(self, other):
        return isinstance(other, City) and self.code == other.code

    def __hash__(self):
        return hash(self.code)

    def __str__(self):
        return self.code
    
    def __gt__(self, other):
        if not isinstance(other, City):
            return NotImplemented
        return self.code > other.code

class Airline:
    def __init__(self, name: str, meal_provided: bool = False, excess_baggage_allowed: bool = False):
        self.name = name
        self.meal_provided = meal_provided
        self.excess_baggage_allowed = excess_baggage_allowed

    def __eq__(self, other):
        return isinstance(other, Airline) and self.name == other.name

class Flight:
    def __init__(self, airline: Airline, origin: City, destination: City, cost: float, duration: timedelta):
        if cost <= 0:
            raise ValueError("Cost must be positive")
        self.airline = airline
        self.origin = origin
        self.destination = destination
        self.cost = cost
        self.duration = duration

class FlightFilter(ABC):
    def __init__(self, enable: bool) -> None:
        self.enable = enable

    @abstractmethod
    def apply(self, flight: Flight) -> bool:
        pass

class MealFilter(FlightFilter):
    def __init__(self, enable: bool) -> None:
        super().__init__(enable)

    def apply(self, flight: Flight) -> bool:
        if self.enable is False:
            return True
        return flight.airline.meal_provided

class ExcessBaggageFilter(FlightFilter):
    def __init__(self, enable: bool) -> None:
        super().__init__(enable)

    def apply(self, flight: Flight) -> bool:
        if self.enable is False:
            return True
        return flight.airline.excess_baggage_allowed

class AirlineDatabase:
    def __init__(self):
        self.airlines: Dict[str, Airline] = {}

    def get(self, airline_name: str):
        return self.airlines[airline_name]

    def add(self, airline: Airline):
        self.airlines[airline.name] = airline

class FlightDatabase:
    def __init__(self):
        self.flights: List[Flight] = []

    def add(self, flight: Flight):
        self.flights.append(flight)

    def get_all_cities(self) -> Set[City]:
        return set(flight.origin for flight in self.flights) | set(flight.destination for flight in self.flights)

    def get_outgoing_flights(self, city: City, filters: List[FlightFilter] = None) -> List[Flight]:
        outgoing_flights = [flight for flight in self.flights if flight.origin == city]
        if filters:
            return [flight for flight in outgoing_flights if all(filter.apply(flight) for filter in filters)]
        return outgoing_flights

class FlightPath:
    def __init__(self, flights: List[Flight]):
        self.flights = flights

    @property
    def total_cost(self) -> float:
        return sum(flight.cost for flight in self.flights)

    @property
    def total_duration(self) -> timedelta:
        return sum((flight.duration for flight in self.flights), timedelta())

    @property
    def hops(self) -> int:
        return len(self.flights)

    def __str__(self):
        return " -> ".join(str(flight.origin) for flight in self.flights) + f" -> {self.flights[-1].destination}"

class FlightSearchEngine:
    def __init__(self, flight_database: FlightDatabase):
        self.database = flight_database

    def search(self, origin: City, destination: City, filters: List[FlightFilter] = None) -> List[FlightPath]:
        min_cost_path = self._dijkstra(origin, destination, lambda f: f.cost, filters)
        min_hops_path = self._dijkstra(origin, destination, lambda f: 1, filters)  # Each flight counts as 1 hop
        
        return [min_cost_path, min_hops_path]

    def _dijkstra(self, origin: City, destination: City, weight_func, filters: List[FlightFilter] = None):
        cities = self.database.get_all_cities()
        distances = {city: float('inf') for city in cities}
        distances[origin] = 0
        predecessors = {city: None for city in cities}
        pq = [(0, origin)]

        while pq:
            current_distance, current_city = heapq.heappop(pq)

            if current_city == destination:
                break

            if current_distance > distances[current_city]:
                continue

            for flight in self.database.get_outgoing_flights(current_city, filters):
                distance = current_distance + weight_func(flight)
                if distance < distances[flight.destination]:
                    distances[flight.destination] = distance
                    predecessors[flight.destination] = flight
                    heapq.heappush(pq, (distance, flight.destination))

        if predecessors[destination] is None:
            return None

        path = []
        current_city = destination
        while current_city != origin:
            flight = predecessors[current_city]
            path.append(flight)
            current_city = flight.origin

        return FlightPath(list(reversed(path)))

    def search_all_paths(self, origin: City, destination: City, filters: List[FlightFilter] = None, 
                         max_hops: int = 3, sort_ascending: bool = True) -> List[FlightPath]:
        def dfs(current: City, path: List[Flight], visited: Set[City]):
            if len(path) > max_hops:
                return []
            
            if current == destination:
                return [FlightPath(path)]

            paths = []
            for flight in self.database.get_outgoing_flights(current, filters):
                if flight.destination not in visited:
                    new_visited = visited | {flight.destination}
                    paths.extend(dfs(flight.destination, path + [flight], new_visited))
            
            return paths

        all_paths = dfs(origin, [], {origin})
        return sorted(all_paths, key=lambda p: p.total_duration, reverse=not sort_ascending)

class FlipTripApp:
    def __init__(self):
        self.flight_database = FlightDatabase()
        self.airline_database = AirlineDatabase()
        self.search_engine = FlightSearchEngine(flight_database=self.flight_database)

    def register_airline(self, name: str, meal_provided: bool = False, excess_baggage_allowed: bool = False):
        airline = Airline(name, meal_provided, excess_baggage_allowed)
        self.airline_database.add(airline)

    def register_flight(self, airline_name: str, origin: str, destination: str, cost: float, duration: int):
        airline = self.airline_database.get(airline_name)
        if not airline:
            raise ValueError(f"Airline {airline_name} not found. Please register the airline first.")
        origin_city = City(origin)
        destination_city = City(destination)
        flight = Flight(airline, origin_city, destination_city, cost, timedelta(minutes=duration))
        self.flight_database.add(flight)

    def search_flight(self, origin: str, destination: str, filters: List[FlightFilter] = None):
        origin_city = City(origin)
        destination_city = City(destination)
        min_cost, min_hops = self.search_engine.search(origin_city, destination_city, filters)

        if not min_cost and not min_hops:
            print("No flights found.")
            return

        print(f"Minimum cost path: {min_cost}, Cost: {min_cost.total_cost}, Hops: {min_cost.hops}")
        print(f"Minimum hops path: {min_hops}, Cost: {min_hops.total_cost}, Hops: {min_hops.hops}")

    def list_all_flights(self, origin: str, destination: str, filters: List[FlightFilter] = None, 
                           max_hops: int = 3, sort_ascending: bool = True):
        origin_city = City(origin)
        destination_city = City(destination)
        paths = self.search_engine.search_all_paths(origin_city, destination_city, filters, max_hops, sort_ascending)

        if not paths:
            print("No flights found.")
            return

        print(f"All possible paths from {origin} to {destination} (sorted by {'ascending' if sort_ascending else 'descending'} duration):")
        for path in paths:
            print(f"{path}, Duration: {path.total_duration}, Cost: {path.total_cost}, Hops: {path.hops}")


if __name__ == "__main__":
    app = FlipTripApp()

    # Register airlines
    app.register_airline("JetAir", meal_provided=True, excess_baggage_allowed=True)
    app.register_airline("AirIndia", meal_provided=True, excess_baggage_allowed=False)
    app.register_airline("Emirates", meal_provided=True, excess_baggage_allowed=True)
    app.register_airline("Lufthansa", meal_provided=True, excess_baggage_allowed=True)

    # Register flights
    app.register_flight("JetAir", "DEL", "BLR", 500, 120)
    app.register_flight("AirIndia", "BLR", "NYC", 600, 900)
    app.register_flight("Emirates", "DEL", "NYC", 1200, 960)
    app.register_flight("Lufthansa", "DEL", "FRA", 800, 480)
    app.register_flight("Lufthansa", "FRA", "NYC", 600, 540)

    # Search flights (minimum cost and minimum hops)
    print("Search for minimum cost and minimum hops:")
    app.search_flight("DEL", "NYC", [MealFilter(True), ExcessBaggageFilter(False)])

    print("\nSearch for all possible paths (sorted by duration):")
    app.list_all_flights("DEL", "NYC", [MealFilter(True), ExcessBaggageFilter(True)], max_hops=3, sort_ascending=True)
    
    print("\nSearch for all possible paths (sorted by duration):")
    app.list_all_flights("DEL", "NYC", [MealFilter(True), ExcessBaggageFilter(False)], max_hops=3, sort_ascending=True)

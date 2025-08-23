from delivery_driver import DeliveryDriver
from dart_node import DartNode

class Truck():
    def __init__(self, id, driver: DeliveryDriver=None, package_capacity: int=16, average_speed: int=18, mileage: int=0):
        self.id = id
        self.package_capacity = package_capacity
        self.average_speed = average_speed
        self.driver = driver
        
        self.packages = []

        self.current_address = "HUB"
        self.minimum_spanning_tree = None
        self.last_address_departure_time = -1
        self.visited_address_log = []
    
    # should be called whenever the truck has reached a node; the edge "points" to the next node not yet in the list
    def update_status(self, address:DartNode, time:int = 0):
        self.visited_addresses_log.append((time, address))
    
    # assumes that it's the same day
    def get_current_mileage(self, current_time: int):
        mileage = 0
        for i in range(len(self.visited_address_log) - 2):
            time, node = self.visited_address_log[i]
        
        # self.mileage + (self.average_speed) * (current_time - self.last_node_departure_time)
        return mileage
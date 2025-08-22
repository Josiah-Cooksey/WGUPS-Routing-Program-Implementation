from delivery_driver import DeliveryDriver

class Truck():
    def __init__(self, id_number, driver: DeliveryDriver=None, package_capacity: int=16, average_speed: int=18, mileage: int=0):
        self.id_number = id_number
        self.package_capacity = package_capacity
        self.average_speed = average_speed
        self.mileage = mileage
        self.driver = driver
        self.at_hub = True
        self.minimum_spanning_tree = None
        self.last_node_departure_time = -1
        self.packages = []
    
    # assumes that it's the same day
    def get_current_mileage(self, current_time: int):
        return self.mileage + (self.average_speed) * (current_time - self.last_node_departure_time)
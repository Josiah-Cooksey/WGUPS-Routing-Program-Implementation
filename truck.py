from typing import List
from delivery_driver import DeliveryDriver
from dart_node import DartNode
from hash_table import HashTable
from mail_item import MailItem
from delivery_status import DeliveryStatus

class Truck():
    def __init__(self, id, driver: DeliveryDriver=None, package_capacity: int=16, average_speed: int=18, mileage: int=0):
        self.id = id
        self.package_capacity = package_capacity
        self.average_speed_mph = average_speed
        self.average_speed_mpm = self.average_speed_mph / 60
        self.driver = driver
        
        self.packages = HashTable()

        self.route_completion_timestamp_minutes = 0
        self.route = None
        self.route_total_distance = 0
        self.current_node_index = 0
        self.last_address_departure_time = -1
        self.visited_address_log: List[DartNode] = []

        self.start_time = None

    # should be called whenever the truck has reached a node; the edge "points" to the next node not yet in the list
    def update_status(self, address:DartNode, time:int = 0):
        self.visited_address_log.append((time, address))
    
    # assumes that it's the same day
    def get_current_mileage(self, current_time: int):
        mileage = 0
        for i in range(len(self.visited_address_log)):
            log_time, log_node = self.visited_address_log[i]
            if current_time > log_time:
                # because the log is in chronological order, we only need to sum distances from nodes logged at a time <= the current time
                mileage += log_node.distance
            else:
                # plus the distance of the final node divided by the distance we've theoretically travelled since we've been there
                # (the end nodes of a route are always at the HUB and always have a distance of 0,
                # so this should fix mileage accrual whilst trucks wait at the HUB for packages to become eligible for loading)
                time_on_that_node = (log_time - current_time)
                if self.average_speed_mpm != 0 and time_on_that_node != 0:
                    mileage += (log_node.distance) / (self.average_speed_mpm * time_on_that_node)
                break
        
        return mileage
    
    # only needs to be called once per route
    # the truck deletes its route (by setting it to None) after delivering all packages 
    def drive_route(self, start_time: int):
        self.start_time = start_time
        
        total_route_distance = 0
        time_when_at_next = start_time
        for node in self.route:
            self.update_status(node, time_when_at_next)

            # TODO: MARK PACKAGES at node.address AS DELIVERED AND REMOVE THEM FROM self.packages
            packages_for_this_address = self.packages.lookup_all(node.label)
            for package in packages_for_this_address:
                self.deliver(package, time_when_at_next)
            
            total_route_distance += node.distance
            time_when_at_next += (node.distance / self.average_speed_mpm)

        self.route = None
        self.route_completion_timestamp_minutes = self.start_time + (total_route_distance / self.average_speed_mpm)

    def calculate_route_round_trip_distance(self):
        for node in self.route:
            self.route_total_distance += node.distance


    def unload(self, package_or_packages: MailItem | List[MailItem]):
        if isinstance(package_or_packages, MailItem):
            self.packages.remove_by_item(package_or_packages.address, package_or_packages)

        elif isinstance(package_or_packages, List):
            for package in package_or_packages:
                self.packages.remove_by_item(package.address, package)
    

    def load(self, package_or_packages: MailItem | List[MailItem]):
        if isinstance(package_or_packages, MailItem):
            self.packages.insert(package_or_packages.address, package_or_packages)

        elif isinstance(package_or_packages, List):
            for package in package_or_packages:
                self.packages.insert(package.address, package)
    

    def deliver(self, package_or_packages: MailItem | List[MailItem], delivery_time):
        if isinstance(package_or_packages, MailItem):
            package_or_packages.update_status(DeliveryStatus.DELIVERED, delivery_time)
            self.unload(package_or_packages)

        elif isinstance(package_or_packages, List):
            for package in package_or_packages:
                package.update_status(DeliveryStatus.DELIVERED, delivery_time)
                self.unload(package)
    
    def can_be_loaded(self, time):
        return self.route == None and len(self.packages) < self.package_capacity and time >= self.route_completion_timestamp_minutes
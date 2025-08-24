from typing import List
from delivery_driver import DeliveryDriver
from dart_node import DartNode
from hash_table import HashTable
from mail_item import MailItem
from delivery_status import DeliveryStatus

class Truck():
    def __init__(self, id, driver: DeliveryDriver=None, package_capacity: int=16, average_speed: int=18):
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

        self._last_reported_mileage = 0

    # should be called whenever the truck has reached a node; the edge "points" to the next node not yet in the list
    def update_status(self, address:DartNode, time:int = 0):
        self.visited_address_log.append((time, address))
    
    # assumes that it's the same day
    def get_current_mileage(self, current_time: int):
        mileage = 0
        prior_node_distance = 0
        prior_log_time = 0
        for i in range(len(self.visited_address_log)):
            log_time, log_node = self.visited_address_log[i]
            if current_time >= log_time:
                # because the log is in chronological order, we need to sum distances from nodes logged at a time <= the current time
                mileage += prior_node_distance
            else:
                # plus the distance that we've theoretically travelled since we've been there
                time_on_last_node = (current_time - prior_log_time)
                estimated_distance = (self.average_speed_mpm * time_on_last_node)
                # sometimes when the trucks are waiting to be loaded, the time they wait * their average speed is a longer distance
                # than what it took to reach where they are
                # this should fix mileage accrual whilst trucks wait at the HUB for packages to become eligible for loading
                if estimated_distance < prior_node_distance and time_on_last_node > 0:
                    mileage += estimated_distance
                break
            prior_node_distance = log_node.distance
            prior_log_time = log_time
        
        self._last_reported_mileage = mileage
        return mileage
    
    # only needs to be called once per route
    # the truck deletes its route (by setting it to None) after delivering all packages 
    def drive_route(self, start_time: int):
        total_route_distance = 0
        time_when_at_next = start_time
        for node in self.route:
            self.update_status(node, time_when_at_next)

            packages_for_this_address = self.packages.lookup_all(node.label)
            for package in packages_for_this_address:
                self.deliver(package, time_when_at_next)
            
            total_route_distance += node.distance
            time_when_at_next += (node.distance / self.average_speed_mpm)

        self.route = None
        self.route_completion_timestamp_minutes = start_time + (total_route_distance / self.average_speed_mpm)

    def calculate_route_round_trip_distance(self):
        for node in self.route:
            self.route_total_distance += node.distance


    def unload(self, package_or_packages: MailItem | List[MailItem]):
        if isinstance(package_or_packages, MailItem):
            self.packages.remove_by_item(package_or_packages.address, package_or_packages)
            return

        for package in package_or_packages:
            self.packages.remove_by_item(package.address, package)
    

    def load(self, package_or_packages: MailItem | List[MailItem]):
        if isinstance(package_or_packages, MailItem):
            self.packages.insert(package_or_packages.address, package_or_packages)
            return

        for package in package_or_packages:
            self.packages.insert(package.address, package)
    

    def deliver(self, package_or_packages: MailItem | List[MailItem], delivery_time):
        if isinstance(package_or_packages, MailItem):
            package_or_packages.update_status(DeliveryStatus.DELIVERED, delivery_time)
            self.unload(package_or_packages)
            return

        for package in package_or_packages:
            package.update_status(DeliveryStatus.DELIVERED, delivery_time)
            self.unload(package)
    
    def can_be_loaded(self, time):
        return self.route == None and len(self.packages) < self.package_capacity and time >= self.route_completion_timestamp_minutes
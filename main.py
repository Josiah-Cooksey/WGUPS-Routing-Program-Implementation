# Developed by Josiah Cooksey; WGU Student ID: 011030459
import csv
from enum import Enum
import os
import random
import re
from delivery_driver import DeliveryDriver
from delivery_status import DeliveryStatus
from distance_node import DistanceNode
from hash_table import HashTable
from mail_item import MailItem
from truck import Truck
from utils import *


# in an ideal world this data would already be in a database that we could query because spreadsheets are unsustainable
def parse_package_data(filename):
    required_ID_table = HashTable()
    my_table = HashTable()

    if not file_exists(filename):
        print(f"File: \"{filename}\" does not exist in the current working directory: {os.getcwd()}")
    
    try:
        with open(filename, 'r') as data:
            reader = csv.reader(data)
            column_titles = next(reader)
            
            while(True):
                # Package ID	Address	City 	State	Zip	Delivery Deadline	Weight KILO	page 1 of 1PageSpecial Notes 
                row = next(reader)
                item = MailItem(row[0].strip(), simplify_address(row[1].strip()), row[2].strip(), row[3].strip(), row[4].strip(), row[5].strip(), row[6].strip(), row[7].strip())
                item.key = item.id
                required_ID_table.insert(item.key, item)
                item.key = item.address
                my_table.insert(item.key, item)

    except StopIteration:
        pass
    except PermissionError:
        print(f"Permission does not exist to open \"{filename}\"")
    """except Exception as e:
        print(f"An error occurred parsing \"{filename}\":\n{e}")"""
    
    return (required_ID_table, my_table)


def parse_distance_data(filename):
    nodes = HashTable()

    if not file_exists(filename):
        print(f"File: \"{filename}\" does not exist in the current working directory: {os.getcwd()}")
    
    try:
        with open(filename, 'r') as data:
            reader = csv.reader(data)
            # there are column labels which we will skip
            next(reader)
            # because we are creating a HashTable that includes the two-way distances between all addresses,
            # we will basically have all cells in memory when it's constructed, so it won't be significantly worse to load the whole table at once for parsing
            rows = list(reader)
            for row_index in range(len(rows)):
                from_node = HashTable()
                row = rows[row_index]
                # the row labels have the address and the zip code
                split_row = row[0].strip().split("\n")
                street_address = simplify_address(split_row[0])

                # it may be necessary later to hash based on address + zip code for uniqueness
                zip_code_label = None
                if len(split_row) == 2:
                    zip_code_label = split_row[1]
                
                from_node_name = street_address
                from_node.before_hash = from_node_name
                from_node.key = from_node.before_hash
                from_node.self_hash = custom_hash(from_node_name)

                # start from 1 to exclude the row label
                # also, because (aside from the label) the Nth row has N cells filled from left to right, we can skip empty cells easily by referencing the row index 
                for column_index in range(1, row_index + 2):
                    # TODO: fix insertion of distances
                    distance = row[column_index]
                    if distance == None or distance == "":
                        break
                    
                    # the row labels have the address and the zip code
                    split_row_2 = rows[column_index - 1][0].strip().split("\n")
                    street_address_2 = simplify_address(split_row_2[0])

                    # it may be necessary later to hash based on address + zip code for uniqueness
                    zip_code_label_2 = None
                    if len(split_row_2) == 2:
                        zip_code_label_2 = split_row[1]
                    to_node_name = street_address_2

                    from_node.insert(to_node_name, DistanceNode(to_node_name, float(distance)))
                    # when populating the other side of the relationship between nodes, we can skip self-relationships
                    if from_node_name != to_node_name:
                        # furthermore, row N only ever contains cells for columns <= N, so we don't need to check if the other node exists to insert
                        holder = nodes.lookup(to_node_name)
                        holder.insert(from_node_name, DistanceNode(from_node_name, float(distance)))
                    
                nodes.insert(street_address, from_node)

    except StopIteration:
        pass
    except PermissionError:
        print(f"Permission does not exist to open \"{filename}\"")

    return nodes


"""A.  Develop a hash table, without using any additional libraries or classes, that has an insertion function that takes the package ID as input and inserts each of the following data components into the hash table:
•   delivery address
•   delivery deadline
•   delivery city
•   delivery zip code
•   package weight
•   delivery status (i.e., at the hub, en route, or delivered), including the delivery time

B.  Develop a look-up function that takes the package ID as input and returns each of the following corresponding data components:
•   delivery address
•   delivery deadline
•   delivery city
•   delivery zip code
•   package weight
•   delivery status (i.e., at the hub, en route, or delivered), including the delivery time

C.  Write an original program that will deliver all packages and meet all requirements using the attached supporting documents “Salt Lake City Downtown Map,” “WGUPS Distance Table,” and “WGUPS Package File.”
1.  Create an identifying comment within the first line of a file named “main.py” that includes your student ID.
2.  Include comments in your code to explain both the process and the flow of the program.

D.  Provide an intuitive interface for the user to view the delivery status (including the delivery time) of any package at any time and the total mileage traveled by all trucks. (The delivery status should report the package as at the hub, en route, or delivered. Delivery status must include the time.)
1.  Provide screenshots to show the status of all packages loaded onto each truck at a time between 8:35 a.m. and 9:25 a.m.
2.  Provide screenshots to show the status of all packages loaded onto each truck at a time between 9:35 a.m. and 10:25 a.m.
3.  Provide screenshots to show the status of all packages loaded onto each truck at a time between 12:03 p.m. and 1:12 p.m.

E.  Provide screenshots showing successful completion of the code that includes the total mileage traveled by all trucks.

F.  Justify the package delivery algorithm used in the solution as written in the original program by doing the following:
1.  Describe two or more strengths of the algorithm used in the solution.
2.  Verify that the algorithm used in the solution meets all requirements in the scenario.
3.  Identify two other named algorithms that are different from the algorithm implemented in the solution and would meet all requirements in the scenario.
a.  Describe how both algorithms identified in part F3 are different from the algorithm used in the solution.

G.  Describe what you would do differently, other than the two algorithms identified in part F3, if you did this project again, including details of the modifications that would be made.

H.  Verify that the data structure used in the solution meets all requirements in the scenario.
1.  Identify two other data structures that could meet the same requirements in the scenario.
a.  Describe how each data structure identified in H1 is different from the data structure used in the solution.

ASSUMPTIONS:
•  Each truck can carry a maximum of 16 packages, and the ID number of each package is unique.
•  The trucks travel at an average speed of 18 miles per hour and have an infinite amount of gas with no need to stop.
•  There are no collisions.
•  Three trucks and two drivers are available for deliveries. Each driver stays with the same truck as long as that truck is in service.
•  Drivers leave the hub no earlier than 8:00 a.m., with the truck loaded, and can return to the hub for packages if needed.
•  The delivery and loading times are instantaneous (i.e., no time passes while at a delivery or when moving packages to a truck at the hub). This time is factored into the calculation of the average speed of the trucks.
•  There is up to one special note associated with a package.
•  The delivery address for package #9, Third District Juvenile Court, is wrong and will be corrected at 10:20 a.m. WGUPS is aware that the address is incorrect and will be updated at 10:20 a.m. However, WGUPS does not know the correct address (410 S. State St., Salt Lake City, UT 84111) until 10:20 a.m.
•  The distances provided in the “WGUPS Distance Table” are equal regardless of the direction traveled.
•  The day ends when all 40 packages have been delivered."""


def start():
    driver_count = 2
    truck_count = 3
    drivers = []
    trucks = []

    distance_data = parse_distance_data("WGUPS Distance Table.csv")
    # we create the required hash table with the ID as the key, as well as a hash table with the address being the key, which will make loading trucks with packages easier
    ID_package_table, package_data = parse_package_data("WGUPS Package File.csv")
    
    for item in package_data:
        hub_distances = distance_data.lookup("HUB")
        result = hub_distances.lookup(item.address)
        print(f"distance from HUB to {item.address}: {result.distance}")
    
    for truck_number in range(truck_count):
        trucks.append(Truck(truck_number + 1))

    for driver_number in range(driver_count):
        d = DeliveryDriver(f"driver{driver_number + 1}")
        trucks[driver_number].driver = d
        drivers.append(d)
    
    # it may be easiest to progress 1 minute at a time
    current_time_minutes = 0
    # this could be incremented dynamically whenever a new package was added by an API if that functionality was ever implemented
    total_package_count = sum(1 for item in package_data)
    packages_on_trucks_count = 0

    all_packages_delivered = False

    truck_restricted_packages = HashTable()
    for package in package_data:
        if package.required_truck != None:
            truck_restricted_packages.insert(package.required_truck, package)


    while not all_packages_delivered:
        for truck in trucks:
            # whenever the truck is at the hub we can safely assume that we should attempt to load packages 
            if truck.at_hub and len(truck.packages) < truck.package_capacity:
                # TODO: pick packages that have to go the farthest, grouped by address; then, while the truck still has room, find the closest address that needs packages delivered
                # another approach would be to group packages by address, then try to group groups

                # we prioritise packages restricted to this truck
                while package := truck_restricted_packages.lookup(truck.id) != None and package.can_be_delivered():
                    truck.packages.append(package)
                # then packages that must be delivered together
                for package in truck.packages:
                    if package.can_be_delivered():
                        truck.packages.append(package)
                # and finally packages grouped by address
            
        # can't dispatch trucks until after 8:00 am (8 * 60 = 480 minutes)

        # TODO: progress time somehow and log events that happen at each minute
        # for mail_items we can store the delivery_time using the mark_delivered function
        # for trucks we'll need 
        current_time_minutes += 1

    # update package #9 address at a specific time (maybe an "updates" list that we poll each minute that progresses?)
    # add a user interface for checking package status

    print("done")


if __name__ == "__main__":
    start()
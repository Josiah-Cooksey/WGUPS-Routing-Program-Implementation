# Developed by Josiah Cooksey; WGU Student ID: 011030459
import csv
from enum import Enum
import math
import os
from delivery_driver import DeliveryDriver
from dart_node import DartNode
from delivery_status import DeliveryStatus
from hash_table import HashTable
from mail_item import MailItem
from truck import Truck
from utils import *
from mst_node import MSTNode


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

                    from_node.insert(to_node_name, DartNode(to_node_name, float(distance)))
                    # when populating the other side of the relationship between nodes, we can skip self-relationships
                    if from_node_name != to_node_name:
                        # furthermore, row N only ever contains cells for columns <= N, so we don't need to check if the other node exists to insert
                        holder = nodes.lookup_exact(to_node_name)
                        holder.insert(from_node_name, DartNode(from_node_name, float(distance)))
                    
                nodes.insert(street_address, from_node)

    except StopIteration:
        pass
    except PermissionError:
        print(f"Permission does not exist to open \"{filename}\"")

    return nodes


def generate_MST(truck: Truck, distance_data):
    minimum_spanning_tree = [MSTNode("HUB")]
    # TODO: decrease big-O for generate_MST by sorting distances beforehand using the fastest sorting function 
    # truck.packages.sort(key=lambda: x: )

    # first we need to find out what nodes we need to connect
    for address, _ in truck.packages:
        new_vertex = MSTNode(address)
        if new_vertex not in minimum_spanning_tree:
            smallest_is_to_this_vertex = None
            smallest_distance = math.inf
            new_vertex_distances = distance_data.lookup_exact(new_vertex.label)
            for existing_vertex in minimum_spanning_tree:
                distance = new_vertex_distances.lookup_exact(existing_vertex.label).distance
                if distance < smallest_distance:
                    smallest_distance = distance
                    smallest_is_to_this_vertex = existing_vertex
            
            new_vertex.add_node(smallest_is_to_this_vertex, distance)
            # makes sure that there's an edge connection on each end
            smallest_is_to_this_vertex.add_node(new_vertex, distance)

            
            minimum_spanning_tree.append(new_vertex)
    
    for element in minimum_spanning_tree:
        connections = " ".join(f"{minimum_spanning_tree.index(sub)}" for sub, _ in element.nodes)
        print(f"{minimum_spanning_tree.index(element)} {(element)} maps to: " + connections)
    truck.minimum_spanning_tree = minimum_spanning_tree


# recursively consumes an MST starting from the passed-in-node and returns a path covering each node and returning to the initial node
def generate_route(current_node:MSTNode, prior_node=None):
    path = []

    # first, we add the paths through all sub-nodes except for the prior_node (which would technically be the parent, if one exists)
    for next_node, distance_to_next_node in current_node.nodes:
        # avoids pathing backwards for now
        if prior_node != None and next_node.label == prior_node.label:
            continue
        # for each child node, we need to indicate that we started here
        self_dart = DartNode(current_node.label, distance_to_next_node)
        path.append(self_dart)

        path.extend(generate_route(next_node, current_node))
        current_node.remove_node(next_node)

    # when there's only one edge connected to the current node
    if len(current_node.nodes) == 1:
        # a prior node makes this a dead-end node
        if prior_node != None:
            _, prior_distance = current_node[0]
            d = DartNode(current_node.label, prior_distance)
            current_node.remove_node(prior_node)
            path.append(d)
    # but no other edges connected makes this the start node again
    else:
        # so the distance can be whatever
        path.append(DartNode(current_node.label, 0))
    
    return path


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
    # when trucks can depart hub after
    start_time_minutes = 480
    current_time_minutes = 0
    delivered_packages = 0

    distance_data = parse_distance_data("WGUPS Distance Table.csv")
    # we create the required hash table with the ID as the key, as well as a hash table with the address being the key, which will make loading trucks with packages easier
    ID_package_table, package_data = parse_package_data("WGUPS Package File.csv")
    
    for truck_number in range(truck_count):
        trucks.append(Truck(truck_number + 1))

    for driver_number in range(driver_count):
        d = DeliveryDriver(f"driver{driver_number + 1}")
        trucks[driver_number].driver = d
        drivers.append(d)
    
    # this could be incremented dynamically whenever a new package was added by an API if that functionality was ever implemented
    total_package_count = sum(1 for item in package_data)

    truck_restricted_packages = HashTable()
    for key, package in package_data:
        if package.required_truck != None:
            truck_restricted_packages.insert(package.required_truck, package)
            # TODO: handle the fact that keys are currently mutable
            # because for this project we know that the address will change, if we force immutable keys that won't work unless we remove and reinsert
            # and for that we'd need a lookup function that doesn't just return the first match
            # however, because the city doesn't change, maybe we could group packages by that
            # the downside to that is that it's not scalable for a real-world software solution
            # a third approach would be allowing mutable keys that are fields of the object being inserted, but that would require manual management of rehashing
            # something else that could work is just not adding packages with incorrect addresses to the hash table, but that's somewhat of a cop-out and we'd need to insert it later 
            # when the update event happens, as well as stall ending the program if we have pending updates, AND update the package count 
            
            # this test confirmed that hash_tables reference the same package instances, meaning an edit to a field will propogate(?) across our different hash_tables
            """truck_restricted_packages.insert(package.required_truck, package)
            retrieval_test = truck_restricted_packages.lookup_all(package.required_truck)
            for test in retrieval_test:
                if test.id == package.id:
                    retrieval_test_item = test
                    print(f"before: {retrieval_test_item}")
                    retrieval_test_item.deadline = "test works"
                    reference_test = ID_package_table.lookup_by_id(retrieval_test_item.id)
                    print(f"after: {reference_test}")
                    break"""
            

    
    
    while not delivered_packages == len(ID_package_table):
        """LOAD PACKAGES"""
        for truck in trucks:
            # whenever the truck is at the hub we can safely assume that we should attempt to load packages 
            if truck.done_with_route and len(truck.packages) < truck.package_capacity:
                # TODO: pick packages that have to go the farthest, grouped by address; then, while the truck still has room, find the closest address that needs packages delivered
                # another approach would be to group packages by address, then try to group groups


                # TODO: this currently doesn't take into account that we'd need to confirm that all loaded packages in the end are loaded with all members of their restriction group
                # we prioritise packages restricted to this truck
                _truck_restricted_packages = truck_restricted_packages.lookup_all(truck.id)
                for package in _truck_restricted_packages:
                    if package.can_be_delivered():
                        truck.load(package)
                # then packages that must be delivered together (ASSUMES THAT CO-DELIVERY RESTRICTIONS ARE LISTED ON ALL PACKAGES IN RESTRICTION GROUP)
                codelivery_packages_to_load = []
                codelivery_packages_to_unload = []
                for _, loaded_package in truck.packages:
                    # because some packages that need to be delivered together may not all be ready for delivery
                    # we will first find all of them and load them into a buffer
                    loading_buffer = []
                    all_buffered_packages_can_be_delivered = True
                    if loaded_package.co_delivery_restrictions != None:
                        for other_package in loaded_package.co_delivery_restrictions:
                            if not other_package.can_be_delivered():
                                all_buffered_packages_can_be_delivered = False
                                # if all grouped packages aren't deliverable, then we need to unload the already-loaded package of that group
                                codelivery_packages_to_unload.append((loaded_package.address, loaded_package))
                                break
                            loading_buffer.append(other_package)

                    if all_buffered_packages_can_be_delivered:
                        codelivery_packages_to_load.extend(loading_buffer)

                truck.unload(codelivery_packages_to_unload)
                truck.load(codelivery_packages_to_load)
                # and finally packages grouped by address


                for _, package in truck.packages:
                    package.update_status(DeliveryStatus.ON_TRUCK, current_time_minutes)

        # can't dispatch trucks until 8:00 am (8 * 60 = 480 minutes)
        if current_time_minutes >= start_time_minutes:
            for truck in trucks:
                if len(truck.packages) >= 1:
                    if truck.minimum_spanning_tree == None:
                        generate_MST(truck, distance_data)
                        truck.route = generate_route(truck.minimum_spanning_tree[0])
                        print("->".join(str(x) for x in truck.route))
                    truck.drive_route(current_time_minutes)
                    
                
        # TODO: progress time somehow and log events that happen at each minute
        # for mail_items we can store the delivery_time using the update_status function
        # for trucks we'll need to keep track of what time they reached each node to be able to tally mileage at that point
        """for key, package in package_data:
            # print(package.get_status(current_time_minutes))
            print(package.get_status(current_time_minutes))"""
        delivered_packages = sum(1 for _, p in package_data if p.get_status(current_time_minutes)[1] == DeliveryStatus.DELIVERED)
        if delivered_packages > 0:
            print(f"{delivered_packages} total delivered packages at {minutes_to_time(current_time_minutes)}")
        # it may be easiest to progress 1 minute at a time
        current_time_minutes += 1

    # update package #9 address at a specific time (maybe an "updates" list that we poll each minute that progresses?)
    # add a user interface for checking package status

    print("done")


if __name__ == "__main__":
    start()
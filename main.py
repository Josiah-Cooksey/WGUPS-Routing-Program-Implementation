# Developed by Josiah Cooksey; WGU Student ID: 011030459
import csv
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
from mail_bundle import MailBundle
import msvcrt

class WGUPSPackageRouter():
    def __init__(self):
        self.driver_count = 2
        self.truck_count = 3
        self.drivers = []
        self.all_trucks = []
        self.trucks = []
        # when trucks can depart hub after
        self.start_time_minutes = 480
        self.now = 0
        self.delivered_packages = 0

        self.distance_data = self.parse_distance_data("WGUPS Distance Table.csv")
        # we create the required hash table with the ID as the key, as well as a hash table with the address being the key, which will make loading trucks with packages easier
        self.packages_by_ID, self.packages_by_ZIP = self.parse_package_data("WGUPS Package File.csv")
        
        # this makes sure that if we have a MailItem M, its co_delivery_restrictions include ALL packages that should be with it
        self.populate_codelivery_restrictions()
        # test = len(set([p.zip for _, p in packages_by_ID]))

        for truck_number in range(self.truck_count):
            self.all_trucks.append(Truck(truck_number + 1))

        for driver_number in range(self.driver_count):
            d = DeliveryDriver(f"driver{driver_number + 1}")
            self.all_trucks[driver_number].driver = d
            self.drivers.append(d)
            # all_trucks includes trucks not assigned a driver
            self.trucks.append(self.all_trucks[driver_number])

        self.truck_restricted_packages = HashTable()
        for _, package in self.packages_by_ZIP:
            if package.required_truck != None:
                self.truck_restricted_packages.insert(package.required_truck, package)
                
        # The delivery address for package #9, Third District Juvenile Court, is wrong and will be corrected at 10:20 a.m. 
        # WGUPS is aware that the address is incorrect and will be updated at 10:20 a.m. 
        # However, WGUPS does not know the correct address (410 S. State St., Salt Lake City, UT 84111) until 10:20 a.m.
        self.timed_events = [[620, "update_address", [9, ["410 S State St", "Salt Lake City", "UT", 84111]]]]
        for _, package in self.packages_by_ZIP:
            if package.delayed_until != None:
                self.timed_events.append([package.delayed_until, "delayed_until", package.id])


    # in an ideal world this data would already be in a database that we could query because spreadsheets are unsustainable
    def parse_package_data(self, filename):
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
                    required_ID_table.insert(item.id, item)
                    my_table.insert(item.zip, item)

        except StopIteration:
            pass
        except PermissionError:
            print(f"Permission does not exist to open \"{filename}\"")
        """except Exception as e:
            print(f"An error occurred parsing \"{filename}\":\n{e}")"""
        
        return (required_ID_table, my_table)


    def parse_distance_data(self, filename):
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
                    from_node.label = from_node_name

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


    def generate_MST(self, packages: HashTable):
        minimum_spanning_tree = [MSTNode("HUB")]
        # TODO: decrease big-O for generate_MST by sorting distances beforehand using the fastest sorting function 
        # truck.packages.sort(key=lambda: x: )

        # first we need to find out what nodes we need to connect
        for address, _ in packages:
            new_vertex = MSTNode(address)
            if new_vertex not in minimum_spanning_tree:
                smallest_is_to_this_vertex = None
                smallest_distance = math.inf
                new_vertex_distances = self.distance_data.lookup_exact(new_vertex.label)
                for existing_vertex in minimum_spanning_tree:
                    distance = new_vertex_distances.lookup_exact(existing_vertex.label).distance
                    if distance < smallest_distance:
                        smallest_distance = distance
                        smallest_is_to_this_vertex = existing_vertex
                
                new_vertex.add_node(smallest_is_to_this_vertex, distance)
                # makes sure that there's an edge connection on each end
                smallest_is_to_this_vertex.add_node(new_vertex, distance)

                
                minimum_spanning_tree.append(new_vertex)
        
        """for element in minimum_spanning_tree:
            connections = " ".join(f"{minimum_spanning_tree.index(sub)}" for sub, _ in element.nodes)
            print(f"{minimum_spanning_tree.index(element)} {(element)} maps to: " + connections)"""
        return minimum_spanning_tree


    # recursively consumes an MST starting from the passed-in-node and returns a path covering each node and returning to the initial node
    def generate_MST_route(self, current_node:MSTNode, prior_node=None):
        path = []

        # first, we add the paths through all sub-nodes except for the prior_node (which would technically be the parent, if one exists)
        for next_node, distance_to_next_node in current_node.nodes:
            # avoids pathing backwards for now
            if prior_node != None and next_node.label == prior_node.label:
                continue
            # for each child node, we need to indicate that we started here
            self_dart = DartNode(current_node.label, distance_to_next_node)
            path.append(self_dart)

            path.extend(self.generate_MST_route(next_node, current_node))
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
            # so the distance can be whatever, but for this program it needs to be zero exactly due to how we measure our trucks' mileage
            path.append(DartNode(current_node.label, 0))
        
        return path
    

    def generate_greedy_route(self, packages: HashTable):
        route = []
        visited_addresses = []

        last_node_visited =  DartNode("HUB", 0)
        route.append(last_node_visited)
        remaining_unique_addresses = list(set(address for address, _ in packages))

        # in a loop, we should pick the next address that's the shortest distance away from last_node_visited
            # then set last_node_visited.distance to be the distance between last_node_visited.label and the next_address 
            # assign last_node_visited = DartNode(, 0)
            # route.append(last_node_visited) 
        
        while len(remaining_unique_addresses) >= 1:
            last_node_visited_address_book = self.distance_data.lookup_exact(last_node_visited.label)
            shortest_distance = math.inf
            shortest_address = None
            for next_address in remaining_unique_addresses:
                next_address_distance = last_node_visited_address_book.lookup_exact(next_address).distance
                if next_address_distance < shortest_distance:
                    shortest_distance = next_address_distance
                    shortest_address = next_address
            
            # now that we've found shortest_address in remaining_unique_addresses that's closest to last_node_visited
            # we can remove shortest_address from remaining_unique_addresses
            remaining_unique_addresses.remove(shortest_address)
            # make sure to update the last node to reflect the distance to shortest_address
            last_node_visited.distance = shortest_distance
            # and update last_node_visited
            last_node_visited = DartNode(shortest_address, 0)
            route.append(last_node_visited) 

        # after appending that initial HUB node and all addresses from remaining_unique_addresses
        # we just need to return to the HUB and ensure that the return distance for the 2nd to last node is correct
        final_node = DartNode("HUB", 0)
        route.append(final_node)

        final_node_address_book = self.distance_data.lookup_exact(final_node.label)
        last_node_visited.distance = final_node_address_book.lookup_exact(last_node_visited.label).distance
        return route


    def populate_codelivery_restrictions(self):
        for _, package in self.packages_by_ID:
            if package.co_delivery_restrictions == None:
                continue
            self.recursive_codelivery(package)
        return
    

    def recursive_codelivery(self, package:MailItem):
        if package.id not in package.co_delivery_restrictions:
            package.co_delivery_restrictions.append(package.id)

        for sub_package in package.co_delivery_restrictions:
            other_end = self.packages_by_ID.lookup_by_id(sub_package)
            if other_end.co_delivery_restrictions == None:
                other_end.co_delivery_restrictions = package.co_delivery_restrictions
                self.recursive_codelivery(other_end)
            else:
                for r in package.co_delivery_restrictions:
                    if not (r in other_end.co_delivery_restrictions):
                        other_end.co_delivery_restrictions.append(r)
                        self.recursive_codelivery(other_end)
            
        return

    def start(self):
        while not self.delivered_packages == len(self.packages_by_ID):
            """PROCESS EVENTS"""
            events_to_process_now = [event for event in self.timed_events if self.now >= event[0]]
            for event in events_to_process_now:
                # important to prevent packages from being marked AT_HUB repeatedly even after being delivered
                self.timed_events.remove(event)
                event_time, event_name, event_data = event

                match event_name:
                    case "update_address":
                        package_ID, new_address_data = event_data
                        new_address, new_city, new_state, new_zip = new_address_data
                        package = self.packages_by_ID.lookup_by_id(package_ID)

                        # important to ensure that the package can be found after the key updates
                        self.packages_by_ZIP.remove_by_item(package.zip, package)

                        package.update_status(DeliveryStatus.AT_HUB)
                        package.has_incorrect_address = False
                        package.address = simplify_address(new_address.strip())
                        package.city = new_city
                        package.state = new_state
                        package.zip = new_zip

                        # reinsert after updating address 
                        self.packages_by_ZIP.insert(package.zip, package)

                    case "delayed_until":
                        package = self.packages_by_ID.lookup_by_id(event_data)
                        package.delayed_until = None
                        package.update_status(DeliveryStatus.AT_HUB, event_time)

            """LOAD PACKAGES"""
            for truck in self.trucks:
                # whenever the truck is at the hub we can safely assume that we should attempt to load packages 
                if truck.can_be_loaded(self.now):
                    """BUNDLING"""
                    # TODO: avoid repeating bundling inside truck loop
                    forced_bundles = []
                    zip_bundles = []
                    bundled_package_IDs = []
                    cannot_be_bundled = []
                    bundled_zip_codes = []
                    
                    # bundle packages that must be delivered together
                    for _, original_package in self.packages_by_ID:
                        if not original_package.can_be_delivered():
                            cannot_be_bundled.append(original_package)
                            continue
                        if original_package.co_delivery_restrictions == None:
                            continue

                        if original_package.id not in bundled_package_IDs:
                            bundle = MailBundle()
                            bundled_package_IDs.extend(original_package.co_delivery_restrictions)

                            for package_ID in original_package.co_delivery_restrictions:
                                p = self.packages_by_ID.lookup_by_id(package_ID)
                                if not p.can_be_delivered():
                                    bundle = None
                                    break
                                bundle.append(p)
                                # then mark that bundle as restricted to a specific truck if any of its packages require it
                                if p.required_truck != None:
                                    bundle.required_truck = p.required_truck

                            if bundle != None:
                                forced_bundles.append(bundle)



                    # bundle by zip code
                    for _, package in self.packages_by_ID:
                        if package.zip in bundled_zip_codes or package.id in bundled_package_IDs or not package.can_be_delivered():
                            continue
                        
                        zip_group = self.packages_by_ZIP.lookup_all(package.zip)
                        bundle = MailBundle()
                        bundle.bundled_by = package.zip
                        for zip_package in zip_group:
                            if zip_package.id in bundled_package_IDs or not zip_package.can_be_delivered() or zip_package.co_delivery_restrictions != None:
                                continue
                            
                            bundle.append(zip_package)
                            if zip_package.deadline != "EOD":
                                deadline = time_to_minutes(string_12_to_time(zip_package.deadline))
                                if deadline < bundle.earliest_deadline:
                                    bundle.earliest_deadline = deadline
                            bundled_package_IDs.append(zip_package.id)

                        zip_bundles.append(bundle)
                        bundled_zip_codes.append(bundle.bundled_by)
                    
                    # now because bundles bundled by zip code have a earliest_deadline field
                    # we can sort by that to handle the zip codes with the earliest deadlines instead of just in order that they happened to be bundled
                    zip_bundles.sort(key=lambda x: x.earliest_deadline)
                    
                    
                    """BUNDLE LOADING"""
                    # load packages with the same zip codes as packages already required to be on this truck 
                    for bundle in forced_bundles:
                        if len(truck.packages) + len(bundle) <= truck.package_capacity:
                            truck.load(bundle) 
                            if len(truck.packages) >= truck.package_capacity: 
                                continue
                            
                            for loaded_package in bundle:
                                if len(truck.packages) >= truck.package_capacity:
                                    break

                                for zip_bundle in zip_bundles:
                                    if loaded_package.zip != zip_bundle.bundled_by:
                                        continue
                                    
                                    # we add as many packages with the same zip code from the bundle into the truck
                                    # and it doesn't matter that the bundle now has fewer items because they are not required to be bundled
                                    # it's just to optimise distance
                                    while len(truck.packages) < truck.package_capacity:
                                        # .pop may throw IndexError 
                                        try:
                                            z = zip_bundle.pop()
                                            truck.load(z)

                                        except IndexError:
                                            break
                                    # there is only 1 zip_bundle grouped by the same zip as loaded_package, so we don't need to continue this for-loop
                                    break


                    # repeated code needs to be in a function
                    for zip_bundle in zip_bundles:
                        # we add as many packages with the same zip code from the bundle into the truck
                        # and it doesn't matter that the bundle now has fewer items because they are not required to be bundled
                        # it's just to optimise distance
                        while len(truck.packages) < truck.package_capacity:
                            # .pop may throw IndexError 
                            try:
                                z = zip_bundle.pop()
                                truck.load(z)

                            except IndexError:
                                break

                        if len(truck.packages) >= truck.package_capacity:
                            break

                    for _, package in truck.packages:
                        package.update_status(DeliveryStatus.ON_TRUCK, self.now)
            
                if truck.route == None and len(truck.packages) >= 1:
                    # a minimum spanning tree seems too inefficient at around 470 miles total
                    """MST = self.generate_MST(truck.packages)
                    truck.route = self.generate_MST_route(MST[0])"""
                    # so we'll use a greedy approach, which turned out to be significantly efficient at 151.9 miles total
                    truck.route = self.generate_greedy_route(truck.packages)
                    print("->".join(str(n) for n in truck.route))
                    t_distance = sum(n.distance for n in truck.route)
                    print(f"total distance: {t_distance}; average distance/package: {t_distance/len(truck.packages)}")     

            # can't dispatch trucks until 8:00 am (8 * 60 = 480 minutes)
            if self.now >= self.start_time_minutes:
                for truck in self.trucks:
                    if truck.route != None:
                        truck.drive_route(self.now)
                        
            self.delivered_packages = sum(1 for _, p in self.packages_by_ID if p.get_status(self.now)[1] == DeliveryStatus.DELIVERED)
            if self.delivered_packages > 0:
                total_mileage = sum(t.get_current_mileage(self.now) for t in self.trucks)
                print(f"{minutes_to_time(self.now)}; total mileage: {total_mileage}; delivered packages: {self.delivered_packages}")
            # it seems easiest to progress 1 minute at a time
            self.now += 1

        print("done")
        
        command_input = None
        while command_input != 'e':
            match command_input:
                case 'a':
                     # prompt for time to check status
                    minutes_time_input = self.get_input_time(f"What time would you like to check the status of all packages? Format example: 3:21 PM\n", "Invalid format! Format example: 3:21 PM")
                    traditional_time_input = minutes_to_time(minutes_time_input)
                    print(f"At {traditional_time_input}\nPackage ID, Delivery Address, Delivery Deadline, Delivery Status, Truck Number:")
                    for _, package in self.packages_by_ID:
                        _, delivery_status = package.get_status(minutes_time_input)
                        print(f"{package.id:<4} {package.address:<40} {package.deadline:<8} {delivery_status:<10} {package.shipped_using_truck_id:<4}")
                    
                    print(f"At that time ({traditional_time_input}), total truck mileage was {sum(t.get_current_mileage(minutes_time_input) for t in self.trucks)}")
                case 'i':
                    package_ID = None
                    found_package = None
                    # get package ID
                    while True:
                        package_ID = self.get_string_input("What is the ID of the package that you'd like to check the status of?\n")
                        try:
                            package_ID = int(package_ID)
                            found_package = self.packages_by_ID.lookup_by_id(package_ID)
                            if found_package == None:
                                print(f"A package with ID {package_ID} could not be found.")
                            else:
                                break
                        except:
                            print("Invalid format! Package ID must be an integer.")
                            
                    # prompt for time to check status
                    minutes_time_input = self.get_input_time(f"At what time should package ID #{package_ID}'s status be checked? Format example: 3:21 PM\n", "Invalid format! Format example: 3:21 PM")
                    traditional_time_input = minutes_to_time(minutes_time_input)
                    result_time, result_status = found_package.get_status(minutes_time_input)
                    print(f"At {traditional_time_input}:\nPackage {package_ID} was {result_status} since {result_time}.\nTotal truck mileage was {sum(t.get_current_mileage(minutes_time_input) for t in self.trucks)}.")
                case 'e':
                    break
            
            print("press a to check status of ALL packages\npress i to check individual package status\npress e to exit")
            command_input = msvcrt.getch().decode(errors="ignore")

    def get_string_input(self, prompt_text):
        response = input(prompt_text)
        return response.strip()

    def get_input_time(self, prompt, error_message):
        time_input = None
        while True:
            time_input = self.get_string_input(prompt)
            try:
                time_input = string_12_to_time(time_input)
                minutes_time_input = time_to_minutes(time_input)
                return minutes_time_input
            except:
                print(error_message)



if __name__ == "__main__":
    solution = WGUPSPackageRouter()
    solution.start()
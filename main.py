# Developed by Josiah Cooksey; WGU Student ID: 011030459
import csv
from enum import Enum
import os
import re

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
a.  Describe how each data structure identified in H1 is different from the data structure used in the solution."""
class hash_table():
    def __init__(self, start_size=23, max_load_index=0.5, max_insert_attempts=10, hashing_helper1=2, hashing_helper2=2):
        self.table = [bucket_status.EMPTY for _ in range(start_size)]
        self.max_load_index = max_load_index
        self.max_insert_attempts = max_insert_attempts
        self.hashing_helper1 = hashing_helper1
        self.hashing_helper2 = hashing_helper2

    
    def __str__(self):
        result = "".join("\n" + str(item) for item in self.table)
        return result
    

    def insert(self, item_hash, some_obj):
        insertion_attempt_count = 0

        self.resize_table()

        while True:
            if insertion_attempt_count > self.max_insert_attempts:
                self.resize_table(True)
                # to avoid resizing the table many times in a row, we reset the attempt count
                insertion_attempt_count = 0

            probe_index = self.calculate_probe_index(item_hash, insertion_attempt_count)
            existing_item = self.table[probe_index]
            # as long as we're not replacing an existing item we can insert here
            if isinstance(existing_item, bucket_status):
                self.table[probe_index] = some_obj
                return
            
            insertion_attempt_count += 1
    

    def calculate_probe_index(self, item_hash, attempt_count):
        return (item_hash + (self.hashing_helper1 * attempt_count) + (self.hashing_helper2 * pow(attempt_count, 2))) % len(self.table)


    # only exists for rubric requirement
    # don't use if your key wasn't the id
    def lookup_by_id(self, item_id: int):
        attempt_count = 0
        item_hash = item_id
        while True:
            probe_index = self.calculate_probe_index(item_hash, attempt_count)
            item = self.table[probe_index]
            # it's guaranteed to either be a mail_item or a bucket_status
            # so we either find it
            if isinstance(item, mail_item):
                return item
            # continue searching
            elif item == bucket_status.DELETED:
                attempt_count += 1
            # or determine that it doesn't exist
            else:
                return None
    
    
    def lookup(self, item_hash: int):
        attempt_count = 0
        while True:
            probe_index = self.calculate_probe_index(item_hash, attempt_count)
            item = self.table[probe_index]
            # it's guaranteed to either be a mail_item or a bucket_status
            # so we either find it
            if isinstance(item, mail_item):
                return item
            # continue searching
            elif item == bucket_status.DELETED:
                attempt_count += 1
            # or determine that it doesn't exist
            else:
                return None
            

    #  resizes if the load index exceeds max_load_index or if overridden, in order to consolidate logic into a single function
    def resize_table(self, override=False):
        if not override and self.calculate_load_index() < self.max_load_index:
            return
        
        new_size = 2 * len(self.table)
        new_table = [bucket_status.EMPTY for _ in range(new_size)]
        # from what I've read, this Pythonic swap is O(1) because we're reassigning references
        self.table, new_table = new_table, self.table
        # rehashes existing items because otherwise they won't be found in the new table
        for item in new_table:
            if isinstance(item, mail_item):
                self.insert(item.hash, item)
    

    def calculate_load_index(self):
        if len(self.table) == 0:
            return 1
        
        counter = 0
        for item in self.table:
            if not isinstance(item, bucket_status):
                counter += 1
        return counter/len(self.table)


def hash_string(some_string):
    result = 0
    for index, char in enumerate(some_string):
        result += (index + 1) * ord(char)
        
    return result

# because lists in Python can hold different types, our hash table will either have an empty bucket_status or a valid mail_item
class bucket_status(Enum):
    EMPTY = 1
    DELETED = 2
    
    def __repr__(self):
        return f"bucket_status{self.name}"


class mail_item():
    def __init__(self, id=None, address=None, city=None, state=None, zip=None, deadline=None, weightKILO=None, notes=None):
        self.id = int(id)
        self.address = address
        self.city = city
        self.state = state
        self.zip = int(zip)
        self.deadline = deadline
        self.weight = int(weightKILO)
        self.notes = notes
        self.delivery_status = delivery_status.AT_HUB
        self.delivery_time = None
        self.hash = None

        self.required_truck = None
        self.co_delivery_restrictions = None
        self.delayed_until = None
        self.has_incorrect_address = None
        self.parse_notes()

    def __str__(self):
        return f"mail_item({self.id}, {self.address}, {self.city}, {self.state}, {self.zip}, {self.deadline}, {self.weight})"

    def parse_notes(self):
        if self.notes == None:
            return
        
        # Example: "Can only be on truck 2"
        truck_restriction = re.search(r"truck\s(\d)+", self.notes)
        if truck_restriction:
            self.required_truck = int(truck_restriction.group(1))
        
        # Example: "Must be delivered with 15, 19"
        co_delivery_string = self.notes.split("Must be delivered with ")
        if len(co_delivery_string) == 2:
            # TODO: rework one-liner to be more readable
            self.co_delivery_restrictions = [package_ID for package_ID in co_delivery_string[1].split(", ") if package_ID != None and package_ID != ""]
        
        # Example: "Delayed on flight---will not arrive to depot until 9:05 am"
        delay_list = self.notes.split("Delayed on flight---will not arrive to depot until ")
        if len(delay_list) == 2:
            self.delayed_until = delay_list[1]

        if "Wrong address listed" in self.notes:
            self.has_incorrect_address = False
    
    def mark_delivered(self, time):
        self.delivery_time = time
        self.delivery_status = delivery_status.DELIVERED



class delivery_status(Enum):
    # refers to a package not being availabe for delivery at the hub yet
    DELAYED = 1
    # awaiting delivery
    AT_HUB = 2
    # awaiting delivery
    ON_TRUCK = 3
    DELIVERED = 4

def file_exists(filename):
    try:
        with open(filename, 'r') as test:
            pass
        return True
    except FileNotFoundError:
        return False

# in an ideal world this data would already be in a database that we could query
# spreadsheets are unsustainable
def parse_package_data(filename):
    required_ID_table = hash_table()
    my_table = hash_table()

    if not file_exists(filename):
        print(f"File: \"{filename}\" does not exist in the current working directory: {os.getcwd()}")
    
    try:
        with open(filename, 'r') as data:
            reader = csv.reader(data)
            column_titles = next(reader)
            
            while(True):
                # Package ID	Address	City 	State	Zip	Delivery Deadline	Weight KILO	page 1 of 1PageSpecial Notes 
                row = next(reader)
                item = mail_item(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
                item.hash = item.id
                required_ID_table.insert(item.hash, item)
                item.hash = hash_string(item.address)
                my_table.insert(item.hash, item)
                print(f"table after insert: {my_table}\n")

    except StopIteration:
        pass
    except PermissionError:
        print(f"Permission does not exist to open \"{filename}\"")
    """except Exception as e:
        print(f"An error occurred parsing \"{filename}\":\n{e}")"""
    
    return (required_ID_table, my_table)

def parse_distance_data(filename):
    nodes = hash_table()

    if not file_exists(filename):
        print(f"File: \"{filename}\" does not exist in the current working directory: {os.getcwd()}")
    
    try:
        with open(filename, 'r') as data:
            reader = csv.reader(data)
            # there are column labels, so we will skip those
            next(reader)
            # because we are creating a hash_table that includes the two-way distances between all addresses,
            # we will basically have all cells in memory when it's constructed, so it won't be significantly worse to load the whole table at once for parsing
            rows = list(reader)
            # we'll parse in reverse because the row labels and column labels differ despite them referring to the same address
            for row_index in range(len(rows) - 1, -1, -1):
                from_node = hash_table()
                row = rows[row_index]
                row_label = row[0]
                # start from 1 to exclude the row label
                for column_index in range(1, len(row)):
                    distance = row[column_index]
                    if distance == None or distance == "":
                        break

                    to_node_name = rows[column_index][0]

                    from_node.insert(hash_string(to_node_name), float(distance))
                    
                nodes.insert(hash_string(row_label), from_node)
                print(f"nodes after insert: {nodes}\n")

    except StopIteration:
        pass
    except PermissionError:
        print(f"Permission does not exist to open \"{filename}\"")
    
    return nodes


"""•  Each truck can carry a maximum of 16 packages, and the ID number of each package is unique.
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
    # we create the required hash table with the ID as the key, as well as a hash table with the address being the key, which will make loading trucks with packages easier
    ID_package_table, package_data = parse_package_data("WGUPS Package File.csv")
    for item in package_data.table:
        print(item)
    distance_data = parse_distance_data("WGUPS Distance Table.csv")


    # TODO: progress time somehow
    # update package #9 address at a specific time (maybe an "updates" list that we poll each minute that progresses?)
    # add a user interface for checking package status

    print("done")

if __name__ == "__main__":
    start()
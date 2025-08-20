# Developed by Josiah Cooksey; WGU Student ID: 011030459
import csv
from enum import Enum
import os

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
    def __init__(self, start_size=23, max_load_index=0.5, max_insert_attempts=10, hashing_helper1=1, hashing_helper2=1):
        self.table = [bucket_status.EMPTY for _ in range(start_size)]
        self.max_load_index = max_load_index
        self.max_insert_attempts = max_insert_attempts
        self.hashing_helper1 = hashing_helper1
        self.hashing_helper2 = hashing_helper2
    

    def insert(self, some_obj):
        insertion_attempt_count = 0
        hash_value = self.hash(some_obj)
        insertion_index = None

        self.resize_table()

        while True:
            if insertion_attempt_count > self.max_insert_attempts:
                self.resize_table(True)

            insertion_index = (hash_value(insertion_attempt_count) + (self.hashing_helper1 * insertion_attempt_count) + (self.hashing_helper1 * pow(insertion_attempt_count, 2))) % len(self.table)


    #  resizes if the load index exceeds max_load_index or if overridden, in order to consolidate logic into a single function
    def resize_table(self, override=False):
        if not override or self.calculate_load_index() < self.max_load_index:
            return
        
        new_size = 2 * len(self.table)
        new_table = [bucket_status.EMPTY for _ in range(new_size)]
        # from what I've read, this Pythonic swap is O(1) because we're reassigning references
        self.table, new_table = new_table, self.table
        # rehashes existing items because otherwise they won't be found in the new table
        for item in self.table:
            if isinstance(item, mail_item):
                self.insert(item)
    

    def calculate_load_index(self):
        if len(self.table == 0):
            return 1
        
        counter = 0
        for item in self.table:
            if not isinstance(item, bucket_status):
                counter += 1
        return counter/len(self.table)


    def hash(self, some_obj):
        try:
            value = some_obj.id
            return value
        except:
            return -1

# because lists in Python can hold different types, our hash table will either have an empty bucket_status or a valid mail_item
class bucket_status(Enum):
    EMPTY = 1
    DELETED = 1


class mail_item():
    def __init__(self, id=None, address=None, city=None, state=None, zip=None, deadline=None, weightKILO=None, notes=None):
        self.id = id
        self.address = address
        self.city = city
        self.state = state
        self.zip = zip
        self.deadline = deadline
        self.weight = weightKILO
        self.notes = notes
        self.delivery_status = delivery_status.AT_HUB
        self.required_truck = None
        self.delivery_restrictions = None
        self.parse_notes()


    def parse_notes(self):
        if self.notes != None:
            return


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
    table = hash_table()

    if not file_exists(filename):
        print(f"File: \"{filename}\" does not exist in the current working directory: {os.getcwd()}")
    
    try:
        with open(filename, 'r') as data:
            reader = csv.reader(data)
            column_titles = next(reader)
            
            while(True):
                # Package ID	Address	City 	State	Zip	Delivery Deadline	Weight KILO	page 1 of 1PageSpecial Notes 
                row = next(reader)
                table.insert(mail_item(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))


    except StopIteration:
        pass
    except PermissionError:
        print(f"Permission does not exist to open \"{filename}\"")
    except:
        print(f"An error occurred parsing \"{filename}\"")
    
    return table

def parse_distance_data():
    return None

def start():
    package_data = parse_package_data("WGUPS Package File.xlsx")
    distance_data = parse_distance_data("WGUPS Distance Table.xlsx")

if __name__ == "__main_":
    start()
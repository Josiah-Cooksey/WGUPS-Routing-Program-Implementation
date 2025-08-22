import re
from delivery_status import DeliveryStatus

class MailItem():
    def __init__(self, id=None, address=None, city=None, state=None, zip=None, deadline=None, weightKILO=None, notes=None):
        self.id = int(id)
        self.address = address
        self.city = city
        self.state = state
        self.zip = int(zip)
        self.deadline = deadline
        self.weight = int(weightKILO)
        self.notes = notes
        self.DeliveryStatus = DeliveryStatus.AT_HUB
        self.delivery_time = None
        self.key = None
        self.hash = None

        self.required_truck = None
        self.co_delivery_restrictions = None
        self.delayed_until = None
        self.has_incorrect_address = None
        self.parse_notes()

    def __str__(self):
        return f"MailItem({self.id}, {self.address}, {self.city}, {self.state}, {self.zip}, {self.deadline}, {self.weight})"

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
        self.DeliveryStatus = DeliveryStatus.DELIVERED
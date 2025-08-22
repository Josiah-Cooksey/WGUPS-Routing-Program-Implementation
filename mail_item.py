import re
from delivery_status import DeliveryStatus
from utils import *

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
        self.delivery_status = None
        self.delivery_time = None
        self.key = None
        self.hash = None
        self.status_log = []

        self.required_truck = None
        self.co_delivery_restrictions = None
        self.delayed_until = None
        self.has_incorrect_address = None
        self.parse_notes()

        if self.delivery_status == None:
            self.update_status(DeliveryStatus.AT_HUB)

    def __str__(self):
        return f"MailItem({self.id}, {self.address}, {self.city}, {self.state}, {self.zip}, {self.deadline}, {self.weight})"
    
    def __repr__(self):
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
            self.update_status(DeliveryStatus.DELAYED)

        if "Wrong address listed" in self.notes:
            self.has_incorrect_address = False
            self.update_status(DeliveryStatus.DELAYED)
    
    def update_status(self, status:DeliveryStatus, time: int=0):
        self.status_log.append([time, status])
        self.delivery_status = status
        match status:
            case DeliveryStatus.DELAYED:
                pass
            case DeliveryStatus.AT_HUB:
                pass
            case DeliveryStatus.ON_TRUCK:
                pass
            case DeliveryStatus.DELIVERED:
                self.delivery_time = time
    
    def get_status(self, time):
        prior_entry = prior_entry_status = prior_entry_time = entry = entry_status = entry_time = None
        for entry in self.status_log:
            entry_time, entry_status = entry
            if entry_time > time:
                prior_entry_time, prior_entry_status = prior_entry
                return f"{prior_entry_status}: {prior_entry_time}"

            prior_entry = entry
            
        return f"{entry_status}: {entry_time}"
    
    def can_be_delivered(self):
        return not self.delayed_until and not self.has_incorrect_address and self.delivery_status == DeliveryStatus.AT_HUB
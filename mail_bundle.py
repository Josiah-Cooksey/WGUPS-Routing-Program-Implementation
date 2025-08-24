from typing import Set

# used to group packages that MUST be delivered together
class MailBundle():
    def __init__(self):
        self.required_package_IDs = Set()
        self.packages = []
        self.truck_restriction = None
    
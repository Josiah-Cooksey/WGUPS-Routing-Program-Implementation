import math

# used to group packages together
class MailBundle():
    def __init__(self):
        self.packages = []
        self.required_truck = None
        self.bundled_by = None
        self.earliest_deadline = math.inf

    def __iter__(self):
        return (p for p in self.packages)

    def __len__(self):
        return len(self.packages)
    
    def append(self, package):
        self.packages.append(package)
    
    def pop(self):
        return self.packages.pop(-1)
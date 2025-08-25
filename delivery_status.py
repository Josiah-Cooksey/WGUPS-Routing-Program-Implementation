from enum import Enum

class DeliveryStatus(Enum):
    # refers to a package not being available for delivery at the hub yet
    DELAYED = "Delayed"
    # awaiting delivery
    AT_HUB = "At Hub"
    # awaiting delivery
    ON_TRUCK = "En Route"
    DELIVERED = "Delivered"

    def __str__(self):
        return self.value
    def __repr__(self):
        return self.value

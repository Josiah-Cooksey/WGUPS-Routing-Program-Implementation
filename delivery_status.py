from enum import Enum

class DeliveryStatus(Enum):
    # refers to a package not being available for delivery at the hub yet
    DELAYED = 1
    # awaiting delivery
    AT_HUB = 2
    # awaiting delivery
    ON_TRUCK = 3
    DELIVERED = 4
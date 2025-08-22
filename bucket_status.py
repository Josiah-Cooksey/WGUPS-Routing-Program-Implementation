from enum import Enum

# because lists in Python can hold different types, our hash table will either have an empty BucketStatus or a valid item
class BucketStatus(Enum):
    EMPTY = 1
    DELETED = 2
    
    def __repr__(self):
        return f"BucketStatus.{self.name}"
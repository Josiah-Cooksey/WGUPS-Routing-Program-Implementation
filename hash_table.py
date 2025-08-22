from bucket_status import BucketStatus
from utils import custom_hash

class HashTable():
    def __init__(self, start_size=2, max_load_index=0.5, max_insert_attempts=10, hashing_helper1=2, hashing_helper2=2):
        self.table = [BucketStatus.EMPTY for _ in range(start_size)]
        self.table_size = start_size
        self.max_load_index = max_load_index
        self.max_insert_attempts = max_insert_attempts
        self.hashing_helper1 = hashing_helper1
        self.hashing_helper2 = hashing_helper2
        # the self hash helps with nested hash tables and populating both sides of a relationship
        self.before_hash = None
        self.self_hash = None
        self.key = self.before_hash

    
    def __str__(self):
        result = "".join("\n" + str(item) for item in self.table)
        return result
    
    # this isn't a proper representation but it helps with debugging
    def __repr__(self):
        output = ""
        if self.before_hash == None:
            output = "no before_hash"
        return self.before_hash
        output += "\n".join(item.before_hash for item in self.table if not isinstance(item, BucketStatus)) 
        return output
    

    def insert(self, key, some_obj):
        key_hash = custom_hash(key)
        some_obj.self_hash = key_hash
        insertion_attempt_count = 0

        while True:
            if insertion_attempt_count > self.max_insert_attempts:
                self.resize_table(True)
                # to avoid resizing the table many times in a row, we reset the attempt count
                insertion_attempt_count = 0

            probe_index = self.calculate_probe_index(key_hash, insertion_attempt_count)
            existing_item = self.table[probe_index]
            # as long as we're not replacing an existing item we can insert here
            if isinstance(existing_item, BucketStatus):
                self.table[probe_index] = some_obj
                return
            
            insertion_attempt_count += 1
    

    def calculate_probe_index(self, item_hash, attempt_count):
        return (item_hash + (self.hashing_helper1 * attempt_count) + (self.hashing_helper2 * pow(attempt_count, 2))) % self.table_size


    # only exists for rubric requirement
    # don't use if your key wasn't the id
    def lookup_by_id(self, item_id: int):
        attempt_count = 0
        item_hash = custom_hash(item_id)
        while True:
            probe_index = self.calculate_probe_index(item_hash, attempt_count)
            item = self.table[probe_index]
            # it's guaranteed to either be a MailItem or a BucketStatus
            # so we either find it
            if not isinstance(item, BucketStatus):
                return item
            # continue searching
            elif item == BucketStatus.DELETED:
                attempt_count += 1
            # or determine that it doesn't exist
            else:
                return None
    
    
    def lookup(self, key):
        key_hash = custom_hash(key)
        attempt_count = 0
        while True:
            probe_index = self.calculate_probe_index(key_hash, attempt_count)
            item = self.table[probe_index]
            # it's guaranteed to either be a MailItem or a BucketStatus
            # so we either find it
            if not isinstance(item, BucketStatus):
                return item
            # continue searching
            elif item == BucketStatus.DELETED:
                attempt_count += 1
            # or determine that it doesn't exist
            else:
                return None
            

    #  resizes if the load index exceeds max_load_index or if overridden, in order to consolidate logic into a single function
    def resize_table(self, override=False):
        if not override and self.calculate_load_index() < self.max_load_index:
            return
        
        new_size = 2 * self.table_size
        self.table_size = new_size
        new_table = [BucketStatus.EMPTY for _ in range(new_size)]
        # from what I've read, this Pythonic swap is O(1) because we're reassigning references
        self.table, new_table = new_table, self.table
        # reinserts existing items at newly-determined index because otherwise they won't be found in the new table
        for item in new_table:
            if not isinstance(item, BucketStatus):
                self.insert(item.key, item)
    

    def calculate_load_index(self):
        if self.table_size == 0:
            return 1
        
        counter = 0
        for item in self.table:
            if not isinstance(item, BucketStatus):
                counter += 1
        return counter/self.table_size
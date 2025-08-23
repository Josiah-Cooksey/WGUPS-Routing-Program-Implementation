from bucket_status import BucketStatus
from utils import custom_hash

class HashTable():
    def __init__(self, start_size=2, max_load_index=0.5, max_insert_attempts=10, hashing_helper1=2, hashing_helper2=2):
        self._table = [BucketStatus.EMPTY for _ in range(start_size)]
        self._table_size = start_size
        self.max_load_index = max_load_index
        self.max_insert_attempts = max_insert_attempts
        self.hashing_helper1 = hashing_helper1
        self.hashing_helper2 = hashing_helper2
        # the self hash helps with nested hash tables and populating both sides of a relationship
        self.before_hash = None
        self.self_hash = None
        self.key = self.before_hash
        self._length = 0

    # returns key, value pairs
    def __iter__(self):
        return (item for item in self._table if len(item) == 2)
    
    def __len__(self):
        return self._length
    
    def __str__(self):
        result = "".join("\n" + str(item) for item in self._table if len(item) == 2)
        return result
    
    # this isn't a proper representation but it helps with debugging
    def __repr__(self):
        output = ""
        if self.before_hash == None:
            output = "no before_hash"
        return self.before_hash
        output += "\n".join(item.before_hash for item in self._table if not isinstance(item, BucketStatus)) 
        return output
    

    def remove_by_key(self, key):
        attempt_count = 0
        key_hash = custom_hash(key)
        while True:
            probe_index = self.calculate_probe_index(key_hash, attempt_count)
            item = self._table[probe_index]
            
            # we either find it
            if len(item) == 2:
                found_key, found_value = item
                # needs to find an exact match
                if found_key == key:
                    self._table[probe_index] = BucketStatus.DELETED
                    self._length -= 1
                    return True
            # continue searching
            elif item == BucketStatus.DELETED:
                pass
            # or determine that it doesn't exist
            else:
                return False
            
            attempt_count += 1
    
    def remove_by_item(self, search_key, search_item):
        attempt_count = 0
        key_hash = custom_hash(search_key)
        while True:
            probe_index = self.calculate_probe_index(key_hash, attempt_count)
            item = self._table[probe_index]
            
            # we either find it
            if len(item) == 2:
                found_key, found_value = item
                # needs to find an exact match
                if found_key == search_key and search_item == found_value:
                    self._table[probe_index] = BucketStatus.DELETED
                    self._length -= 1
                    return True
            # continue searching
            elif item == BucketStatus.DELETED:
                pass
            # or determine that it doesn't exist
            else:
                return False
            
            attempt_count += 1




    def insert(self, key, some_obj):
        key_hash = custom_hash(key)
        try:
            some_obj.self_hash = key_hash
        except:
            pass
        insertion_attempt_count = 0

        while True:
            if insertion_attempt_count > self.max_insert_attempts:
                self.resize_table(True)
                # to avoid resizing the table many times in a row, we reset the attempt count
                insertion_attempt_count = 0

            probe_index = self.calculate_probe_index(key_hash, insertion_attempt_count)
            existing_item = self._table[probe_index]
            # as long as we're not replacing an existing item we can insert here
            if isinstance(existing_item, BucketStatus):
                self._table[probe_index] = (key, some_obj)
                self._length += 1
                return
            
            insertion_attempt_count += 1
    

    def calculate_probe_index(self, item_hash, attempt_count):
        return (item_hash + (self.hashing_helper1 * attempt_count) + (self.hashing_helper2 * pow(attempt_count, 2))) % self._table_size


    # only exists for rubric requirement
    # don't use if your key wasn't the id
    def lookup_by_id(self, item_id: int):
        attempt_count = 0
        item_hash = custom_hash(item_id)
        while True:
            probe_index = self.calculate_probe_index(item_hash, attempt_count)
            item = self._table[probe_index]
            
            # we either find it
            if len(item) == 2:
                found_key, found_value = item
                # needs to return only an exact match
                if found_key == item_id:
                    return found_value
            # continue searching
            elif item == BucketStatus.DELETED:
                pass
            # or determine that it doesn't exist
            else:
                return None
            
            attempt_count += 1
    
    # TODO: make address lookups case-insensitive (probably by uncapitalising all characters of addresses or adjusting the hashing function)
    def lookup_first(self, key):
        key_hash = custom_hash(key)
        attempt_count = 0
        while True:
            probe_index = self.calculate_probe_index(key_hash, attempt_count)
            item = self._table[probe_index]
            
            # we either return the first match
            if len(item) == 2:
                found_key, found_value = item
                return found_value
            # continue searching
            elif item == BucketStatus.DELETED:
                attempt_count += 1
            # or determine that it doesn't exist
            else:
                return None
            
    def lookup_exact(self, key):
        attempt_count = 0
        key_hash = custom_hash(key)
        while True:
            probe_index = self.calculate_probe_index(key_hash, attempt_count)
            item = self._table[probe_index]
            
            # we either find it
            if len(item) == 2:
                found_key, found_value = item
                # needs to return only an exact match
                if found_key == key:
                    return found_value
            # continue searching
            elif item == BucketStatus.DELETED:
                pass
            # or determine that it doesn't exist
            else:
                return None
            
            attempt_count += 1

            
    # this allows us to retrieve all elements that match the key
    def lookup_all(self, key):
        results = []
        probed_indexes = []
        key_hash = custom_hash(key)
        attempt_count = 0
        while True:
            probe_index = self.calculate_probe_index(key_hash, attempt_count)
            item = self._table[probe_index]
            if probe_index in probed_indexes:
                return results
            
            if len(item) == 2:
                found_key, found_value = item
                if found_key == key:
                    results.append(found_value)
            # continue searching
            elif item == BucketStatus.DELETED:
                pass
            # or determine that it doesn't exist
            else:
                return results
            
            attempt_count += 1
            probed_indexes.append(probe_index)
            

    #  resizes if the load index exceeds max_load_index or if overridden, in order to consolidate logic into a single function
    def resize_table(self, override=False):
        if not override and self.calculate_load_index() < self.max_load_index:
            return
        # important to reset this to avoid double-counting items
        self._length = 0

        new_size = 2 * self._table_size
        self._table_size = new_size
        new_table = [BucketStatus.EMPTY for _ in range(new_size)]
        # from what I've read, this Pythonic swap is O(1) because we're reassigning references
        self._table, new_table = new_table, self._table
        # reinserts existing items at newly-determined index because otherwise they won't be found in the new table
        for item in new_table:
            if len(item) == 2:
                key, value = item
                self.insert(key, value)
    

    def calculate_load_index(self):
        if self._table_size == 0:
            return 1
        return self._length/self._table_size
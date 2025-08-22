class DistanceNode():
    def __init__(self, before_hash=None, distance: float=None, key=None):
        self.before_hash = before_hash
        self.distance = distance
        self.self_hash = None
        if key == None:
            self.key = self.before_hash
        else:
            self.key = key

    def __repr__(self):
        return f"{self.distance} miles to {self.before_hash}"
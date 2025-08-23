# can represent a start point and a distance to the next, or and end point and the distance to reach it from your current position
# depends on context
class DartNode():
    def __init__(self, before_hash=None, distance: float=None, key=None):
        self.before_hash = before_hash
        self.distance = distance
        self.self_hash = None
        if key == None:
            self.key = self.before_hash
        else:
            self.key = key

    def __repr__(self):
        return f"node: {self.before_hash}; distance: {self.distance}"

    def __str__(self):
        return self.before_hash
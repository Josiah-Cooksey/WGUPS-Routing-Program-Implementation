# can represent a start point and a distance to the next, or and end point and the distance to reach it from your current position
# depends on context
class DartNode():
    def __init__(self, label=None, distance: float=None):
        self.label = label
        self.distance = distance

    def __repr__(self):
        return f"node: {self.label}; distance: {self.distance}"

    def __str__(self):
        return self.label
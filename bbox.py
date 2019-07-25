from math import acos, cos, sin, radians
from shapely.geometry import Polygon


class BoundingBox(object):

    """
    Distance to include point in current bbox
    """
    def get_merge_distance(self):
        return self.merge_distance if self.radius < self.merge_distance else self.radius

    """
    Normalize trigonometric values
    """
    @staticmethod
    def _normalize_trigonometric_value(value):
        if value > 1:
            return 1
        elif value < -1:
            return -1
        else:
            return value

    """
    Calculates distance from current centroid to lon lat point
    """
    def distance_to(self, lon, lat):
        # Earth radius const
        r = 6373.0

        return acos(self._normalize_trigonometric_value(
                sin(radians(lat)) * sin(radians(self.centroid[1])) +
                cos(radians(lat)) *
                cos(radians(self.centroid[1])) *
                cos(radians(self.centroid[0]) - radians(lon)))
        ) * r

    """
    Calculates distance from current centroid to Node-like object
    :param object: Node-like object
    """
    def distance_to_osm_object(self, object):
        lon = float(object.attribs['lon'])
        lat = float(object.attribs['lat'])
        return self.distance_to(lon, lat)

    """
    Recalculates centroid of current bbox
    """
    def _recalculate_centroid(self):
        # Its a lot faster to recalculate centroid without using shapely
        lon3 = self.W + (self.E - self.W) / 2
        lat3 = self.S + (self.N - self.S) / 2
        self.centroid = [lon3, lat3]
        self.radius = (self.distance_to(self.centroid[0], self.centroid[1]) / 2)

    """
    Extends bounding box with node-like object
    
    :param object: Node-like object
    :return: returns nothing
    """
    def insert_object(self, object):
        if self.W > float(object.attribs['lon']):
            self.W = float(object.attribs['lon'])
        if self.E < float(object.attribs['lon']):
            self.E = float(object.attribs['lon'])

        if self.S > float(object.attribs['lat']):
            self.S = float(object.attribs['lat'])
        if self.N < float(object.attribs['lat']):
            self.N = float(object.attribs['lat'])

        self._recalculate_centroid()

    """
    Merges another bounding box into current
    """
    def merge_into(self, bbox):
        if self.W > bbox.W:
            self.W = bbox.W
        if self.E < bbox.E:
            self.E = bbox.E
        if self.S > bbox.S:
            self.S = bbox.S
        if self.N < bbox.N:
            self.N = bbox.N

        # We dont need any recalculations of centroid at this point, because only shapely poly is used at merge stage
        self.poly = None
        # Second bbox is merged into current - ignore it at next iterations
        bbox.merged = True

    """
    Generates shapely.Polygon from current bounds, if not present
    """
    def get_poly(self):
        if self.poly is None:
            self.poly = Polygon([(self.N, self.E), (self.S, self.E), (self.S, self.W), (self.N, self.W)])
        return self.poly

    """
    Returns True if percentage of area is enough to merge
    """
    def is_suitable_for_merge(self, area):
        if area <= 0:
            return False
        else:
            current_area = self.get_poly().area
            percentage = area / (current_area / 100)
            return percentage >= self.percentage_to_merge

    """
    Constructs bounding box
    
    :param ES: South-East [longitude, latitude] 
    :param WN: North-West [longitude, latitude] 
    """
    def __init__(self, ES, WN, merge_distance, merge_percentage):
        self.N = float(WN[1])
        self.E = float(ES[0])
        self.S = float(ES[1])
        self.W = float(WN[0])
        self._recalculate_centroid()
        self.poly = None
        self.merged = False
        self.merge_distance = merge_distance
        self.percentage_to_merge = merge_percentage

    """
    Check if current Node-like object is in bounding box
    
    :param item: Node-like object
    :return: True - if bbox contains this point
    """
    def __contains__(self, item):
        lon = float(item.attribs['lon'])
        lat = float(item.attribs['lat'])
        return (self.W <= lon <= self.E) and (self.S <= lat <= self.N)

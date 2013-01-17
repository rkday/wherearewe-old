import re
import time
import MySQLdb
import sys
import itertools
from shapely.geometry.polygon import LinearRing,Polygon
from shapely.geometry import Point
from ostn02python.eastings_to_decimal_degrees import postcodes_to_points

constituencies = {}
sconstituencies = {}
home = Point(-0.779346,51.397894)
basetime = time.time()
n = 0
total_old_points = 0
total_new_points = 0

def parse_coords(str_coords):
    coords_iter = str_coords.split(" ")
    result_coords = []
    for pair in coords_iter:
        i, j = pair.split(",")
        result_coords.append((float(i), float(j)))
    return result_coords


with open("constituencies.kml") as f:
    for line in f:
        if 'Name' in line:
            mo = re.search(">(.*)<", line)
            name = ' '.join(mo.group(1).split()[:-2])

        elif 'coordinates' in line:
            mo = re.search("coordinates>(.*?)</coo", line)
            coords = parse_coords(mo.group(1))
            inner_coords = None
            if 'innerBoundary' in line:
                mo = re.search("innerBoundary.*coordinates>(.*?)</coo", line)
                inner_coords = [parse_coords(mo.group(1))]
     
            constituencies[name] = Polygon(coords, inner_coords)
            #total_new_points += len(sconstituencies[name].exterior.coords)
            #total_old_points += len(constituencies[name].exterior.coords)
            #print "%d vs. %d" % (total_new_points, total_old_points)
            n+=1
            #print n
            #print time.time() - basetime

colour_cycle = itertools.cycle(["#ff0000", "#00ff00", "#0000ff"])
print "var constituencies = {"
for name in sorted(constituencies.keys()):
    simple_constit = constituencies[name].simplify(0.01)
    print """"{0}": {4}'colour': "{1}",
        'exterior_coordinates': {2},
        'interior_coordinates': {3},
        'text': '{0}'{5},
""".format(name, colour_cycle.next(), [[x, y] for x,y in list(simple_constit.exterior.coords)], [[[x,y] for x,y in list(i.coords)] for i in list(simple_constit.interiors)], '{', '}')
print "}"

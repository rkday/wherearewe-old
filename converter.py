import re
import time
import MySQLdb
import sys
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
            sconstituencies[name] = constituencies[name].simplify(0.001)
            print name
            #total_new_points += len(sconstituencies[name].exterior.coords)
            #total_old_points += len(constituencies[name].exterior.coords)
            #print "%d vs. %d" % (total_new_points, total_old_points)
            n+=1
            #print n
            #print time.time() - basetime


basetime = time.time()

cxn = MySQLdb.connect(user='wherearewe', db='wherearewe')
cursor = cxn.cursor()

with open("all_postcodes_from_ex239QR.csv") as f:
    postcode_constituencies = {}
    unknowns = []
    last_constituency = constituencies.keys()[0]
    n = 0
    wrong_guesses = 0
    for postcode,point in postcodes_to_points(f):
        n += 1
        if constituencies[last_constituency].contains(point):
            postcode_constituencies[postcode] = last_constituency
        else:
            wrong_guesses += 1
            for constituency in constituencies.keys():
                if constituencies[constituency].contains(point):
                    postcode_constituencies[postcode] = constituency
                    last_constituency = constituency
                    break
        if postcode in postcode_constituencies:
            cursor.execute("""INSERT INTO postcodes (postcode, constituency) values(%s, %s)""",
                    (postcode, postcode_constituencies[postcode]))
        else:
            print "%s (%s) is unknown" % (postcode, point)
            unknowns.append((postcode, point))
        if (n % 5000 == 0):
            cxn.commit()
        if (n % 100 == 0):
            print "n: %d, wrong guesses: %d, elapsed time: %f" % (n, wrong_guesses, time.time()-basetime)
            

    cxn.commit()
    print "Could not get constituency data for the following postcodes:"
    print unknowns

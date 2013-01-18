import re
from shapely.geometry.polygon import LinearRing,Polygon
from shapely.geometry import Point


def _parse_coords(str_coords):
    coords_iter = str_coords.split(" ")
    result_coords = []
    for pair in coords_iter:
        i, j = pair.split(",")
        result_coords.append((float(i), float(j)))
    return result_coords

def get_constituency_list(kml_file):
    constituencies = {}
    with open(kml_file) as f:
        for line in f:
            if 'Name' in line:
                mo = re.search(">(.*)<", line)
                name = ' '.join(mo.group(1).split()[:-2]).replace(".", "")

            elif 'coordinates' in line:
                mo = re.search("coordinates>(.*?)</coo", line)
                coords = _parse_coords(mo.group(1))
                inner_coords = None
                if 'innerBoundary' in line:
                    mo = re.search("innerBoundary.*coordinates>(.*?)</coo", line)
                    inner_coords = [_parse_coords(mo.group(1))]
         
                constituencies[name] = Polygon(coords, inner_coords)
    return constituencies

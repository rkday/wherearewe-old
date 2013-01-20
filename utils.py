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

class ColourCoordinator:
    def __init__(min, max, num_steps, start_colour, end_colour):
        self.groups = {}
        step_iter = itertools.count(min, max, (max-min)/float(num_steps))
        r_color_iter = itertools.count(int(start_colour[1:3], 16), 
                int(end_colour[1:3], 16),
                (int(end_colour[1:3], 16)-int(start_colour[1:3], 16)/float(num_steps)))
        g_color_iter = itertools.count(int(start_colour[3:5], 16), 
                int(end_colour[3:5], 16),
                (int(end_colour[3:5], 16)-int(start_colour[3:5], 16)/float(num_steps)))
        b_color_iter = itertools.count(int(start_colour[5:], 16), 
                int(end_colour[5:], 16),
                (int(end_colour[5:], 16)-int(start_colour[5:], 16)/float(num_steps)))

        step = step_iter.next()
        while True:
            step = step_iter.next()
            colour = "#%x%x%x" % (r_color_iter.next(), g_color_iter.next(), b_color_iter.next())
            groups[step] = colour
            break if step == max

    def get_colour_mapping(count):
        for key in sorted(groups.keys()):
            if count <= key:
                return groups[key]

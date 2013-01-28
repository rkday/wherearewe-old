import re
import itertools
from shapely.geometry.polygon import LinearRing, Polygon
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
    for line in kml_file:
        if 'Name' in line:
            mo = re.search(">(.*)<", line)
            name = ' '.join(mo.group(1).split()[:-2]).replace(".", "")

        elif 'coordinates' in line:
            mo = re.search("coordinates>(.*?)</coo", line)
            coords = _parse_coords(mo.group(1))
            inner_coords = None
            if 'innerBoundary' in line:
                mo = re.search("innerBoundary.*coordinates>(.*?)</coo",
                               line)
                inner_coords = [_parse_coords(mo.group(1))]

            constituencies[name] = Polygon(coords, inner_coords)
    return constituencies

class ColourCoordinator:
    def __init__(self, min, max, num_steps, start_colour, end_colour):
        self.groups = {}
        step_iter = itertools.count(min, max, (max - min) / float(num_steps))
        red_colours = self.colour_strings_to_steps(start_colour[1:3],
                                                   end_colour[1:3],
                                                   num_steps)
        green_colours = self.colour_strings_to_steps(start_colour[3:5],
                                                     end_colour[3:5],
                                                     num_steps)
        blue_colours = self.colour_strings_to_steps(start_colour[5:7],
                                                    end_colour[5:7],
                                                    num_steps)

        step = step_iter.next()
        while True:
            step = step_iter.next()
            colour = "#%x%x%x" % (red_colours.next(),
                                  green_colours.next(),
                                  blue_colours.next())
            self.groups[step] = colour
            if step == max:
                break

    def colour_strings_to_steps(self, from_str, to_str, num_steps):

        """Converts two strings representing colours, such as "ff" and "c0", to
        a sequence of numbers representing the steps between them (e.g. 256,
        250...192)"""

        start = int(from_str, 16)
        end = int(to_str, 16)
        distance = end - start
        step_length = distance / float(num_steps)
        return itertools.count(start, end, step_length)

    def get_colour_mapping(self, count):
        for key in sorted(self.groups.keys()):
            if count <= key:
                return self.groups[key]
